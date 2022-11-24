"""Python's scoping rules, as code.

There are lots of invariants and ideas not yet expressed in code:

- scopes form a tree with a GlobalScope at the root
- there are no GlobalScopes elsewhere in the tree
- *using* a name before a nonlocal declaration is also an error
- a way to check a scope's invariants
- locals/nonlocals/globals are disjoint
- everything about comprehensions
- translating the AST into a tree of scopes
- Using a subset of Python

"""


from __future__ import annotations

import sys
from typing import *
if sys.version_info < (3, 11): from typing_extensions import Self, TypeAlias
from abc import *
from enum import *
from contextlib import contextmanager
import ast

import attrs

from .scope_common import *

x = 'glob'
#def f():
#    x = 'closure'
#    class C:
#            print(x)
#            print(locals())
#            x = 'local'
#            print(locals())
#            print(x)
#            del x
#            exec('print(x)')
#            print(eval('x'))
#    def g():
#            print(locals())
#            print(x)
#            exec('print(x)')
#            print(eval('x'))
#    g()
#    def h():
#            print(locals())
#            exec('print(x)')
#            print(eval('x'))
#    h()

#f()

#def f():
#	x = 'closure'
#	def ex():
#		print(locals())
#		print(x)
#	return ex

#class C:
#	x = 'closure'
#	def ex():
#		print(locals())
#		print(x)

#ex = f()
#ex()

#C.ex()

#exec('ex()')
#exec('C.ex()')

__all__ = (
	'Scope',
	'RootScope',
	'GlobalScope',
	'ClassScope',
	'FunctionScope',
	'LambdaScope',
	'ComprehensionScope',
	#'VarCtx',
	'ScopeT',
	'SrcT',
	)

SrcT = TypeVar('SrcT')
ScopeT: TypeAlias = 'Scope[SrcT]'

class Scope(ScopeTree, Generic[SrcT]):
	is_scope: ClassVar[bool] = True
	name: str
	parent: Self | None
	glob: GlobalScope[SrcT]
	root: RootScope

	# Tracking the progress of the build.
	class BuildStage(IntEnum):
		BUILDING = auto()
		CLEANUP = auto()
		DONE = auto()

	# During building, earlier stages are set as an instance variable.
	# At the end, this variable is deleted, leaving the class variable.
	build_stage: BuildStage = BuildStage.DONE

	# Mapping of variable names to their binding scopes, for every var that appears in this scope.
	# The location may be self, or some enclosing scope.  It is determined at compile time.
	# The var is Local in its binding scope, which means that in that scope, the var is mapped to itself.
	# The binding scope may temporarily be unknown, but this is eventually resolved by the time the
	# entire scope has been built.
	# Any var that is not in vars is an unused var.
	vars: Mapping[str, VarUse | None]
	scope: Scope
	src: SrcT | None = None

	# Child Scopes, in the order they were created.
	nested: list[int, ScopeT]

	kind: ClassVar[ScopeKind]

	# True if this Scope will currently allow walrus operators.
	#	Otherwise reject, with a SyntaxError, any walrus expression.
	# It is False as an instance attribute:
	#	1. Temporarily while examining any ITER in a comprehension.
	#		Accomplished with 'with comprehension.in_iterable: ...' statement.
	#	2. Always, when the scope was created if the flag was set in its parent at the time.
	#		Since the parent is an expression, this scope can only be a comprehension or a lambda.
	walrus_allowed: ClassVar[bool] = True

	# True to interpret a bind() as part of an assignment expression.
	in_walrus: ClassVar[bool] = False

	# Convenience access to VarCtx values.

	for member in VarCtx.__members__:
		exec(f'@staticmethod\n'
			 f'def {member}():\n'
			 f'\treturn VarCtx.{member}')
	del member

	@abstractmethod
	def __init__(self, src: SrcT = None, parent: Scope = None, name: str = '',
				 **kwds):
		super().__init__(src, parent, name, **kwds)
		self.src = src
		self.scope = self
		self.bindings = VarBindings(self)
		self.vars = {}
		if parent and not parent.walrus_allowed: self.walrus_allowed = False
		self.start_build()

	def start_build(self) -> None:
		self.build_stage = self.BuildStage.BUILDING

	@contextmanager
	def build(self) -> Iterable[Self]:
		if self.build_stage is self.BuildStage.DONE:
			raise ValueError(f'Object {self!r} is already built')
		yield self			# perform building primitives in this context.
		if self.isCLASS() or self.isFUNC():
			self.parent.bind(self.name, VarCtx.NESTED)
		self.build_stage = self.BuildStage.DONE

	def qualname(self, varname: str = '', *, sep: str = '.') -> str:
		""" Fully qualified name of this scope, or given variable name in this scope.
		Optional separator to replace '.'.
		Global scope is part of this name only if it has its own name.
		"""
		names = list(self.scope_names)
		if varname: names.append(varname)
		if not names: names = ['<global>']
		return sep.join(names)

	@property
	def objname(self) -> str:
		return self.qualname(sep='_')

	@property
	def scope_names(self) -> Iterator[str]:
		""" Iterator for names of self and enclosed scopes, from globals to self.
		Global scope is part of this only if it has its own name.
		"""
		yield from self.parent.scope_names
		yield self.name

	def get_use(self, name: VarName, makenew: bool = False) -> VarUse:
		""" The VarUse for given name, install a new one if needed and requested. """
		use: VarUse = self.vars.get(name)
		if not use: use = VarUse(None, VarCtx.UNUSED)
		if use.hasUNUSED() and makenew or self.build_stage is not self.BuildStage.DONE:
			self.vars[name] = use
		return use

	def context(self, var: str) -> VarCtx:
		return self.get_use(var).ctx

	def usage(self, var: str) -> VarCtx:
		return self.context(var).usage

	def type(self, var: str) -> VarCtx:
		return self.context(var).type

	@var_mangle
	def use(self, name: VarName) -> None:
		""" Set USE context flag.
		"""
		use: VarUse = self.get_use(name)
		use.useUSE()

	@var_mangle
	def bind(self, name: VarName,
			flags: VarCtx = VarCtx(0),
			**kwds):
		""" Set the BINDING context flag, and any other extras given.
		Also create a local binding if not externally defined
		"""
		use: VarUse = self.get_use(name)
		if not use.hasEXTERN_BIND() or self.isGLOB():
			use.binding = self._make_binding(name)
		#print(type(use))
		#print(dir(use))
		#print(dir(type(use)))
		use.useBINDING()

		if flags: use.ctx |= flags

	def _bind_walrus(self, name: VarName, **kwds) -> Scope:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		Implemented differently in CLASS and COMP scopes.
		"""
		self.bind(name, **kwds)
		return self.vars[name]

	@contextmanager
	def use_walrus(self):
		""" A bind() call in this context is a walrus operator.
		SyntaxError if part of a comprehension iterable.
		"""
		if not self.walrus_allowed:
			raise SyntaxError(
				'assignment expression cannot be used in a comprehension iterable expression')

		save = self.in_walrus
		self.in_walrus = True
		yield
		self.in_walrus = save

	@var_mangle
	def decl_nonlocal(self, name: VarName) -> None:
		""" Declare the var as being nonlocal. """
		use: VarUse = self.get_use(name)
		# Only NLOC_DECL is valid.
		if use.hasNLOC_DECL(): return
		if not use.hasUNUSED(): use.ctx.raise_err(name, VarCtx.NLOC_DECL)
		use.useNLOC_DECL()

	@var_mangle
	def decl_global(self, name: VarName) -> None:
		""" Declare the var as being global. """
		use: VarUse = self.get_use(name)
		# Only GLOB_DECL is valid.
		if use.hasGLOB_DECL(): return
		if not use.hasUNUSED(): use.ctx.raise_err(name, self.GLOB_DECL())
		use.useGLOB_DECL()
		use.binding = self.glob._make_binding(name)
		self.glob.decl_global(name)

	@contextmanager
	def nest(self, kind: ScopeKind, src: SrcT, name: str = '', scope: ScopeT = None, **kwds) -> Iterable[Scope]:
		""" Report a nested scope.  Create the Scope object.
		Report the name as assigned in the current scope, except for
			Lambda and Comprehension, which are anonymous.
		"""
		with super().nest(kind, src, name, **kwds) as result:
			src = result.src
			yield result

	def _cleanup(self) -> None:
		""" Resolve binding scope for all Seen and Closure variables, recursively.
		Add missing CELL variables while processing descendants.
		"""
		self.build_stage = self.BuildStage.CLEANUP
		var: VarName
		def add_CELL(scope: Scope) -> None:
			while True:
				if scope.isROOT(): return
				use : VarUse = scope.get_use(var)
				if not use.hasTYPES():
					use = set_type(scope)
				if scope.isCLOS():
					if use.hasCELL(): return
					if use.hasGLOBAL(): return
					if use.hasLOCAL(): return
					# FREE goes to CELL + FREE.
					use.setCELL()

				scope = scope.parent

		def set_type(scope: Scope) -> VarUse:
			""" Set the TYPES bit. """
			use: VarUse = scope.get_use(var, makenew=True)
			if not use.binding:
				try: binding = scope.binding(var)
				except SyntaxError:
					use.setUNRES()
					return use
				use.binding = binding
				use = scope.vars[var]

			# Set the TYPES bit(s).
			# In GLOB scope, type is both LOCAL and GLOBAL.
			# Don't set CELL now.  CELL may be added to FREE later.
			sc = use.binding.bindings.scope
			if sc is scope:
				use.setLOCAL()
			if sc is scope.glob:
				use.setGLOBAL()
			if not use.hasTYPES():
				use.setFREE()
			return use

		for var in list(self.vars):
			use = set_type(self)
			if use.hasFREE() and use.hasUSE(): add_CELL(self)

		self.build_stage = self.BuildStage.DONE
		for nested in self.nested:
			nested._cleanup()

		for var, use in self.vars.items():
			if not use.hasGLOBAL() and not use.hasLOCAL():
				assert use.hasCELL() == (
					self.isCLOS()  and (self._captures(self.binder(var), var))), (self, var, use)
			else:
				assert not use.hasCELL(), (self, var, use)

	def _make_binding(self, name: VarName) -> Variable:
		""" Create a binding for name in this scope, if it doesn't already exist.
		Return the binding Variable.
		In response to
		(1) self.bind(var), or 
		(2) in global scope if var resolves to here from an enclosed scope.
		"""
		use: VarUse = self.get_use(name)
		var: Variable = use.binding
		if not var:
			var = use.binding = self.bindings[name]
		return var

	# Methods after tree build is complete...

	@var_mangle
	def binding(self, name: VarName) -> Variable:
		""" Find the binding.
		SyntaxError if var is still unresolved (i.e. nonlocal variable with no matching scope).
		"""
		if self.build_stage < self.BuildStage.CLEANUP:
			raise ValueError(f'Cannot resolve names in scope {self!r} before it and all ancestors are built.')

		binding = self._binding(name, skipclass=False)
		if not binding:
			raise SyntaxError(f"no binding for nonlocal '{name}' found in scope {self.qualname()}")
		return binding

	@var_mangle
	def _binding(self, name: VarName, skipclass: bool = True, closure: bool = False, **kwds) -> Variable | None:
		""" Tries to find the binding object for the var. """
		# Implemented differently in GlobalScope.
		use: VarUse = self.get_use(name)
		if use.hasGLOB_DECL(): return self.glob._binding(name, **kwds)
		if use.hasNLOC_DECL(): return self.parent._binding(name, closure=True, **kwds)
		if use.hasBINDING(): return self._make_binding(name)
		else: return self.parent._binding(name, **kwds)

	def binding_scope(self, name: VarName, **kwds) -> Scope | None:
		use: VarUse = self.get_use(name)
		if use and use.binding:
			return use.binding_scope
		try: return self._binding(name).bindings.scope
		except AttributeError: return None

	def _captures(self, binder: Scope, name: VarName) -> bool:
		""" Whether a FREE var is used and has same binder as given binder,
		in any scope in the subtree.
		"""
		if name in self.vars:
			use = self.get_use(name)
			if use.hasLOCAL():
				if self.isCLOS() and self.binder(name) is not binder: return False
			elif use.hasUSE():
				if self.binder(name) is binder: return True
				elif not use.hasFREE() and self.isCLOS(): return False
		# Try child subtrees.
		return any(child._captures(binder, name)
			for child in self.nested)

	@var_mangle
	def binder(self, name: VarName) -> Scope:
		return self.binding(name).bindings.scope

	def dump_vars(self, leader: str = '') -> None:
		print(f'{leader}{self!r}')
		leader += '  '
		for var, use in self.vars.items():
			try: scope_name = use.binding.bindings.scope.qualname()
			except AttributeError: scope_name = '(unresolved)'
			print(f'{leader}{var} {use.ctx!r} -> {scope_name}')
		for sc in self.nested:
			sc.dump_vars(leader)

class RootScope(Scope, kind=ScopeKind.ROOT):
	""" Container for all the modules in a program.
	Will be created for a GlobalScope's parent if one is not provided to it.
	"""
	modules: Mapping[str, GlobalScope]

	def __init__(self, *args, **kwds):
		super().__init__(None, *args, **kwds)
		self.modules = {}

class NestedScope(Scope):
	""" Any Scope other than GlobalScope or RootScope.  Subclasses are OpenScope and ClosedScope.
	"""
	parent: GlobalScope  # Cannot be None

class OpenScope(NestedScope, kind=ScopeKind.OPEN):
	def exec_effective(self, name: VarName) -> bool: return True

class GlobalScope(OpenScope, kind=ScopeKind.GLOB):
	parent: RootScope | None
	initial: dict = None

	def __init__(self, src: SrcT, parent: RootScope = None, name: str = '', initial: dict = None, **kwds):
		super().__init__(src, parent or RootScope(), name, **kwds)
		if initial:
			self.initial = initial
		if name:
			self.root.modules[name] = self

	def decl_nonlocal(self, var: str) -> NoReturn:
		raise SyntaxError("nonlocal declaration not allowed at module level")

	@var_mangle
	def decl_global(self, name: VarName) -> Scope:
		self._make_binding(name)
		self.get_use(name).useGLOB_DECL()

	@contextmanager
	def build(self) -> Iterable[Self]:
		with super().build():
			yield self
		self._cleanup()

	@var_mangle
	def _binding(self, name: VarName, closure: bool = False, **kwds) -> Variable:
		""" Get the static scope for this var.  It is always self. """
		if closure: return None
		else: return self._make_binding(name)

	@var_mangle
	def _bind_walrus(self, name: VarName, **kwds) -> Scope:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		Implemented differently in CLASS and COMP scopes.
		"""
		self.bind(name, **kwds)
		self.decl_global(name)
		return self.vars[name]

	@property
	def scope_names(self) -> Iterator[str]:
		if self.name: yield self.name

class ClassScope(OpenScope, kind=ScopeKind.CLASS):

	def _bind_walrus(self, name: VarName, **kwds) -> NoReturn:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		This is a syntax error.
		"""
		raise SyntaxError('assignment expression within a comprehension cannot be used in a class body')

	def _binding(self, name: VarName, skipclass: bool = True, **kwds) -> Scope | None:
		""" Tries to find the binding object for the var, possibly skipping over any CLASS scopes. """
		if skipclass:
			return self.parent._binding(name, **kwds)
		else:
			return super()._binding(name, **kwds)

class LocalsScope(OpenScope, kind=ScopeKind.LOCS):
	""" Evaluates builtin locals() in the parent scope.
	Binding for a name is same as in the parent, only if it has INLOCALS context.
	"""

	def _binding(self, name: VarName, **kwds) -> Variable | None:
		use: VarUse = self.parent.get_use(name)
		if use.hasINLOCALS:
			return self.parent._binding(name, skipclass=False)
		return None

class ExecEvalScope(LocalsScope, kind=ScopeKind.EVEX):
	parent: GlobalScope  # Cannot be None
	local: Mapping = None	# Used at runtime as replacement for locals().
	mode: Final[str] = 'exec/eval'

	def __init__(self, src: SrcT = None, parent: Scope = None, name: str = '', *, glob: dict = None, loc: Mapping = None, **kwds):
		if not parent:
			parent = GlobalScope(f'<{mode}>', initial=glob)
		else:
			assert not glob, 'Cannot have both parent and global dict.'

		super().__init__(src, parent, name or f'<{self.mode}>', **kwds)
		if loc: self.local = loc

	def _binding(self, name: VarName, **kwds) -> Variable:
		""" Get the static scope for this var.
		Try the locals first, then the globals.
		"""
		# Local variables are either the locals() dict in the parent scope when evex() is called,
		# or a specific dict.
		if self.loc:
			binding = self.loc.get(name)
		else:
			binding = super()._binding(name)
		if binding: return binding

		return self.parent._binding(name)

class ExecScope(ExecEvalScope, kind=ScopeKind.EXEC):
	mode: Final[str] = 'exec'
	def __init__(self, *args, **kwds):
		super().__init__(*args, mode='exec', **kwds)

class EvalScope(ExecEvalScope, kind=ScopeKind.EVAL):
	mode: Final[str] = 'eval'
	def __init__(self, *args, **kwds):
		super().__init__(*args, mode='eval', **kwds)

class ClosedScope(NestedScope, kind=ScopeKind.CLOS):

	@var_mangle
	def exec_effective(self, name: VarName) -> bool:
		""" True if an exec('name' = value) will change 'name' at runtime. """
		use = self.get_use(name)
		if use:
			if use.hasINLOCALS():
				return False
		return True

class FunctionScope(ClosedScope, kind=ScopeKind.FUNC):
	pass

class LambdaScope(ClosedScope, kind=ScopeKind.LAMB):
	pass

class ComprehensionScope(ClosedScope, kind=ScopeKind.COMP):
	is_comp: ClassVar[bool] = True

	# Note, bind(var) and _bind_walrus(var) for the same var are contradictory, in either order
	# of occurence.  _bind_walrus() may have bubbled up from a nested COMP.
	# Either of these stores a binding in self.vars[var], but the usage is BINDING in the
	# first case and something else in the second case.`
	# The second of the two occurrences raises a SyntaxError.

	@var_mangle
	def bind(self, name: VarName, **kwds) -> None:
		""" Specialized bind() for COMPs, handles walrus differently.
		The bind() is delegated up to the first non-COMP enclosing scope.
		"""
		if self.in_walrus:
			use: VarUse = self.get_use(name)
			owner_bind: VarUse = self._bind_walrus(name)
			if owner_bind.hasGLOB_DECL():
				use.useGLOB_DECL()
			else:
				use.useNLOC_DECL()
			use.setBINDING()
		else:
			# Not a walrus.  Check for previous walrus binding.
			use: VarUse = self.vars.get(name)
			if use and use.hasWALRUS():
				use.ctx.raise_err(name, VarCtx.WALRUS)
			super().bind(name, **kwds)

	def _bind_walrus(self, name: VarName) -> VarUse:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		Defines a binding in this scope as well.
		SyntaxError if name is already BINDING
		"""
		use: VarUse = self.get_use(name)
		if use.hasBINDING() and not use.hasWALRUS():
			# Already seen as an iteration variable in this scope.
			use.ctx.raise_err(name, VarCtx.WALRUS)
		use.useWALRUS()
		# Try the parent, recursively.
		use = self.parent._bind_walrus(name)
		return use

	@var_mangle
	def _binding(self, name: VarName, **kwds) -> Variable | None:
		""" Find the binding.
		SyntaxError if var is still unresolved (i.e. nonlocal variable with no matching scope).
		"""
		use: VarUse = self.get_use(name)
		if not use: return None
		if use.hasWALRUS:
			return self.parent._binding(name)
		return super()._binding(name)

	@contextmanager
	def in_iterable(self):
		""" The body of the 'with in_iterable' statement is within the ITER in a
		'for target_list in ITER' clause.
		This makes all walrus expressions raise SyntaxErrors, including in nested
		comprehensions or lambdas.
		"""
		save = self.walrus_allowed
		self.walrus_allowed = False
		yield
		if save:
			del self.walrus_allowed

def test():
	# Set up a sample program
	# def outer():
	#   n = 42
	#   class C:
	#	  anno: int
	#	  (anno2): int
	#	  [wal := 0 for x in []]		# syntax error
	#     def foo(self, a = blah):
	#       global x
	#       x = a
	#       nonlocal n
	#	    anno: int
	#	    (anno2): int
	#       used

	 
	import treebuild
	print('testing scopes.py')
	root = RootScope()
	builder = treebuild.Builder(root)
	with builder.nestGLOB(None, 'top') as g:
		with builder.nestFUNC(None, 'f') as f:
			f.bind('x')
			f.bind('y')
			f.bind('z')
			with f.nestCLASS(None, 'C') as C:
				ref = ScopeTreeProxy(C)
				ref.bind('__x')
				with ref.nestFUNC(None, '__f') as f2: pass
				C.bind('x')
				with C.nestFUNC(None, 'h') as h:
					h.decl_nonlocal('x')
					h.decl_nonlocal('y')

		with builder.nestFUNC(None, 'outer') as outer:
			builder.bind('n')
			with builder.nest(outer.CLASS(), None, 'C') as c:
				builder.anno('anno', int)
				with builder.nestFUNC(None, 'foo') as foo:
					builder.bind('self', VarCtx.PARAM)
					builder.bind('a', VarCtx.PARAM)
					builder.use('a')
					builder.decl_global('x')
					builder.bind('x')
					builder.decl_nonlocal('n')
					#builder.decl_nonlocal('unres')
					builder.anno('anno', int)
					builder.use('used')
					# COMP scope hierarchy:
					#	lc
					#		bind w
					#		Walrus w2
					#		Walrus w is error
					#		bind w2 is error
					#		lc2
					#			bind w is OK
					#			bind w2 is error
					#			Walrus w is error
					#			Walrus w is OK
					#		lci (in iterable of lc)
					#			Walrus is error
					#			lci2
					#				Walrus is error
					#			lam (LAMB)
					#				Walrus is error

					#with foo.nestEXEC(None, '<exec>') as ex:
					with foo.nest(foo.EXEC(), None, '<exec>') as ex:
						x = 0
					with foo.nestCOMP(None, 'outercomp') as lc:
						lc.bind('w')
						with lc.use_walrus():
							lc.bind('w2')
							try: lc.bind('w')
							except SyntaxError as e:
								assert str(e) == "assignment expression cannot rebind comprehension iteration variable 'w'"
							else: assert 0
						try: lc.bind('w2')
						except SyntaxError as e:
							assert str(e) == "assignment expression cannot rebind comprehension iteration variable 'w2'"
						else: assert 0
						with lc.nestCOMP(None, 'innercomp') as lc2:
							lc.bind('w')		# This is OK
							try: lc.bind('w2')
							except SyntaxError as e:
								assert str(e) == "assignment expression cannot rebind comprehension iteration variable 'w2'"
							else: assert 0
							with lc.use_walrus():
								try: lc.bind('w')
								except SyntaxError as e:
									assert str(e) == "assignment expression cannot rebind comprehension iteration variable 'w'"
								else: assert 0
								lc.bind('w2')	# This is OK.
						with lc.in_iterable(): 
							with lc.nestCOMP(None, 'itercomp') as lci:
								pass
								try:
									lci.use_walrus().__enter__()
								except SyntaxError as e:
									assert str(e) == "assignment expression cannot be used in a comprehension iterable expression"
								else: assert 0
								with lci.nestCOMP(None, 'iterinnercomp') as lci2:
									try:
										lci2.use_walrus().__enter__()
									except SyntaxError as e:
										assert str(e) == "assignment expression cannot be used in a comprehension iterable expression"
									else: assert 0
								with lci.nestLAMB(None, 'iterlambda') as lam:
									try:
										with lam.use_walrus():
											pass
									except SyntaxError as e:
										assert str(e) == "assignment expression cannot be used in a comprehension iterable expression"
									else: assert 0

				with builder.nest(c.COMP(), None, 'listcomp') as lc2:
					with builder.use_walrus():
						try: builder.bind('wal')
						except SyntaxError as e:
							assert str(e) == "assignment expression within a comprehension cannot be used in a class body"


	C.bind('__foo')
	g.dump_vars()
	try: foo.binding('unres')
	except SyntaxError: pass
	repr(VarName('__x', foo))

	b = VarBindings(foo)
	v = b[VarName('w')]

	repr(v)
	#assert ex.binding_scope('n') is outer

	assert foo.binding_scope("C") is outer
	assert c.binding_scope("C") is outer

	assert foo.binding_scope("foo") is g
	assert c.binding_scope("foo") is c

	assert foo.binding_scope("self") is foo
	assert c.binding_scope("self") is g

	assert foo.binding_scope("a") is foo
	assert c.binding_scope("a") is g

	assert foo.binding_scope("blah") is g
	assert c.binding_scope("blah") is g

	assert foo.binding_scope("x") is g
	assert c.binding_scope("x") is g

	assert foo.binding_scope("w") is g
	assert lc.binding_scope("w") is lc

	assert foo.binding_scope("w2") is foo
	assert lc.binding_scope("w2") is foo

	assert foo.binding_scope("anno") is foo
	assert c.binding_scope("anno") is c

	assert foo.binding_scope("anno2") is g
	assert c.binding_scope("anno2") is g

	assert foo.binding_scope("used") is g
	assert c.binding_scope("used") is g

if __name__ == "__main__":
	import scopes
	scopes.test()
