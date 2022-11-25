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

from .scope_common import *

from . import scopes
from .scopes import *
from .treebuild import SrcT

NsT = TypeVar('NsT', bound='Namespace')
ValT = TypeVar('ValT')
BuildT = Callable[[NsT, scopes.ScopeT, scopes.SrcT, Iterator[scopes.ScopeT]], None]

class Namespace(ScopeTree, Generic[scopes.SrcT, ValT]):
	""" Abstract base class.
	Able to get the value (if any) of, bind, rebind, or unbind identifiers.
	Associated with a Scope object.
	Part of a tree, where every Namespace other than the RootNamespace has a parent.
	A Namespace doesn't necessarily keep track of its children.  The caller has the
	option of making an index of some or all of the children it creates.
	"""

	scope: Scope
	parent: Namespace | None
	vars: Mapping[str, Binding[ValT]]
	src: SrcT | None = None

	# Nested namespaces created during build.
	nested: List[Namespace]

	def __init__(self, src: SrcT, parent: Namespace = None, name: str = None, *,
					key: object = None, scope: ScopeT = None, **kwds):
		super().__init__(src, parent, name, scope=scope, **kwds)
		if parent:
			assert self.scope.parent is parent.scope

		# Create bindings for local names in the scope.
		self.vars = Bindings()
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

	@var_mangle
	def load(self, name: VarName) -> ValT:
		""" Get the current value for the var if any, else raise a NameError.
		Raise SyntaxError if var is unresolved in the scope.
		"""
		binding = self._load_binding(name)
		if binding: return binding.value
		self.raise_unbound(name, self.binder(name))

	@var_mangle
	def anno(self, name: str, anno, **kwds) -> Self:
		pass

	def raise_unbound(self, var: str, binder: Namespace) -> NoReturn:
		if self is binder:
			raise UnboundLocalError(f"local variable '{var}' referenced before assignment")
		else:
			raise NameError(f"name '{var}' is not defined")

	@var_mangle
	def has_bind(self, name: VarName) -> bool:
		""" True if there is a Binding for Var and the Binding is bound,
		but only looks in the binding Namespace (i.e., where bind and unbind take place).
		"""
		try: b = self.binder(name)
		except SyntaxError: return False
		if not b: return False
		return bool(b.vars[name])
		
	def store(self, var: str, value: ValT, **kwds) -> None:
		""" Set the value of the var in the binding ns.
		Raise SyntaxError if var is unresolved in the scope.
		"""
		self.binder(var).vars.bind(var, value)

	# Same as store()
	store_walrus = store

	def delete(self, var: str) -> None:
		""" Unbind the var in the binding ns, if it is now bound.
		Raise NameError if it is not bound.
		Raise SyntaxError if var is unresolved in the scope.
		"""
		vars = self.binder(var).vars
		try: vars.unbind(var)
		except AttrobiteError:
			self.raise_unbound(var, self.binder(var))

	# Helper methods...

	def binder(self, var: str) -> Namespace | None:
		""" Find the binding ns for var.
		Return None if there is no binding scope.
		Raise SyntaxError if var is unresolved in the scope.
		"""
		try:
			scope: Scope = self.scope.binding_scope(var)
		except SyntaxError:
			raise
		if scope: return self.search_scope(scope)
		return None

	def _get_bind(self, var: str) -> Binding | None:
		""" Binding object, if any, in this ns. """
		return self.vars.get(var)

	@abstractmethod
	def _load_binding(self, var: str) -> Binding | None:
		""" Find the Binding, if any, containing the value of Var.
		self is a binding ns for Var, but the result might not always
		be the binding stored here.
		The RootNamespace is not a binding ns, and is handled differently.
		"""
		binding_ns = self.binder(var)
		if binding_ns is self:
			return self._get_bind(var)
		try: return binding_ns._load_binding(var)
		except RecursionError:
			print(f'Recursion error: {var} in {self!r}')
			raise

class RootNamespace(Namespace, kind=ScopeKind.ROOT):
	""" The environment for a program and its modules.
	Includes bindings for the builtins module.
	"""

	def __init__(self, scope: RootScope = None):
		self.scope = scope or RootScope()
		super().__init__(None, None, scope=self.scope)

	## TODO: Get bindings from either the builtins module or some alternate supplied dict.
	def _load_binding(self, var: str) -> Binding | None:
		""" Find the Binding, if any, containing the value of Var.
		self is not a binding ns.  There might or might not be a Binding for var.
		"""
		return self._get_bind(var)

class GlobalNamespace(Namespace, kind=ScopeKind.GLOB):

	def __init__(self, src: SrcT, parent: RootNamespace = None, name: str = '', *,
			 scope: GlobalScope = None, index: int = None, **kwds):
		if not parent:
			parent = RootNamespace(scope and scope.parent)
			with parent.scope.nestGLOB(src, name=name) as sc:
				pass
			sc.start_build()
			if not scope: scope = sc
		#if index is None: index = len(parent.nested)
		super().__init__(src, parent, name, scope=scope, index=index, **kwds)

	def store(self, var: str, value: ValT) -> None:
		""" Set the value of the var in the binding ns.
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
		# Else try the root ns.
		return self.root._load_binding(var)

class ClassNamespace(Namespace, kind=ScopeKind.CLASS):

	def _load_binding(self, var: str) -> Binding | None:
		""" Find the Binding, if any, containing the value of var.
		"""
		use = self.scope.get_use(var)
		if use.hasGLOB_DECL():
			return self.glob._load_binding(var)

		binding = self._get_bind(var)
		if binding: return binding
		if use.hasLOCAL():
			return self.glob._load_binding(var)
		if use.hasGLOBAL():
			return self.glob._load_binding(var)
		if use.hasFREE():
			return super()._load_binding(var)

class ClosedNamespace(Namespace, kind=ScopeKind.CLOS):
	pass

class FunctionNamespace(ClosedNamespace, kind=ScopeKind.FUNC):
	pass

class LambdaNamespace(ClosedNamespace, kind=ScopeKind.LAMB):
	pass

class ComprehensionNamespace(ClosedNamespace, kind=ScopeKind.COMP):
	pass

class LocalsNamespace(Namespace, kind=ScopeKind.LOCS):
	def _load_binding(self, var: str) -> Binding | None:
		""" Find the Binding, if any, containing the value of Var.
		locals() returns the binding if
		- has INLOCALS usage
		- is currently bound
		"""
		if self.parent.isCLOS():
			use: VarUse | None = self.parent.scope.get_use(var)
			if not use or not use.hasINLOCALS(): return self.parent.vars[var]
			binding_ns = self.search_scope(use.binding.bindings.scope)
			return binding_ns._get_bind(var)
		else:
			try: return self.parent._get_bind(var)
			except AttributeError: return None

class ExecEvalNamespace(LocalsNamespace, kind=ScopeKind.EVEX):
	def _load_binding(self, var: str) -> Binding:
		""" Find the Binding, if any, containing the value of Var.
		locals() returns the binding if
		- has INLOCALS usage
		- is currently bound
		Get the binding from the GLOB if this fails.
		"""
		binding: Binding = super()._load_binding(var)
		if binding: return binding
		return self.glob._load_binding(var)

class EvalNamespace(ExecEvalNamespace, kind=ScopeKind.EVAL):
	pass

class ExecNamespace(ExecEvalNamespace, kind=ScopeKind.EXEC):
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

	@classmethod
	def unbound(cls) -> Self:
		return cls()

	def unbind(self) -> None:
		""" Make unbound. """
		try: del self.value
		except: pass

	def __repr__(self) -> str:
		if self:
			return f'= {self.value!r}'
		else:
			return '<unbound>'

class Bindings(dict[VarName, Binding[ValT]]):
	""" Lookup table for Var names, with missing name resulting in None.
	Behavior can be customized by subclassing (for example, logging all operations).
	"""
	def __getitem__(self, var: VarName) -> Binding[ValT]:
		return self.get(var)

	def insert(self, var: VarName) -> Binding[ValT]:
		binding = self.get(var)
		if not binding:
			self[var] = binding = Binding.unbound()
		return binding

	def bind(self, var: VarName, value: ValT) -> None:
		self.insert(var).bind(value)

	def unbind(self, var: VarName) -> None:
		""" Make var unbound.  Raise AttributeError if already unbound. """
		self.insert(var).unbind()

class RootBindings(Bindings):
	""" Lookup table for Var names, using supplied global dict.
	TODO: use builtins module's dict if nothing else is supplied.
	"""
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
arbitrary expression in the context of that ns.

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

		# 1. Transform the source tree by replacing name references with calls to the ns.
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

