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
from contextlib import contextmanager

import sys
from typing import *
from typing_extensions import Self, TypeAlias
from abc import *
from enum import *
from contextlib import contextmanager
import ast

import attrs

from scope_common import *

__all__ = (
	'Scope',
	'RootScope',
	'GlobalScope',
	'ClassScope',
	'FunctionScope',
	'LambdaScope',
	'ComprehensionScope',
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

		Note, this is also called by RootScope.add_module(), which supplies GLOB as the scope kind.

	with parent(): body...  Delegates load and store operations to the current scope's parent.

	with walrus_allowed(): body...  Disables ALL store_walrus() calls (raise SyntaxError).
		This is reported when examining any ITER expression in any comprehension.

After the Create phase is complete, these operations are valid:

	Note that Resolve phase will have been performed on all enclosing scopes.

	_closure_scope(var).  Looks for a closed scope in which var is Local (if any),
		including possibly the current scope itself.

		These are the _closure_scope rules:
		1.	An open scope returns its parent._closure_scope().
		2.	The global scope returns None.
		3.	A closed scope returns itself if var is Local,
			otherwise returns its parent._closure_scope().

	binding_scope(var).  Returns the binding scope for the var, if any.
		The binding scope might already be stored in the scope.
		If the binding scope exists, other than _unresolved_nonlocal, return it.
		Try calling _closure_scope(var).  If there is a value found, this is
			the binding scope.
		Otherwise it depends on the context of var:
			For Unresolved, then either raise a SyntaxError or leave it as Unresolved.
			Else the var is Seen or Unused.  Use the global scope as the binding scope, and
			perform load(var) on the global scope (which will make it a Top there).
		In all cases, except a SyntaxError of course, store the result as the binding scope.

	binding(var).  Returns the binding VarBind object for thevar, if any.
		It points to the binding scope.
"""

SrcT = TypeVar('SrcT')
ScopeT: TypeAlias = 'Scope[SrcT]'

_noarg: Final = object()				# Use as some argument default values.

# Singleton marker for nonlocal var whose nonlocal scope is not yet known.
_unresolved_nonlocal: Final = object()

class VarCtx(Enum):
	""" The current context of some Var name in a Scope.  It can change as the scope is building. """

	Unused = 0			# var does not appear at all
	Seen = auto()		# var appears in the scope but has no other information (so far)
	Local = auto()		# var is in current scope
	Closure = auto()	# var is in some closed scope, other than current
	Unresolved = auto()	# var is declared nonlocal, but the scope is not yet determined
	Global = auto()		# var is in global scope, which is not the current scope
	Walrus = auto()		# var is a walrus target in a comprehension or enclosed comprehension
	# Tests true if anything other than Unused.
	def __bool__(self): return bool(self.value)
	@property
	def is_used(self): return self is self.Seen
	@property
	def is_local(self): return self is self.Local
	@property
	def is_nonlocal(self): return self in (self.Closure, self.Unresolved)
	@property
	def is_global(self): return self is self.Global
	@property
	def is_top(self): return self is self.Top

class Scope(ScopeTree, Generic[SrcT]):
	is_scope: ClassVar[boo] = True
	name: str
	parent: Self | None
	global_scope: GlobalScope[SrcT] = None

	# Has the build completed?  Set False as an instance variable from the constructor
	# until the end of the build() context manager.  It prevents resolving vars.
	is_built: bool = True

	# Mapping of variable names to their binding scopes, for every var that appears in this scope.
	# The location may be self, or some enclosing scope.  It is determined at compile time.
	# The var is Local in its binding scope, which means that in that scope, the var is mapped to itself.
	# The binding scope may temporarily be unknown, but this is eventually resolved by the time the
	# entire scope has been built.
	vars: Mapping[str, VarBind | None]
	scope: Scope
	src: SrcT | None = None

	# Child Scopes, mapped by their src ids (which must be unique).
	nested: Mapping[int, ScopeT]
	@property
	def child_scopes(self) -> Iterable[ScopeT]: return self.nested.values()

	kind: ClassVar[Scope.Kind]

	# True if this Scope will allow walrus operators.
	#	Otherwise reject, with a SyntaxError, any walrus expression.
	# It is False as an instance attribute:
	#	1. Temporarily while examining any ITER in a comprehension.
	#		Accomplished with 'with comprehension.in_iterable: ...' statement.
	#	2. Always, when the scope was created if the flag was set in its parent at the time.
	#		Since the parent is an expression, this scope can only be a comprehension or a lambda.
	walrus_allowed: ClassVar[bool] = True

	# True to interpret a bind() as part of an assignment expression.
	in_walrus: ClassVar[bool] = False

	@attrs.define()
	class VarBind:
		""" Defines a binding of a variable name in a Scope, with some optional flags. """

		# Which Scope is this in.  None means a nonlocal variable whose closure is not known yet.
		scope: Scope | None

		anno: bool = False
		param: bool = False				# Variable is a function parameter
		nested: bool = False			# Variable is a nested tree
		
		def __repr__(self) -> str:
			if self.scope is None: return '(unresolved)'
			rep = repr(self.scope)
			if self.anno: rep += ' (anno)'
			if self.param: rep += ' (param)'
			if self.nested: rep += ' (nested)'
			return f'<{rep}>'

	@abstractmethod
	def __init__(self, src: SrcT, parent: Scope = None, name: str = '',
				 **_kwds):
		if not src: src = _EmptySrc()
		super().__init__(src, parent, name)
		self.global_scope = parent and parent.global_scope
		self.src = src
		self.scope = self
		self.vars = dict()
		self.nested = dict()
		if parent and not parent.walrus_allowed: self.walrus_allowed = False
		self.is_built = False

	@contextmanager
	def build(self) -> Iterable[Self]:
		if self.is_built:
			raise ValueError(f'Object {self!r} is already built')
		yield self			# perform building primitives in this context.
		if self.kind in (self.CLASS, self.FUNC):
			self.parent.bind(self.name, nested=True)
		self.is_built = True

	def qualname(self, varname: str = '', *, sep: str = '.') -> str:
		""" Fully qualified name of this scope, or given variable name in this scope.
		Optional separator to replace '.'.
		Global scope is part of this name only if it has its own name.
		"""
		names = list(self.scope_names)
		if varname: names.append(varname)
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

	def context(self, var: str) -> VarCtx:
		try: binding = self.vars[var]
		except KeyError: return VarCtx.Unused
		if not binding: return VarCtx.Seen
		scope = binding.scope
		if scope is self: return VarCtx.Local
		elif self.kind is self.COMP: return VarCtx.Walrus
		elif scope is self.global_scope: return VarCtx.Global
		else: return VarCtx.Closure

	def get(self, var: str) -> Scope | None:
		return self.vars.get(var)

	def use(self, var: str) -> None:
		""" Change from Unused to Seen, otherwise no change.
		"""
		# Unused -> Seen.
		self.vars.setdefault(var, None)

	def bind(self, var: str,
			anno: bool = False,
			param: bool = False,			# Variable is a function parameter
			nested: bool = False,			# Variable is a nested scope
			**kwds):

		binding = self.vars.get(var)
		if not binding:
			binding = self.vars[var] = self.VarBind(self)
		if anno: binding.anno = True
		if param: binding.param = True
		if nested: binding.nested = True

	def bind_walrus(self, var: str, **kwds) -> VarBind:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		Implemented differently in Class and Comprehension scopes.
		"""
		self.bind(var, **kwds)
		return self.vars[var]

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

	def decl_nonlocal(self, var: str) -> None:
		""" Declare the var as being nonlocal. """
		context = self.context(var)
		if not context:
			# Name Unused.  Change to Closure, but unresolved.
			# Search for actual nonlocal scope is done later in binding() method.
			self.vars[var] = self.VarBind(None)
			return
		# Only Closure is valid.
		if context.is_nonlocal:
			return
		elif context.is_global:
			# Global is an error.
			raise SyntaxError(f"var '{var}' is nonlocal and global")
		elif context.is_local:
			# Local is an error.  If annotated or parameter, this changes the message.
			if self.vars[var].param:
				raise SyntaxError(f"name '{var}' is parameter and nonlocal")
			elif self.vars[var].anno:
				raise SyntaxError(f"annotated name '{var}' can't be nonlocal")
			else:
				raise SyntaxError(f"name '{var}' is assigned to before nonlocal declaration")

	def decl_global(self, var: str) -> None:
		""" Declare the var as being global. """
		context = self.context(var)
		if not context:
			# Name Unused.  Change to Global.
			self.vars[var] = self.global_scope._make_binding(var)
			return
		# Only Global is valid.
		if context.is_global:
			return
		elif context.is_nonlocal:
			# Global is an error.
			raise SyntaxError(f"var '{var}' is nonlocal and global")
		elif context.is_local:
			# Local is an error.  If annotated or parameter, this changes the message.
			if self.vars[var].param:
				raise SyntaxError(f"name '{var}' is parameter and nonlocal")
			elif self.vars[var].anno:
				raise SyntaxError(f"annotated name '{var}' can't be nonlocal")
			else:
				raise SyntaxError(f"name '{var}' is assigned to before nonlocal declaration")

	def has_anno(self, var: str) -> bool:
		try: return var in self.annos
		except: return False		# self.annos not created yet.

	@contextmanager
	def nest(self, kind: Scope.Kind, src: SrcT = None, name: str = '', **kwds) -> Iterable[Scope]:
		""" Report a nested scope.  Create the Scope object.
		Report the name as assigned in the current scope, except for
			Lambda and Comprehension, which are anonymous.
		"""
		with super().nest(kind, src, name, **kwds) as result:
			src = result.src
			if id(src) in self.nested:
				raise ValueError(f'Duplicate src {src!r} for subscopes of {self!r}')
			self.nested[id(src)] = result
			yield result

	def cleanup(self) -> None:
		""" Resolve binding scope for all Seen and Closure variables, recursively. """
		var: str
		for var, binding in self.vars.items():
			if not binding or not binding.scope: self.binding(var, cacheit=True)
		for nested in self.nested.values():
			nested.cleanup()

	def child_scope(self, src: SrcT) -> ScopeT:
		""" Find the nested Scope having the given src. """
		return self.nested[id(src)]

	@property
	def child_scopes(self) -> Iterable[ScopeT]:
		return self.nested.values()

	def _make_binding(self, var: str) -> VarBind:
		""" Create a binding for var if it doesn't already exist.  Return the binding.
		In response to
		(1) self.bind(var), or 
		(2) in global scope if var resolves to here from an enclosed scope.
		"""
		binding = self.vars.get(var)
		if not binding:
			self.vars[var] = binding = self.VarBind(self)
		return binding

	# Methods after tree build is complete...

	@property
	def all_built(self) -> bool:
		""" Is this Scope and all enclosing Scopes all built? """
		return self.is_built and self.parent.all_built

	def binding(self, var: str, **kwds) -> VarBind | None:
		""" Tries to find the binding object for the var. """
		# Implemented differently in NestedScope, GlobalScope.
		raise NotImplementedError

	def binding_scope(self, var: str, **kwds) -> Scope | None:
		""" Tries to find the binding scope for the var. """
		return self.binding(var, **kwds).scope

class RootScope(Scope, kind=Scope.ROOT):
	""" Container for all the modules in a program.
	Will be created for a GlobalScope's parent if one is not provided to it.
	"""
	modules: Mapping[str, GlobalScope]

	all_built: bool = True

	#def __new__(cls, **kwds):
	#	return super().__new__(cls, Scope.ROOT)

	def __init__(self, *args, **kwds):
		super().__init__(None, *args, **kwds)
		self.modules = {}
		# Root scope is always considered built.
		del self.is_built
		self.all_built = True

	def add_module(self, var: str = '', **kwds) -> GlobalScope:
		result = self.nest_Global(var, **kwds)
		if var: self.modules[var] = result
		return result

class GlobalScope(Scope, kind=Scope.GLOB):
	parent: RootScope | None

	def __init__(self, src: SrcT, parent: RootScope = None, name: str = '', **kwds):
		super().__init__(src, parent or RootScope(), name, **kwds)
		self.global_scope = self
		if name:
			self.parent.modules[name] = self

	def decl_nonlocal(self, var: str) -> NoReturn:
		raise SyntaxError("nonlocal declaration not allowed at module level")

	def decl_global(self, var: str) -> VarBind:
		return self.make_binding(var)

	@contextmanager
	def build(self) -> Iterable[Self]:
		with super().build():
			yield self
		self.cleanup()

	def binding(self, var: str, **kwds) -> VarBind:
		""" Get the static scope for this var.  It is always self. """
		return self._make_binding(var)

	def _closure(self, _var: str) -> None:
		""" Get nearest enclosing ClosedScope for var, if any.  It is always None. """
		return None

	@property
	def scope_names(self) -> Iterator[str]:
		return []


class NestedScope(Scope):
	""" Any Scope other than GlobalScope or RootScope.  Subclasses are OpenScope and ClosedScope.
	"""
	parent: GlobalScope  # Cannot be None
	def __init__(self, *args, **kwds):
		super().__init__(*args, **kwds)

	def binding(self, var: str, cacheit: bool = False) -> VarBind:
		""" Find the binding.
		SyntaxError if var is still unresolved (i.e. nonlocal variable with no matching scope).
		"""
		if not self.all_built:
			raise ValueError(f'Cannot resolve names in scope {self!r} before it and all ancestors are built.')

		binding: VarBind | None = self.vars.get(var)
		if self.kind is self.COMP:
			if binding and binding.scope is not self:
				# Walrus.  Get from parent.
				return self.parent.binding(var)
		if binding and binding.scope:
			# Local, Closure, and Global.
			return binding
		# Look for a binding in an enclosing closed scope.
		closure = self._closure(var)
		if closure:
			# Make Closure.
			binding = closure
		else:
			if binding and not binding.scope:
				# Closure, no closure scope.  This is an error.
				raise SyntaxError(f"no binding for nonlocal '{var}' found")
			else:
				# Seen or Unused.  Make Global.
				binding = self.global_scope._make_binding(var)

		if cacheit: self.vars[var] = binding
		return binding

class OpenScope(NestedScope):

	def _closure_scope(self, var) -> ClosedScope | None:
		return self.parent._closure_scope(var)

	def _closure(self, var: str) -> VarBind | None:
		""" Get nearest enclosing ClosedScope for var, if any.  Never self.  """
		return self.parent._closure(var)

# For modules, exec and eval.  Provides a module name, otherwise unnecessary (??)
class ToplevelScope(Scope):
	parent: GlobalScope  # Cannot be None

	def __init__(self, parent: GlobalScope):
		super().__init__("<toplevel>", parent)


class ClassScope(OpenScope, kind=Scope.CLASS):

	def bind_walrus(self, var: str, **kwds) -> NoReturn:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		This is a syntax error.
		"""
		raise SyntaxError('assignment expression within a comprehension cannot be used in a class body')

class ClosedScope(NestedScope):
	def _closure_scope(self, var) -> ClosedScope | None:
		""" Change Unused to Seen.
		Return static scope if Local or Closure, None if Global, go to parent otherwise.
		"""
		context = self.context(var)
		if context is context.Global:
			return None
		elif context in (context.Local, context.Closure):
			return self.get(var)
		else:
			# Unused, Seen
			return self.parent._closure_scope(var)

	def _closure(self, var) -> VarBind | None:
		""" Get nearest enclosing ClosedScope, including self, for var, if any. """
		binding: VarBind | None = self.vars.get(var)
		if binding and binding.scope:
			# Local. Closure, or Global.
			if binding.scope.kind.is_closed:
				# This is it.
				return binding
			else:
				return None
		else:
			# Not here.  Try parent (recursively).
			return self.parent._closure(var)

class FunctionScope(ClosedScope, kind=Scope.FUNC):
	pass

class LambdaScope(FunctionScope, kind=Scope.LAMB):
	pass

class ComprehensionScope(FunctionScope, kind=Scope.COMP):
	is_comp: ClassVar[bool] = True

	# Note, bind(var) and bind_walrus(var) for the same var are contradictory, in either order
	# of occurence.  bind_walrus() may have bubbled up from a nested comprehension.
	# Either of these stores a binding in self.vars[var], but the binding is Local in the
	# first case and something else in the second case.`
	# The second of the two raises a SyntaxError.

	def bind(self, var: str, **kwds):
		""" Specialized bind() for Comprehensions, handles walrus differently.
		The bind() is delegated up to the first non-Comprehension enclosing scope.
		"""
		if self.in_walrus:
			self.bind_walrus(var)
		else:
			# Not a walrus.  Check for previous walrus binding.
			binding = self.vars.get(var)
			if binding and binding.scope is not self:
				raise SyntaxError(f"assignment expression cannot rebind comprehension iteration variable '{var}'")
			super().bind(var, **kwds)

	def bind_walrus(self, var: str) -> VarBind:
		""" Find or create binding for var in some enclosing scope, which originated in a comprehension.
		Defines a binding in this scope as well.
		SyntaxError if var is already Local
		"""
		binding = self.vars.get(var)
		if binding:
			if binding.scope is self:
				# Already seen as an iteration variable in this scope.
				raise SyntaxError(f"assignment expression cannot rebind comprehension iteration variable '{var}'")
		else:
			# Try the parent, recursively.
			binding = self.parent.bind_walrus(var)
			self.vars[var] = binding
		return binding

	@contextmanager
	def in_iterable(self):
		""" The body of the 'with in_iterable' statement is within the ITER in a
		'for target_list in ITER' clause.
		This makes all walrus expressions raise SyntaxErrors, including in nested
		comprehensions or lambdas.
		"""
		self.walrus_allowed = False
		yield
		del self.walrus_allowed

class _EmptySrc:
	count: int = 0
	def __init__(self):
		type(self).count += 1
		self.n = self.count

	def __repr__(self) -> str:
		return f'<no src {self.n}>'

def test():
	# Set up a sample program
	# class C:
	#   def foo(self, a = blah):
	#     global x
	#     x = a

	import treebuild
	print('testing scopes.py')
	root = RootScope()
	builder = treebuild.ScopeBuilder(root)
	with builder.nestGLOB(None, 'top') as g:
		with builder.nest(g.CLASS, None, 'C') as c:
			with builder.nestFUNC(None, 'foo') as foo:
				builder.bind('self')
				builder.bind('a', param=True)
				builder.use('a')
				builder.decl_global('x')
				builder.bind('x')
				with builder.nest(g.COMP, None, 'listcomp') as lc:
					with lc.use_walrus():
						builder.bind('w')

	assert foo.binding_scope("C") is g
	assert c.binding_scope("C") is g

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

	assert foo.binding_scope("w") is foo
	assert lc.binding_scope("w") is foo

if __name__ == "__main__":
	import scopes
	scopes.test()
