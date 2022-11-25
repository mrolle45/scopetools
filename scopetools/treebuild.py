""" module treebuild.py.

Creates a tree structure to model a Python module, for purpose of managing variables.
Each node in the tree is a module, class def, function def, lambda, or comprehension.

Source for the module is an ast.Node syntax tree, or a string / file with the Python code.
It's possible to use some other representation through subclassing, such as a mypy.Node tree.

The tree can be composed of Scope objects, Namespace objects, or other types, depending
on which subclass of TreeBuilder is being used.

"""
from __future__ import annotations

from contextlib import contextmanager
import ast
from abc import *
from typing import *
#from .target import *
from .scope_common import *

from .scopes import *
#from assignable import Assignor

"""
There are two parts to the building process, which are separated so that they can be
individually customized.  The two objects are referenced by each other.

1. A Traverser for the source.  This module contains a Traverser using an ast.py abstract
syntax tree (or ast.Node objects).
The Traverser walks through the source program and finds various events which define the
structure of the program.

2. A Builder receives events from the Traverser and translates them into an output tree
structure.  A custom builder may also produce more results than the output tree, such as
code analysis.
The Builder has control over the level of detail of events reported, by recursively calling
the Traverser to report more details.

The events of interest are:

*	Introduce a new tree, nested in the current tree.  Events reported while traversing the
	source will be applied to the nested tree, with certain exceptions.

*	Escape to parent of current tree in body of a context manager.
	All operations while doing so are applied to the parent.  Nesting operations disallowed.

*	A load, assignment or delete of a Target object.
	Provides a token for the assigned value (for an assignment)
	and one or more tokens for the targets (only one for load or delete).
	Traversing each target reports details:

	*	An unpacked target, as in the 'a' in 'a, b = x'.  It will receive one element from
		unpacking the assigned value.  The target can also be a starred target, as in
		'a, *b = x' with only one such allowed in an assignment, and none in a delete.

	*	A named variable, which is defined relative to the current tree.

	*	A named attribute of a given object.

	*	A given subscript of a given container.

*	An assignment expression, as in 'a := x'.  This is similar to the name 'a' appearing
	within an assignment statement, except that in some cases, the semantics of 'a' will
	be different.

*	An annotated assignment, as in 'target: anno' or 'target: anno = rvalue'.
	The target can be a variable, attribute, or subscript.
	The second form is equivalent to 'target: anno' followed by 'target = rvalue'.
	A variable target will be considered local to the current tree, even if there is no assigned value.

*	A global or nonlocal declaration of a variable.

Specialized Builder classes are defined for building trees of Scope and Namespace objects.
Building a Namespace tree requires an existing Scope tree.  By default, a new Scope tree is
built using the Scope Builder and the same Traverser.

"""

SrcT = TypeVar('SrcT')
ValT = TypeVar('ValT')
TravT: TypeAlias = 'Traverser[TreeT, SrcT]'
BldT: TypeAlias = 'Builder[SrcT, TreeT]'

def build() -> TreeT:
	pass

def build_from_scopes() -> TreeT:
	pass

class Traverser(Generic[TreeT, SrcT]):
	""" Walk the source, whatever form that may take, and perform operations on the builder.
	"""
	build: BldT

	def __init__(self):
		pass

	def build(self, build: BldT) -> TreeT:
		self.builder = build
		self.visit(build.curr.src)

	# Builder methods also defined here, for convenience.  They are forwarded to the builder.
	def __getattr__(self, attr: str) -> Any:
		try: return getattr(self.builder, attr)
		except AttributeError: return self.__getattribute__(attr)

	@property
	def curr(self) -> TreeT: return self.builder.curr

	def __repr__(self) -> str:
		return f'Traverse {self.curr.tree_type.__name__}'

class Builder(ScopeTreeProxy, Generic[SrcT, TreeT]):
	""" Creates and builds a Tree starting with a given root.
	"""
	trav: TravT
	curr: TreeT				# The tree currently working on.
	scope_builder_class: ClassVar[Type[Builder] | None ] = None

	def __init__(self, root: TreeT, trav: TravT = None):
		if trav:
			self.trav = trav

		super().__init__(root)

	def build(self) -> None:
		with self.curr.build():
			self.curr.add_nested()
			if hasattr(self, 'trav'): self.trav.build(self)

	def scope_builder(self) -> Builder:
		""" A Builder to build the current scope, called if scope is not yet built. """
		return (self.scope_builder_class or Builder)(self.curr.scope, self.trav)

	@property
	def is_scope(self) -> bool:
		return self.curr.is_scope

class NamespaceBuilder(Builder):
	""" Specialized builder for Namespace trees. """
	def __init__(self, *args, indexed:bool = False, **kwargs):
		super().__init__(*args, **kwargs)
		self.indexed = indexed

	def build(self):
		# Build the root scope if necessary.
		if not self.curr.scope.is_built:
			sc_bldr = self.scope_builder()
			sc_bldr.build()
			self.curr.update_vars()
		self.nested_iter = iter(self.curr.scope.nested)
		self.curr.add_nested()
		self.trav.build(self)

""" Specialized Traverser for tree of ast.Node objects. """

class ASTTraverser(Traverser[ast.AST, TreeT], ast.NodeVisitor):
	def __init__(self, *args, **kwds):
		super().__init__(*args, **kwds)

	def traverse(self, src: ast.AST):
		#super().visit(src)
		self.generic_visit(src)
	def visit(self, src: ast.AST | list[ast.AST]):
		if isinstance(src, list):
			for item in src:
				self.visit(item)
		elif isinstance(src, ast.AST):
			# Don't call base visit() because it will look for self.visit_xxx method.
			# This is OK, but it causes a break in the debugger.
			method = 'visit_' + src.__class__.__name__
			if hasattr(self, method):
				getattr(self, method)(src)
			else:
				self.generic_visit(src)

	# Nested scopes...
	def visit_FunctionDef(self, src: ast.FunctionDef):
		returns = self.anno_str(src.returns)

		with self.nestFUNC(src, src.name, returns=returns, type_comment=src.type_comment):
			for name, node in ast.iter_fields(src):
				if name != 'returns':
					self.visit(node)

	def visit_ClassDef(self, src: ast.ClassDef):
		with self.nestCLASS(src, src.name) as cls:
			self.generic_visit(src)

	def visit_Lambda(self, src: ast.Lambda):
		with self.nestLAMB(src):
			self.generic_visit(src)

	def visit_GeneratorExp(self, src: ast.GeneratorExp):
		self.visit_comp(src, '<genexpr>', src.elt)

	def visit_ListComp(self, src: ast.ListComp):
		self.visit_comp(src, '<listcomp>', src.elt)

	def visit_SetComp(self, src: ast.SetComp):
		self.visit_comp(src, '<setcomp>', src.elt)

	def visit_DictComp(self, src: ast.DictComp):
		self.visit_comp(src, '<listcomp>', src.key, src.value)

	# Simple name binding operations, with name(s) as strings in the ast node...

	def visit_Name(self, src: ast.Nonlocal):
		""" Any Name is either a use or a binding of the id. """
		if isinstance(src.ctx, ast.Load):
			self.use(src.id)
		else:
			# Store and Del are both name binding.
			self.bind(src.id)

	def visit_Nonlocal(self, src: ast.Nonlocal):
		for name in src.names:
			self.decl_nonlocal(name)

	def visit_Global(self, src: ast.Global):
		for name in src.names:
			self.decl_global(name)

	def visit_Import(self, src: ast.Import):
		for alias in src.names:
			name = alias.asname or alias.name.split(".")[0]
			self.store(name, src)

	def visit_ImportFrom(self, src: ast.ImportFrom):
		for alias in src.names:
			name = alias.asname or alias.name
			if name != '*':
				self.store(name, src)

	def visit_ExceptHandler(self, src: ast.ExceptHandler):
		# The order of operations is:
		#	Evaluate the type.
		#	Assign the exception to the name, if present.
		#	Execute the body.
		#	Delete the name, if present.
		# Cannot use generic_visit() because visiting the name, which is not an AST, does nothing.
		self.visit(src.type)
		name = src.name
		if name:
			self.bind(name)
			self.store(name, src.type)
		self.visit(src.body)
		if name:
			self.delete(name)

	# Name binding using an arbitrary Target target...

	def visit_For(self, src: ast.For):
		# The order of operations is:
		#	Make an Target for the target.  This does not affect the external environment.
		#	Evaluate the iter expression.
		#	For each rvalue in the iter:
		#		Assign the rvalue to the target.  This will evaluate any expressions in the target.
		#		Execute the body.
		#	Execute the "else" clause, if present
		target = self.make_target(src.target)
		self.visit(src.iter)
		# Here is where the iter will be unpacked.
		self.store(target, src.iter)
		self.visit(src.body)
		self.visit(src.orelse)

	def visit_withitem(self, src: ast.withitem):
		# The order of operations is:
		#	Evaluate the context_expr.
		#	Call its __enter__() method
		#	Assign the result to the optional_vars, if present.  This is a Target.
		self.visit(src.context_expr)
		target = src.optional_vars
		if target:
			self.store(target, src.context_expr)

	def visit_MatchAs(self, src: ast.MatchAs):
		name = src.name
		if name:
			self.store(name)

	visit_MatchStar = visit_MatchAs

	def visit_Assign(self, src: ast.Assign):
		#for target in src.targets:
		#	self.store(target, src.value)
		self.traverse(src)

	def visit_AnnAssign(self, src: ast.AnnAssign):
		anno = self.anno_str(src.annotation)
		# (var) : anno is a no-op, so don't visit target, which 
		# mistakenly has Store() context.
		if not src.simple and not src.value: return

		# expr : anno [ = value ] does nothing for now.  The anno is ignored,
		# and we don't know how to report 'expr = value' yet.
		if not isinstance(src.target, ast.Name): return

		if src.value:
			self.anno_store(src.target.id, anno, src.value)
		else:
			self.anno(src.target.id, anno)

	def visit_NamedExpr(self, src: ast.NamedExpr):
		with self.use_walrus():
			self.traverse(src)

	def visit_arg(self, src: ast.arg):
		anno = self.anno_str(src.annotation)
		rvalue = self.ArgValue(src.arg)
		comm = src.type_comment
		if comm:
			if anno:
				raise SyntaxError(f'Function parameter {src.arg!r} has both annotation and type comment.')
		if anno:
			self.anno_store(src.arg, anno, rvalue)
		else:
			self.store(src.arg, rvalue, type_comment=anno)

	def visit_Constant(self, src: ast.Constant):
		pass

	# Helpers

	def anno_str(self, anno: ast.AST) -> str | None:
		""" Converts an annotation expression to a str, if it is not already a str.
		None becomes None.
		"""
		if isinstance(anno, ast.Str):
			return anno.s
		elif anno is None:
			return None
		else:
			return ast.unparse(anno)

	def visit_comp(self, src: ast.AST, name: str, *elements: ast.AST) -> None:
		""" Common to all comprehension nodes.
		element(s) is either src.elt or src.key and src.value.
		The element(s) are evaluated, in order, after every iteration of the
		innermost "for" or "if" clause.
		Everything is evaluated in a new COMP scope,
			except the iterable in the first "in" clause.
		"""
		with self.nestCOMP(src, name):
			gen: ast.comprehension
			for i, gen in enumerate(src.generators):
				# gen consists of a target (Target), an iterable, and some "if" expressions.
				# target is assigned from each element of the iterable, not the iterable itself.
				if i:
					self.visit(gen.iter)
				else:
					with self.use_parent(): self.visit(gen.iter)
				self.visit(gen.target)
				#target = ast_make_target(gen.target)
				self.visit_iter(*gen.ifs)
			self.visit_iter(*elements)

	def visit_iter(self, *srcs: ast.AST) -> None:
		for src in srcs:
			self.visit(src)

#class ASTTargetTraverser(target.ASTBuilder):
#	""" Traverses an ast Node for an assignable object, which can be used in assignments,
#	deletes, or evaluations.  Produces an Target object.  """
#	def __call__(self, target: ast.AST) -> Target:
#		pass

#ast_make_target = ASTTargetTraverser()

if __name__ == '__main__':
	# Test building from module code.
	sample = '''if 1:
	x = 2
	class A:
		pass

	try: x
	except NameError as e:
		foo

	'''
	b = Builder(RootScope())
	t = ASTTraverser()
	t.builder = b
	t.visit(ast.parse(sample))

	root_scope = GlobalScope()


	with open('scopestest.py', "rb") as f:
		data = f.read()
		root = ast.parse(data)
	t.traverse(root)

