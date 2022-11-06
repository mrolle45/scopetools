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
from typing_extensions import Self, TypeAlias
from abc import *
from enum import *
from contextlib import contextmanager
import ast

import attrs

from scope_common import *

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


"""
Everything about scopes:

Every Scope corresponds to a module, a function, or a class.
	A function includes function defs, lambdas, and comprehensions.

Every scope other than a module is enclosed in a larger scope.  Scopes form a tree structure.

A scope has static (determined by the compiler) and dynamic (determined at runtime) properties.

The Scope class manages the static properties.  Once the Scopes tree is constructed for the
program, it remains constant and it may be used in the analysis of the code contained in them.

The Namespace class (in namespaces module) manages dynamic properties of scopes.

A Scope has variables.  A variable (or 'var') is a name which is found in the scope.
	In the global scope, it may also be a var which is declared global in a nested scope.

For each var in a Scope, it is associated with a "binding Scope".  This may be the same
Scope or it may be some enclosing Scope.  The var is said to be "Local" in the binding scope.

Important: If the binding Scope is not the original Scope, then it is considered to be the SAME
VARIABLE in both scopes.

The Scope is built with a series of primitive static operations, which correspond to things found
in the Python program.  They are performed in the same order as they appear in the program.  Also,
when a nested Scope is created, the new scope is built at that time, and then building of the
original scope continues.

Refer to the ScopeTree class for details.

After the ENTIRE Scopes tree has been built, then the Scopes can be examined for their static properties.
These are properties that apply only to Scope objects.  See the Scope class for details.

Scope building primitive operations:

	load(var).  Just reports the fact that this var appears.

	anno(var, anno).	Just reports appearance of var in statement 'var: anno'.
		Same as load(var), except:
			The var is local to the current scope.
			It conflicts with an earlier or later decl_nonlocal() or decl_global().
			The SyntaxError text is different with annotated variables.
			The scope records that var is an annotated variable.

	store(var).  Notes the fact that the var has been assigned, or reassigned.
		var becomes Local if it is Seen or Unused.
		The optional value is ignored.  It is provided for compatibility with Namespace builders.
		
	store_walrus(var).  A variant of store(var) behaving differently in a comprehension.
		This is delegated to the enclosing scope.
		It is a SyntaxError if:
			The said enclosing scope is a class.
			The target name appears anywhere as a "for" target in this scope.
			The call appears dynamically within a 'with walrus_allowed' at any level.
				This also applies in a LambdaScope, which is possible in a comprehension.

	delete(var).  Notes that the variable has been deleted.  Treated same as store(var)

	decl_global(var).  Declares the var to be in the global scope.
		If earlier loaded in a non-global scope, this is a SyntaxError.
		Also adds a load(var) to the global scope.

	decl_nonlocal(var).  Declares the var to be in an enclosing closed scope.
		If earlier loaded, or in the global scope, this is a SyntaxEerror.
		Actually locating this enclosed scope happens in the Resolve phase of the tree build.

	with nest(kind, [name], [src]) as scope: body...
		Creates a nested scope for these parameters.  If a name is given, it is bound in the
			parent scope.  The nested scope is passed to the caller, which will build it.
		Arguments provided:
			Kind of Scope to be used.
			An optional src object.
			An optional name, for function and class defs only.
		Creates a nested Scope for these parameters.
		If name is specified it is stored in the current scope.
		Calls the new scope's builder, with the new scope as the current scope.

	with parent(): body...  Delegates load and store operations to the current scope's parent.

	with walrus_allowed(): body...  Disables ALL store_walrus() calls (raise SyntaxError).
		This is reported when examining any ITER expression in any comprehension.

After the Create phase is complete, these operations are valid:

	Note that Resolve phase will have been performed on all enclosing scopes.

	_closure(var).  Looks for a closed scope in which var is Local (if any),
		including possibly the current scope itself.

		These are the _closure rules:
		1.	An open scope returns its parent._closure().
		2.	The global scope returns None.
		3.	A closed scope returns itself if var is Local,
			otherwise returns its parent._closure().

	binder(var).  Returns the binding scope for the var, if any.
		The binding scope might already be stored in the scope.
		If the binding scope exists, return it.
		Try calling _closure(var).  If there is a value found, this is
			the binding.
		Otherwise it depends on the context of var:
			For Unresolved, then either raise a SyntaxError or leave it as Unresolved.
			Else the var is Seen or Unused.  Use the global scope as the binding scope, and
			perform load(var) on the global scope (which will make it a Top there).
		In all cases, except a SyntaxError of course, store the result as the binding scope.

	binding(var).  Returns the binding Scope object for the var, if any.
		It points to the binding scope.
"""

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
		self.binder = VarBinder(self)
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
		if self.kind in (self.kind.CLASS, self.kind.FUNC):
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

	def get_use(self, name: VarName, makenew: bool = True) -> VarUse:
		""" The VarUse for given name, install a new one if needed and requested. """
		info: VarUse = self.vars.get(name)
		if (not info or not info.hasUSAGE()) and makenew and self.build_stage is not self.BuildStage.DONE:
			if not info: info = VarUse(None, VarCtx.UNUSED)
			self.vars[name] = info
		return info

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
		info: VarUse = self.get_use(name)
		info.setUSE()

	@var_mangle
	def bind(self, name: VarName,
			flags: VarCtx = VarCtx(0),
			**kwds):
		""" Set the BINDING context flag, and any other extras given.
		Also create a local binding if not externally defined
		"""
		info: VarUse = self.get_use(name)
		if not info.hasEXTERN_BIND() or self.kind.is_global:
			info.binding = self._make_binding(name)
		info.setBINDING()

		if flags: info.ctx |= flags

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
		info: VarUse = self.get_use(name)
		# Only NLOC_DECL is valid.
		if info.hasNLOC_DECL(): return
		if info.hasUSAGE(): info.ctx.raise_err(name, VarCtx.NLOC_DECL)
		info.setNLOC_DECL()

	@var_mangle
	def decl_global(self, name: VarName) -> None:
		""" Declare the var as being global. """
		info: VarUse = self.get_use(name)
		# Only GLOB_DECL is valid.
		if info.hasGLOB_DECL(): return
		if info.hasUSAGE(): info.ctx.raise_err(name, self.GLOB_DECL())
		info.setGLOB_DECL()
		info.binding = self.glob._make_binding(name)
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
		var: str
		def add_CELL(scope: Scope) -> None:
			if scope.kind.is_root: return
			info = scope.get_use(var)
			#if not info:
			#	info = set_type(scope)
			set_type(scope)
			if scope.kind.is_closed:
				if info.hasCELL(): return
				if info.hasGLOBAL(): return
				# FREE goes to CELL and not FREE.  UNUSED likewise
				if info.hasFREE() or not info.hasUSAGE(): info.clrFREE().setCELL()

				if info.hasLOCAL(): return
			add_CELL(scope.parent)

		def set_type(scope: Scope) -> VarUse:
			""" Set the TYPES bit. """
			info: VarUse = scope.vars.get(var)
			if not info or not info.binding:
				try: scope.binding(var, cacheit=True)
				except SyntaxError:
					info.setUNRES()
					return info
				info = scope.vars[var]

			# Set the TYPES bit(s).
			# In GLOB scope, type is both LOCAL and GLOBAL.
			# Not CELL.  FREE may change to CELL later
			sc = info.binding.binder.scope
			if sc is scope:
				info.setLOCAL()
			if sc is scope.glob:
				info.setGLOBAL()
			if not info.hasTYPES():
				info.setFREE()
			#assert info.ctx.getLOCAL == (info.ctx.getBINDING or self.kind.is_global), (scope, var)
			return info

		for var in list(self.vars):
			info = self.get_use(var)

			info = set_type(self)
			if info.hasFREE() and info.hasUSE(): add_CELL(self)

		for nested in self.nested:
			nested._cleanup()

		for var in list(self.vars):
			info = self.get_use(var)
			if not info.hasGLOBAL() and not info.hasLOCAL():
				assert info.hasCELL() == (
					self.kind.is_closed  and (self.captures(self.binding(var), var))), (self, var, info)
			else:
				assert not info.hasCELL(), (self, var, info)
			#if info.hasWALRUS() and not info.hasBINDING():
			#	# This is a COMP which was skipped in binding var in an inner COMP.
			#	# A GLOBAL var does not appear in compiler's symbol table.
			#	if info.hasGLOBAL():
			#		del self.vars[var]

		self.build_stage = self.BuildStage.DONE

	def _make_binding(self, name: VarName) -> Variable:
		""" Create a binding for name in this scope, if it doesn't already exist.
		Return the binding Variable.
		In response to
		(1) self.bind(var), or 
		(2) in global scope if var resolves to here from an enclosed scope.
		"""
		info: VarUse = self.get_use(name)
		var: Variable = info.binding
		if not var:
			var = info.binding = self.binder[name]
		return var

	# Methods after tree build is complete...

	def binding(self, name: VarName, cacheit: bool = False) -> Variable:
		""" Find the binding.
		SyntaxError if var is still unresolved (i.e. nonlocal variable with no matching scope).
		"""
		if self.build_stage < self.BuildStage.CLEANUP:
			raise ValueError(f'Cannot resolve names in scope {self!r} before it and all ancestors are built.')

		binding = self._binding(name)
		if not binding:
			raise SyntaxError(f"no binding for nonlocal '{name}' found in scope {self!r}")
		if cacheit: self.get_use(name).binding = binding
		return binding

	def _binding(self, name: VarName, **kwds) -> Variable | None:
		""" Tries to find the binding object for the var. """
		# Implemented differently in NestedScope, GlobalScope.
		raise NotImplementedError

	def binding_scope(self, name: VarName, **kwds) -> Scope | None:
		info: VarUse = self.get_use(name)
		if info and info.binding:
			return info.binding_scope
		try: return self._binding(name).binder.scope
		except AttributeError: return None

	def captures(self, binding: Variable, name: VarName) -> bool:
		""" Whether a FREE var is used and is same as given variable,
		in any scope in the subtree.
		"""
		if name in self.vars:
			use = self.get_use(name)
			if use.hasLOCAL():
				if self.kind.is_closed and self.binding(name) is not binding: return False
			elif use.hasUSE():
				if self.binding(name) is binding: return True
				elif not use.hasFREE() and self.kind.is_closed: return False
		# Try child subtrees.
		return any(child.captures(binding, name)
			for child in self.nested)

	def exec_effective(self, name: VarName) -> bool: return True

	def closures(self) -> Iterable[Variable]:
		""" Iterates over all variables with CELL context bit. """
		for info in self.vars.values():
			if info.ctx.getLOCAL or info.ctx.getCELL: info.binding

	def dump_vars(self, leader: str = '') -> None:
		print(f'{leader}{self!r}')
		leader += '  '
		for var, info in self.vars.items():
			try: scope_name = info.binding.binder.scope.qualname()
			except AttributeError: scope_name = '(unresolved)'
			print(f'{leader}{var} {info.ctx!r} -> {scope_name}')
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

class GlobalScope(Scope, kind=ScopeKind.GLOB):
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
		self.get_use(name).setGLOB_DECL()

	@contextmanager
	def build(self) -> Iterable[Self]:
		with super().build():
			yield self
		self._cleanup()

	@var_mangle
	def _binding(self, name: VarName, **kwds) -> Variable:
		""" Get the static scope for this var.  It is always self. """
		return self._make_binding(name)

	def _closure(self, _var: str) -> None:
		""" Get nearest enclosing ClosedScope for var, if any.  It is always None. """
		return None

	def _bind_walrus(self, name: VarName, **kwds) -> Scope:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		Implemented differently in CLASS and COMP scopes.
		"""
		self.bind(name, **kwds)
		self.decl_global(name)
		return self.vars[name]

	#def _make_binding(self, name: VarName) -> Variable:
	#	""" Create a binding for name in this scope, if it doesn't already exist.
	#	Return the binding Variable.
	#	In response to
	#	(1) self.bind(var), or 
	#	(2) in global scope if var resolves to here from an enclosed scope.
	#	"""
	#	return super()._make_binding(name)

	@property
	def scope_names(self) -> Iterator[str]:
		if self.name: yield self.name

class NestedScope(Scope):
	""" Any Scope other than GlobalScope or RootScope.  Subclasses are OpenScope and ClosedScope.
	"""
	parent: GlobalScope  # Cannot be None

	@var_mangle
	def _binding(self, name: VarName, cacheit: bool = False) -> Variable | None:
		""" Find the binding.
		SyntaxError if var is still unresolved (i.e. nonlocal variable with no matching scope).
		"""

		info: VarUse = self.get_use(name)
		if self.kind.is_comp:
			if info and info.hasWALRUS():
				# WALRUS.  Get from parent.
				return self.parent._binding(name)
		binding: Variable | None = info.binding
		if binding:
			# Local, Free, and Global.
			return binding
		# Look for a binding in an enclosing closed scope.
		closure: Variable | None = self._closure(name)
		if closure:
			# Make Free.
			binding = closure
		else:
			if info.hasNLOC_DECL():
				# Free, no closure scope.  This is an error.
				return None
			else:
				# Seen or Unused.  Make Global.
				binding = self.glob._make_binding(name)

		if cacheit: self.vars[name] = attrs.evolve(info, binding=binding)
		return binding

class OpenScope(NestedScope):

	def _closure(self, var: str) -> Scope | None:
		""" Get nearest enclosing ClosedScope for var, if any.  Never self.  """
		return self.parent._closure(var)

class ExecEvalScope(OpenScope, kind=ScopeKind.EVEX):
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

	def _closure(self, var: str) -> Scope | None:
		if not self.parent.context(var) & (VarCtx.CELL | VarCtx.LOCAL): return None
		if self.parent.kind.is_open: return None
		return super()._closure(var)

class ExecScope(ExecEvalScope, kind=ScopeKind.EXEC):
	mode: Final[str] = 'exec'
	def __init__(self, *args, **kwds):
		super().__init__(*args, mode='exec', **kwds)

class EvalScope(ExecEvalScope, kind=ScopeKind.EVAL):
	mode: Final[str] = 'eval'
	def __init__(self, *args, **kwds):
		super().__init__(*args, mode='eval', **kwds)

class LocalsScope(OpenScope, kind=ScopeKind.LOCS):
	""" Evaluates builtin locals() in the parent scope.
	Binding for a name is same as in the parent, only if it has INLOCALS context.
	"""

	def _binding(self, name: VarName, cacheit: bool = False) -> Variable | None:
		use = self.parent.get_use(name)
		if use.ctx.hasINLOCALS:
			return self.parent._binding(name)
		return None

class ClassScope(OpenScope, kind=ScopeKind.CLASS):

	def _bind_walrus(self, name: VarName, **kwds) -> NoReturn:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		This is a syntax error.
		"""
		raise SyntaxError('assignment expression within a comprehension cannot be used in a class body')

class ClosedScope(NestedScope):

	def _closure(self, name: VarName) -> Variable | None:
		""" Get nearest enclosing ClosedScope, including self, for var, if any. """
		info: VarUse | None = self.vars.get(name)
		binding = info and info.binding
		if binding:
			# Local. Free, or Global.
			if binding.binder.scope.kind.is_closed:
				# This is it.
				return binding
			else:
				return None
		else:
			# Not here.  Try parent (recursively).
			return self.parent._closure(name)

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

class LambdaScope(FunctionScope, kind=ScopeKind.LAMB):
	pass

class ComprehensionScope(FunctionScope, kind=ScopeKind.COMP):
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
			info: VarUse = self.get_use(name)
			owner_bind: VarUse = self._bind_walrus(name)
			if owner_bind.hasGLOB_DECL():
				info.setGLOB_DECL()
			else:
				info.setNLOC_DECL()
			info.setBINDING()
		else:
			# Not a walrus.  Check for previous walrus binding.
			info: VarUse = self.vars.get(name)
			if info and info.hasWALRUS():
				info.ctx.raise_err(name, VarCtx.WALRUS)
			super().bind(name, **kwds)

	def _bind_walrus(self, name: VarName) -> VarUse:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		Defines a binding in this scope as well.
		SyntaxError if name is already BINDING
		"""
		info: VarUse = self.get_use(name)
		if info.hasBINDING() and not info.hasWALRUS():
			# Already seen as an iteration variable in this scope.
			info.ctx.raise_err(name, VarCtx.WALRUS)
		info.setWALRUS()
		# Try the parent, recursively.
		info = self.parent._bind_walrus(name)
		return info

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
				ref = TreeRef(C)
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

	b = VarBinder(foo)
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
