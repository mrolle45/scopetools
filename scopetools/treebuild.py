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

from scopes import *
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

*	A load, assignment or delete of an Target object.
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

TreeT = TypeVar('TreeT')
SrcT = TypeVar('SrcT')
ValT = TypeVar('ValT')
TravT: TypeAlias = 'Traverser[TreeT, SrcT]'
BldT: TypeAlias = 'Builder[SrcT, TreeT]'
_noarg: Final = object()				# Use as some argument default values.

class Traverser(Generic[TreeT, SrcT]):
	""" Walk the source, whatever form that may take, and perform operations on the builder.
	"""
	build: BldT

	def __init__(self):
		pass

	def build(self, build: BldT, src: SrcT) -> TreeT:
		self.builder = build
		self.visit(src)

	#def visit(self, src: SrcT) -> None:
	#	super().visit(src)
	#	#self.traverse(src)

	# Builder methods also defined here, for convenience.  They are forwarded to the builder.
	def __getattr__(self, attr: str) -> Any:
		try: return getattr(self.builder, attr)
		except AttributeError: return self.__getattribute__(attr)

class Builder(Generic[SrcT, TreeT]):
	""" Creates and builds a Tree starting with a given root.
	"""
	trav: TravT
	curr: TreeT				# The tree currently working on.
	par: TreeT | None		# Parent of curr, if known and with_parent() is allowed.
	assignor: Assignor

	def __init__(self, root: TreeT, trav: TravT = None):
		if trav:
			self.trav = trav

		self.curr = root
		self.par = None
		#self.assignor = Assignor(self)

	def build(self, src: SrcT) -> None:
		with self.curr.build():
			if hasattr(self, 'trav'): self.trav.build(self, src)

	@contextmanager
	def use_parent(self) -> None:
		assert self.par, f'Cannot escape to parent of {self.curr!r}.'
		save, self.curr, self.par = self.curr, self.par, None
		yield
		self.curr, self.par = save, self.curr

	@contextmanager
	def nest(self, kind: ScopeKind, name: str = '', **kwargs) -> Generator:
		""" Create and push context to a nested tree.
		"""
		newtree: TreeT = self._make_nested(kind, name, **kwargs)
		with newtree.build() as n:
			with self.nest_tree(newtree) as n2:
				yield n2

	@contextmanager
	def nest_tree(self, newtree: TreeT) -> Generator:
		""" Push a new tree on the stack.
		Subclass may push additional information.
		"""
		save, self.par, self.curr = self.par, self.curr, newtree
		yield self.curr
		self.par, self.curr = save, self.par

	def nest_Module(self, name: str = '', **kwds) -> GlobalScope:
		return self.nest(self.GLOB, name, **kwds)
	def nest_Function(self, name: str, **kwds) -> FunctionScope:
		return self.nest(self.FUNC, name, **kwds)
	def nest_Class(self, name: str, **kwds) -> ClassScope:
		return self.nest(self.CLASS, name, **kwds)

	@abstractmethod
	def _make_nested(self, kind: ScopeKind, name: str = '', **kwargs) -> TreeT:
		...

	def scope_builder(self) -> ScopeBuilder:
		""" A Builder to build the current scope, called if scope is not yet built. """
		return ScopeBuilder(self.curr.scope, self.trav)

	def __getattr__(self, attr: str) -> Any:
		try: return getattr(self.curr, attr)
		except AttributeError: return self.__getattribute__(attr)

class ScopeBuilder(Builder):
	""" Specialized builder for Scope trees. """

	def build_scope(self) -> Generator:
		""" Context manager.  Caller performs all the tree building operations in the context. """
		return self.curr.build()

	#def build(self) -> Generator:
	#	""" Context manager to build the tree and then resolve names.

	#		with builder.build() [as scope]:
	#			builder yields current scope to caller.

	#			... Build operations for scope and all nested scopes.

	#			builder resolves names in entire scope tree.\
	#	"""
	#	return self.curr.build()

	def _make_nested(self, kind: ScopeKind, name: str = '', **kwargs) -> TreeT:
		""" Create a nested Scope from self.curr. """
		return self.curr.nest(kind, name, **kwargs)

class NamespaceBuilder(Builder):
	""" Specialized builder for Namespace trees. """
	def __init__(self, *args, indexed:bool = False, **kwargs):
		super().__init__(*args, **kwargs)
		self.indexed = indexed

	def build(self, src: SrcT):
		# Build the root scope if necessary.
		if not self.curr.scope.is_built:
			sc_bldr = self.scope_builder()
			sc_bldr.build(src)
			self.curr.update_vars()
		self.nested_iter = iter(self.curr.scope.nested)
		self.trav.build(self, src)

	def has_bind(self, var: str) -> bool:
		return self.curr.has_bind(var)

	#@contextmanager
	#def nest(self, kind: ScopeKind, name: str = '', **kwargs) -> Generator:
	#	""" Moves to new nested Namespace, also saves and restores the current scope's nested scopes. """
	#	save = self.nested_iter
	#	with super().nest(kind, name, **kwargs) as new:
	#		self.nested_iter = iter(self.curr.scope.nested)
	#		yield new
	#	self.nested_iter = save

	@contextmanager
	def nest_tree(self, newtree: TreeT) -> Generator:
		""" Moves to new nested Namespace, also saves and restores the current scope's nested scopes. """
		save = self.nested_iter
		self.nested_iter = iter(newtree.scope.nested)
		with super().nest_tree(newtree):
			yield newtree
		self.nested_iter = save

	def _make_nested(self, kind: ScopeKind, name: str = '', **kwargs) -> TreeT:
		""" Create nested Namespace from self.curr and the next nested Scope of self.curr.scope.
		The kind and name are redundant.
		"""
		scope = next(self.nested_iter)
		assert kind is scope.kind and name == scope.scope_name
		return self.curr.nest(scope, key=name if self.indexed else None, **kwargs)

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

		with self.nest(self.FUNC, src.name, returns=returns, type_comment=src.type_comment):
			for name, node in ast.iter_fields(src):
				if name != 'returns':
					self.visit(node)

	def visit_ClassDef(self, src: ast.ClassDef):
		with self.nest(self.CLASS, src.name):
			self.generic_visit(src)

	def visit_Lambda(self, src: ast.Lambda):
		with self.nest(self.LAMB):
			self.generic_visit(src)

	def visit_GeneratorExp(self, src: ast.GeneratorExp):
		self.visit_comp(src.generators, src.elt)

	visit_ListComp = visit_GeneratorExp
	visit_SetComp = visit_GeneratorExp

	def visit_DictComp(self, src: ast.DictComp):
		self.visit_comp(src.generators, src.key, src.value)

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
			self.nonlocal_stmt(name)

	def visit_Global(self, src: ast.Global):
		for name in src.names:
			self.global_stmt(name)

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
		# Cannot use traverse() because it will visit the type and then the body, and not the name.
		typ = self.visit(src.type)
		name = src.name
		if name:
			self.store(name, typ)
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
		#	Assign the result to the optional_vars, if present.  This is an Target.
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
		if src.value:
			self.anno_assign(src.target.id, anno, src.value)
		else:
			self.anno(src.target.id, anno)

	def visit_NamedExpr(self, src: ast.NamedExpr):
		with self.use_walrus():
			self.traverse(src)

	def visit_arg(self, src: ast.arg):
		anno = self.anno_str(src.annotation)
		rvalue = self.ArgValue(src.arg)
		comm = src.type_comment
		if anno:
			self.anno_assign(src.arg, anno, rvalue, type_comment=comm)
		else:
			self.store(src.arg, rvalue, type_comment=comm)

	def visit_Constant(self, src: ast.Constant):
		pass

	# Helpers

	def anno_str(self, anno: ast.AST) -> str | None:
		""" Converts an annotation expression to a str, if it is not already a Str.
		None becomes None.
		"""
		if isinstance(anno, ast.Str):
			return anno.s
		elif anno is None:
			return None
		else:
			return ast.unparse(anno)


	def visit_comp(self, comp: list[ast.comprehension], *elements: ast.AST) -> None:
		""" Common to all comprehension nodes.
		The element(s) are evaluated, in order, after every iteration of the
		innermost "for" or "if" clause.
		Everything is evaluated in a new COMP scope,
			except the iterable in the first "in" clause.
		"""
		with self.nest(self.COMP):
			gen: ast.comprehension
			for i, gen in enumerate(comp):
				# gen consists of a target (Target), an iterable, and some "if" expressions.
				# target is assigned from each element of the iterable, not the iterable itself.
				if i:
					self.visit(gen.iter)
				else:
					with self.use_parent(): self.visit(gen.iter)
				target = ast_make_target(gen.target)
				self.visit_iter(*gen.ifs)
			self.visit_iter(*elements)
			pass

	def visit_iter(self, *srcs: ast.AST) -> None:
		for src in srcs:
			self.visit(src)

class ASTTargetTraverser(ast.NodeVisitor):
	""" Traverses an ast Node for an assignable object, which can be used in assignments,
	deletes, or evaluations.  Produces an Target object.  """
	def __call__(self, target: ast.AST) -> Target:
		pass

ast_make_target = ASTTargetTraverser()

if __name__ == '__main__':
	# Test building from module code.
	sample = '''
	x = 2
	class A:
		pass

	'''
	#b = Builder(RootNamespace())
	b = ScopeBuilder(RootScope())
	t = ASTTraverser()
	t.visit(ast.parse(sample))

	root_scope = GlobalScope()


	with open('scopestest.py', "rb") as f:
		data = f.read()
		root = ast.parse(data)
	t.traverse(root)

