""" Emulation for the runtime concept of a namespace.

Namespaces form a tree, starting with RootNamespace, which has a RootScope.
Under that is a GlobalNamespace, which has a GlobalScope.

There are two ways to build the tree up to this point.
1.	Make a RootScope, make a RootNamespace with this scope.
	Call (the RootNamespace).nestGLOB(src, optional name, key, etc.).
		This makes a GlobalScope and returns the new GlobalNamespace.
2.	Make a GlobalScope, which will create a RootScope as a parent.
	Call GlobalNamespace(the GlobalScope, optional key).
	This creates the RootNamespace and adds the GlobalNamespace to
	its modules list.
"""

from __future__ import annotations

import sys
from typing import *
from abc import *

if sys.version_info >= (3, 8):
	from functools import cached_property
else:
	from backports.cached_property import cached_property

import ast

from scope_common import *

import scopes
from scopes import *
from treebuild import SrcT

NsT = TypeVar('NsT', bound='Namespace')
ValT = TypeVar('ValT')
BuildT = Callable[[NsT, scopes.ScopeT, scopes.SrcT, Iterator[scopes.ScopeT]], None]
_noarg: Final = object()				# Use as some argument default values.

#def null_builder(space: NsT, scope: ScopeT, src: SrcT, nested: Iterator[ScopeT]): pass

class Namespace(ScopeTree, Generic[scopes.SrcT, ValT]):
	""" Abstract base class.
	Able to get the value (if any) of, bind, rebind, or unbind identifiers.
	Associated with a Scope object.
	Part of a tree, where every Namespace other than the RootNamespace has a parent.
	A Namespace doesn't necessarily keep track of its children.  The caller has the
	option of making an index of some or all of the children it creates.
	"""

	"""
	Namespaces are related to Scopes, which are regions of a python source.
	A Namespace has an associated Scope object.
	Scopes also form a tree, and the structure of the Namespace tree matches that of
	the Scope tree.  That is,

						RootNamespace        RootScope
							  ^                  ^
							 ...                 ...
	                      Namespace     -->    Scope
							  ^                  ^
							  |  parent          |  parent
						  Namespace     -->    Scope

	Variables and Bindings.

	Every Variable (or "var") is an occurrence of an identifier in the python source.
	It is is found in some particular Scope.
	As the program runs, the Var can be inspected, asigned a value, or deleted.
	When there is no value assigned to it, the Var is "unbound".

	In the scopes.py module, the concept of "binding scope" is discussed.  For any var which
	appears in a "current scope", the binding scope is that Scope or some enclosing Scope.
	The Namespace associated with the binding scope is known as the "binding namespace",
	and this namespace keeps track of the current value, if any, of that Var.

	The Var is always Local in the binding scope.

	A Namespace uses a VarTable object to manage all Vars which are local to its own scope.
	This is found in Namespace.vars.  VarTable is a separate class so that it might be subclassed
	with a different implementation for managing the Vars, as long as VarTable[Var] works the same.

	A VarTable is a mapping from the Var name to a Binding object.
	A Binding is simply a container which is either "bound" or "unbound".
	If it is bound, it has a value (any python object).
	(Note, an unbound Binding is NOT the same as a having value of None).
	The attribute Binding.value can be inspected, set, or deleted.  If it is unbound, then
	get and delete will raise AttributeError.  bool(Binding) is True if bound, False if unbound.
  
	For any Namespace, the Binding for the Var is stored its binding namespace's vars.
	This is a runtime concept, not compile time.

	The procedure for finding the binding namespace for a Var from the current namespace is to go up the
	parent chain until finding the namespace whose scope is the binding scope.  See this diagram:

						binding namespace     -->      binding scope
						       ^                            ^
						       | 0 or more parents          | binder(Var)
						current namespace     -->      current scope

	Assign and delete of a Var by a Namespace is delegated to the Binding for the Var in the
	binding Namespace for the Var.

	The operation of getting the value of a Var works differently, in accordance with Python's
	name resolution rules.  The get may be delegated to the binding Namespace or possibly some
	ancestor Namespace in the parent chain.  It depends on the type of the binding Namespace.

	In a closed namespace (i.e. a function):
		Get the Binding from the VarTable.
		If the Binding is bound, return its value.
		Else the exception will be UnboundLocalError if the current namespace is the binding namespace,
		otherwise it will be NameError.

	In an open namespace (i.e. a class):
		This will always be the current namespace as well, because python's scope resolution
		prevents it from being the binding namespace for something else.
		Get the Binding from the VarTable.
		If the Binding is bound, return the value.
		Otherwise, the operation is delegated to global Namespace.

	In the global namespace (i.e. a module, or delegated from a class):
		Get the Binding from the VarTable.
		If there is no Binding for the Var, this is because there is no binding operation
		for that Var as a global variable anywhere in the entire program.  It is treated as unbound.
		If the Binding is bound, return the value.
		Otherwise, the operation is delegated to the main namespace.

	In the main namespace (i.e. the entire program):
		The VarTable maps all builtin names to their values, taken from the program-wide builtins module.
		An alternate mapping can be provided to the main namespace constructor.
		This mapping is read-only and the values are always bound.
		If there a Binding for the Var, then it returns its value.
		Otherwise, it raises NameError.

	The current namespace sets the value of a Var, or unbinds the Var, by delegating this operation
	to the binding namespace.  It is never further delegated to a different namespace.
	In the binding namespace, the value of the binding for the Var is bound or unbound, respectively.

	Getting the binding namespace can raise a SyntaxError if its scope has no binding scope.
	This would be raised while building the Scopes tree if the Scope was set to cache the binding scopes
	for nonlocal variables.  Without this option, the exception is raised by the Namespace.

	Building a Namespace tree:

	This is a recursive operation, starting from a GlobalNamespace.  It uses a builder function, which
	will be provided by the client in constructing the GlobalNamespace.  The same builder can be used
	for all branches of the tree, but the client may also specify a different builder for a given branch.

	The tree can also be built from the RootNamespace, which will build Namespaces for all of the
	modules in the RootScope.

	Important: The Scopes tree must be entirely built first.

	The build is performed by the Namespace.build() method.
	This calls the builder function to process a namespace.  For convenience, it is also given:
		the scope,
		the reference object contained in the scope, and
		the nested scopes.  These are in the form of an iterator, so that the builder can get
			the nested scopes one at a time without needing a 'for' loop.
			An example would be a builder which traverses a syntax tree for the scope.
			Whenever it visits something which creates a nested scope, it can get the corresponding
			Scope object (assuming that the Scopes tree was built in the same order,
			such as by traversing the same syntax tree).

	The Namespace.nest() method does the recursive build of a nested namespace.  It is given:
		one of the nested scopes (or an iterator from which it gets the next scope),
		an optional key for indexing the new nested namespace in the current namespace, and
		an optional builder to use instead of self.builder.
	The nested namespace is created, and its build() method is called for it immediately.

	"""
	scope: Scope
	parent: Namespace | None
	vars: Mapping[str, Binding[ValT]]
	src: SrcT | None = None

	# Nested namespaces created during build.
	nested: List[Namespace]
	global_ns: GlobalNamespace | None

	def __init__(self, src: SrcT, parent: Namespace = None, name: str = None, *,
					key: object = None, scope: ScopeT = None, **kwds):
		super().__init__(src, parent, name, scope=scope, **kwds)
		if parent:
			assert self.scope.parent is parent.scope
			self.global_ns = parent.global_ns
		else:
			self.global_ns = None

		# Create bindings for local names in the scope.
		self.vars = VarTable()
		self.update_vars()

	def update_vars(self):
		for var in self.scope.vars:
			if var not in self.vars:
				self.vars[var] = Binding()

	@contextmanager
	def build(self) -> Generator[Self]:
		if self.is_built:
			raise ValueError(f'Object {self!r} is already built')
		yield self			# perform building primitives in this context.
		if self.kind in (self.CLASS, self.FUNC):
			if self.name: self.parent.store(self.name, self)
		del self.is_built

	# Methods called by the builder...

	@ScopeTree.mangler
	def load(self, var: str) -> ValT:
		""" Get the current value for the var if any, else raise a NameError.
		Raise SyntaxError if var is unresolved in the scope.
		"""
		binding = self._load_binding(var)
		if binding: return binding.value
		self.raise_unbound(var, self.binder(var))

	def anno(self, var: str, anno, rvalue: ValT = _noarg, **kwds) -> Self:
		pass

	def raise_unbound(self, var: str, binder: Namespace) -> NoReturn:
		if self is binder:
			raise UnboundLocalError(f"local variable '{var}' referenced before assignment")
		else:
			raise NameError(f"name '{var}' is not defined")

	@ScopeTree.mangler
	def has(self, var: str) -> bool:
		""" True if there is a Binding for Var and the Binding is bound. """
		try: self.load(var)
		except NameError: return False
		return True

	@ScopeTree.mangler
	def has_bind(self, var: str) -> bool:
		""" True if there is a Binding for Var and the Binding is bound,
		but only looks in the binding Namespace (i.e., where bind and unbind take place).
		"""
		try: b = self.binder(var)
		except SyntaxError: return False
		if not b: return False
		return bool(b.vars[var])
		
	@ScopeTree.mangler
	def store(self, var: str, value: ValT, **kwds) -> None:
		""" Set the value of the var in the binding namespace.
		Raise SyntaxError if var is unresolved in the scope.
		"""
		self.binder(var).vars.bind(var, value)

	# Same as store()
	store_walrus = store

	@ScopeTree.mangler
	def delete(self, var: str) -> None:
		""" Unbind the var in the binding namespace, if it is now bound.
		Raise NameError if it is not bound.
		Raise SyntaxError if var is unresolved in the scope.
		"""
		if self.has(var):
			self.binder(var).vars.unbind(var)
			return
		self.raise_unbound(var, self.binder(var))

	# Helper methods...

	def binder(self, var: str) -> Namespace | None:
		""" Find the binding namespace for var.
		Return None if there is no binding scope.
		Raise SyntaxError if var is unresolved in the scope.
		"""
		try:
			scope: Scope = self.scope.binder(var)
		except SyntaxError:
			raise
		return self.search_scope(scope)

	def _get_bind(self, var: str) -> Binding | None:
		""" Binding object, if any, in this namespace. """
		return self.vars.get(var)

	@abstractmethod
	def _load_binding(self, var: str) -> Binding | None:
		""" Find the Binding, if any, containing the value of Var.
		self is a binding namespace for Var, but the result might not always
		be the binding stored here.
		The RootNamespace is not a binding namespace, and is handled differently.
		"""
		binding_ns = self.binder(var)
		if binding_ns is self:
			return self._get_bind(var)
		try: return self.binder(var)._load_binding(var)
		except RecursionError:
			print(f'{var} in {self!r}')
			raise
		...

class RootNamespace(Namespace, kind=Scope.ROOT):
	""" The environment for a program and its modules.
	Includes bindings for the builtins module.
	"""
	def __new__(cls, *args):
		return super().__new__(cls, kind=Scope.ROOT)

	def __init__(self, scope: RootScope = None):
		self.scope = scope or RootScope()
		super().__init__(None, None, scope=self.scope)

	def _load_binding(self, var: str) -> Binding | None:
		""" Find the Binding, if any, containing the value of Var.
		self is not a binding namespace.  There might or might not be a Binding for var.
		"""
		return self._get_bind(var)

class GlobalNamespace(Namespace, kind=Scope.GLOB):

	def __init__(self, src: SrcT, parent: RootNamespace = None, name: str = '', *,
			 scope: GlobalScope = None, index: int = None, **kwds):
		if not parent:
			parent = RootNamespace(scope and scope.parent)
			with parent.scope.nestGLOB(src, name=name) as sc:
				pass
			sc.is_built = False
			if not scope: scope = sc
		if index is None: index = len(parent.nested)
		super().__init__(src, parent, name, scope=scope, index=index, **kwds)
		self.global_ns = self

	def store(self, var: str, value: ValT) -> None:
		""" Set the value of the var in the binding namespace.
		Raise SyntaxError if var is unresolved in the scope.
		"""
		binding = self.vars[var]
		if not binding: self.vars[var] = binding = Binding()
		binding.bind(value)

	def _load_binding(self, var: str) -> Binding | None:
		""" Find the Binding, if any, containing the value of Var.
		"""
		binding = self._get_bind(var)
		if binding: return binding				# Binding exists and is bound.
		# Else try the root namespace.
		return self.root._load_binding(var)

class ClassNamespace(Namespace, kind=Scope.CLASS):

	def _load_binding(self, var: str) -> Binding | None:
		""" Find the Binding, if any, containing the value of var.
		"""
		ctx = self.scope.context(var)
		if ctx.hasGLOBDECL:
			return self.glob._load_binding(var)

		binding = self._get_bind(var)
		if binding: return binding
		if ctx.hasLOCAL:
			return self.glob._load_binding(var)
		if ctx.hasGLOBAL:
			return self.glob._load_binding(var)
		if ctx.hasFREE:
			return super()._load_binding(var)

class FunctionNamespace(Namespace, kind=Scope.FUNC):
	pass

class LambdaNamespace(FunctionNamespace, kind=Scope.LAMB):
	pass

class ComprehensionNamespace(FunctionNamespace, kind=Scope.COMP):
	pass

class Binding(Generic[ValT]):
	""" The current value (if any) of a Var in a Namespace.
	"""
	# The value attribute only exists if the Binding is bound.
	value: ValT

	class Unbound: pass
	_unbound: Final = Unbound()					# Sentinel for constructor or bind().

	def __init__(self, value: ValT | Unbound = _unbound):
		if value is not self._unbound:
			self.value = value

	def __bool__ (self) -> bool:
		return hasattr(self, 'value')

	def bind(self, value: ValT | Unbound = _unbound):
		if value is not self._unbound:
			self.value = value
		else:
			self.unbind()

	def unbind(self):
		del self.value

	def __repr__(self) -> str:
		if self:
			return f'= {self.value!r}'
		else:
			return '<unbound>'

class VarTable(dict[str, Binding[ValT]]):
	""" Lookup table for Var names, with missing name resulting in None.
	Behavior can be customized by subclassing (for example, logging all operations).
	"""
	def __getitem__(self, var: str) -> Binding[ValT]:
		return self.get(var)

	def bind(self, var: str, value: ValT) -> None:
		self[var].bind(value)

	def unbind(self, var: str) -> None:
		self[var].unbind()

class GlobalVarTable(VarTable):
	""" Lookup table for Var names, using supplied global dict. """
	def __init__(self, glob: dict[str, ValT]):
		self.glob = glob

	def __getitem__(self, var: str) -> Binding[ValT]:
		try: return Binding(self.glob[var])
		except: return None

	def bind(self, var: str, value: ValT) -> None:
		self.glob[var] = value

	def unbind(self, var: str) -> None:
		del self.glob[var]




""" Expression evaluators.

This is an extension of the idea of resolving a named variable in the Namespace environment.

An Evaluator is an object which will operate on a Namespace and compute the result of an
arbitrary expression in the context of that namespace.

The expression has a type SrcT, and the result of the computation is a ValT.

For speed purposes, the expression object is kept in the Evaluator, and the function which
computes the expression is created only on demand.

"""

class Evaluator(Generic[SrcT, ValT]):
	expr: SrcT

	def __init__(self, expr: SrcT):
		self.expr = expr

	@cached_property
	def caller(self) -> Callable[[Namespace], ValT]:
		return self.make_caller(self.expr)

	@abstractmethod
	def make_caller(self, expr: ast.expr) -> Callable[[Namespace], ValT]:
		...

	def __call__(self, ns: Namespace) -> ValT:
		return self.caller(ns)


class ASTPyObjectEval(Evaluator[ast.AST, object]):
	""" Specialized evaluator for runtime Python objects, taken from an ast.Expression. """

	def make_caller(self, expr: ast.expr) -> Callable[[Namespace], object]:
		# Try evaluating as a literal.
		try: lit = ast.literal_eval(expr)
		except: pass
		else:
			return lambda ns: lit

		# 1. Transform the source tree by replacing name references with calls to the namespace.
		expr = self.Transformer().visit(expr)
		expr = ast.fix_missing_locations(expr)
		# 2. Compile it
		c = compile(ast.Expression(expr), '<expr>', 'eval')
		# 3. Make function which will evaluate it with variable 'ns' as given Namespace.
		def caller(ns: Namespace) -> None:
			locs = dict(ns=ns)
			return eval(c, locs)
		# 4. This is the result.
		return caller

	class Transformer(ast.NodeTransformer):
		""" Visits a source expression and produces one with the name references replaced.
		Calling self.visit(expr) returns the transformed expr tree.
		"""
		def visit_Name(self, node: ast.Name) -> ast.Expr:
			""" Replace with a call to namespace.load({name}). """
			assert type(node.ctx) is ast.Load
			newnode = ast.parse(
				f'ns.load({node.id!r})', mode='eval')
			return newnode.body

		def visit_NamedExpr(self, node: ast.NamedExpr) -> ast.Expr:
			""" Replace with a call to namespace.load({name}). """
			#node = self.generic_visit(node)
			if sys.version_info >= (3, 10):
				rvalue = ast.unparse(self.visit(node.value))
				newnode = ast.parse(
					f'ns.store_walrus({node.target.id!r}, {rvalue})', mode='eval')
				return newnode.body
			else:
				# ast.unparse does not exist, so build the new node the hard way.
				newnode = ast.parse(
					f'ns.store_walrus({node.target.id!r})', mode='eval'
					).body
				newnode.args.append(self.visit(node.value))
				return newnode

		def generic_visit(self, node):
			return super().generic_visit(node)

if __name__ == '__main__':
	expr = ast.parse('(x := y + 2)', mode='eval').body

	e = ASTPyObjectEval(expr)
	x = RootNamespace()
	with x.nestGLOB('foo', 'dummy module', key=42) as y:
		y.store('y', 42)
		y.store('x', None)

	e(y)
	#print(y.load('x'), y.load('y'))

	expr = ast.parse('[1, 2, 3]', mode='eval').body

	#print(ASTPyObjectEval(expr)(y))

	z = GlobalNamespace('bar', None, key=43)

