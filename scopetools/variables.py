""" variables.py.

Classes pertaining to a variable in a Python program.
"""

from __future__ import annotations

from enum import *
import attrs

ManglerT: TypeAlias = 'ScopeTree | TreeRef'
MangledT: TypeAlias = 'tuple[str, ClassScope | None]'

class VarName(str):
	""" Name of the variable, with built-in name mangling.
	Can be used as an ordinary str, but str cannot be used as a VarName.
	"""
	mangled: VarMangle = None		# Set only if name was mangled.

	def __new__(cls, name: str, mangler: ManglerT = None):
		if type(name) is cls:
			return name
		if mangler:
			# Mangle the name.
			private = name
			name, class_owner = mangler.mangle(name)
			if class_owner:
				self = str.__new__(cls, name)
				self.mangled = VarMangle(private, class_owner)
				return self
		return str.__new__(cls, name)

	def unmangle(self, mangler: ManglerT = None) -> str:
		if self.mangled:
			if not mangler or _class_owner(mangler) is self.mangled.mangler:
				return self.mangled.private
		return self

	def __repr__(self) -> str:
		if self.mangled:
			return f'{self} ({self.mangled!r})'
		else:
			return self

class VarCtx(Flag):
	""" Flag bits indicating how a variable occurs in a scope. """

	# How the name appears in the scope code.
	# These are accumulated from individual appearances while building a Scope.
	# Some combinations are not allowed, or allowed in restricted sequence:
	#	GLOB_DECL and NLOC_DECL cannot follow any of the other bits, nor each other.
	#	BINDING | WALRUS cannot be followed by BINDING without WALRUS.
	UNUSED = 0				# Doesn't appear anywhere.  Default result for scope.context().
	GLOB_DECL = auto()		# Global declaration.
							# In GLOB, includes a global declaration in any nested scope.
	NLOC_DECL = auto()		# nonlocal declaration
	EXTERN_BIND = NLOC_DECL | GLOB_DECL
	ANNO = auto()			# an annotated name, via 'x: type' statement, not 'x: type' parameter.
	BINDING = auto()		# some binding reference, other than the above
	USE = auto()			# none of the above, a value reference.
	WALRUS = auto()			# a walrus target in an owned COMP, possibly with BINDING.
							# this is to prevent also being BINDING without WALRUS.
	USAGE = UNUSED | GLOB_DECL | NLOC_DECL | BINDING | USE | WALRUS


	@property
	def usage(self) -> Literal[VarCtx.GLOB_DECL, VarCtx.NLOC_DECL,
						  VarCtx.BINDING, VarCtx.USE]:
		return self & self.USAGE

	def with_usage(self, usage: Self) -> Self:
		""" New VarCtx with usage replaced by new usage. """
		return self & ~self.USAGE | usage

	# Kinds of binding operations seen.  May be combined with each other.
	# Only combined with BINDING...
	PARAM = auto()			# a function parameter
	NESTED = auto()			# a nested scope.
	IMPORT = auto()			# an imported name
	BINDFLAGS = ANNO | PARAM | NESTED | IMPORT

	# Where resolved...
	# Mutually exclusive, except
	#	in GLOB scope where LOCAL and GLOBAL come together.
	LOCAL = auto()			# the scope itself
	GLOBAL = auto()			# the global scope
	FREE = auto()			# an ancestor closed scope
	CELL = auto()			# same as FREE, but also in CLOS, if captured by any scope in subtree.
	UNRES = auto()			# none found (a NLOC_DECL with no matching scope)
	TYPES = LOCAL | GLOBAL | FREE | CELL | UNRES

	@property
	def type(self) -> Literal[VarCtx.LOCAL, VarCtx.GLOBAL, VarCtx.FREE, VarCtx.UNRES]:
		return self & self.TYPES

	INLOCALS = CELL | LOCAL	# Eligible for inclusion in locals() in this scope.
							# Runtime value is parent value if it is bound there,
							#	otherwise unbound.

	def raise_err(self, var: str, plus: VarCtx = None) -> None:
		""" Raise a SyntaxError for some illegal combinations of flags. """
		if plus: self |= plus
		if self & self.GLOB_DECL:
			if self & self.NLOC_DECL:
				raise SyntaxError(f"var '{var}' is nonlocal and global")
			s = 'global'
		elif self & self.NLOC_DECL:
			s = 'nonlocal'
		else:
			s = ''

		if s:
			# global or nonlocal is an error.  If annotated or parameter, this changes the message.
			if self & self.PARAM:
				raise SyntaxError(f"name '{var}' is parameter and {s}")
			elif self & self.ANNO:
				raise SyntaxError(f"annotated name '{var}' can't be {s}")
			else:
				raise SyntaxError(f"name '{var}' is assigned to before {s} declaration")

		if plus & self.WALRUS:
			raise SyntaxError(f"assignment expression cannot rebind comprehension iteration variable '{var}'")

	def __repr__(self) -> str:
		return str(self).split('.')[1]

@attrs.define
class VarUse:
	""" How the variable is used in the current scope.
	This is different from how it is resolved (which is in self.binding)
	The same name can be in different scopes and resolve to the same binding,
	each with its own context.
	"""
		
	binding: Variable			# Where var is resolved.
	ctx: VarCtx

	# Convenience access to test for or set or unset self.ctx values.
	# As in self.getXXX() -> new VarCtx with just the bits of XXX from self.ctx
	#	and self.hasXXX() -> true if any the bits of XXX are in self.ctx
	#	and self.setXXX() -> set the bits of XXX in self.ctx, return self
	#	and self.clrXXX() -> clear the bits of XXX in self.ctx, return self
	for name, ctx in VarCtx.__members__.items():
		exec(f'def get{name}(self, v = {ctx}) -> VarCtx: return self.ctx & v')
		exec(f'def has{name}(self, v = {ctx}) -> bool: return bool(self.ctx & v)')
		exec(f'def set{name}(self, v = {ctx}) -> VarUse: self.ctx |= v; return self')
		exec(f'def clr{name}(self, v = {ctx}) -> VarUse: self.ctx &= ~v; return self')
	del name

	def set_usage(self, usage: VarCtx) -> None:
		self.ctx = self.ctx.with_usage(usage)

	@property
	def binding_scope(self) -> Scope | None:
		if self.binding:
			return self.binding.binder.scope
		else:
			return None

	def __repr__(self) -> str:
		if self.binding:
			return f'{self.ctx!r} {self.binding!r}'
		else:
			return f'{self.ctx!r} (unresolved)'

@attrs.define(frozen=True)
class Variable:
	""" A unique variable in the program.
	Name (mangled, perhaps) and binder table.
	The binder maps the unique objects by name.
	"""
	name: VarName
	binder: VarBinder

	def __repr__(self) -> str:
		return f'{self.name} in {self.binder.scope.qualname()}'

class VarBinder:
	""" Keeps unique Variable objects indexed by their names.
	Used by a particular Scope to keep those Variables bound to that scope.
	"""
	scope: Scope
	vars: dict[VarName, Variable] = dict()

	def __init__(self, scope: Scope):
		self.scope = scope
		self.vars = {}

	def __getitem__(self, name: VarName) -> Variable:
		try: return self.vars[name]
		except KeyError: pass
		var = self.vars[name] = Variable(name, self)
		return var

# For mangling private names...

@attrs.define(frozen=True)
class VarMangle:
	""" A mangled name.  Gives the original (private) name and the mangler class. """
	private: str
	mangler: ClassScope

	def __repr__(self) -> str:
		return f'{self.mangler.name}.{self.private}'

def mangle(var: str, scope: ScopeTree) -> MangledT:
	""" Return the mangled version of a variable name in this scope.
	Mostly returns same name.
	"""
	# Most common case: the name is not private.
	if var.startswith('__') and not var.endswith('__'):
		class_owner = _class_owner(scope)
		if class_owner:
			return _mangle(var, class_owner.name), class_owner.scope
	return var, None

def _mangle_args(args: tuple, pos: int = 1) -> list:
	""" Mangles one of the given args, using args[0] as the mangler.
	Returns the args with the mangled arg in place of the original.
	If there aren't enough args, returns the args unchanged.
	"""
	try: name = args[pos]
	except IndexError: return list(args)
	if type(name) is VarName: return list(args)
	newargs = list(args)
	newargs[pos] = VarName(name, newargs[0])
	return newargs

def var_mangle(func: FuncT = None, *, var: str | int = 'name') -> FuncT:
	""" Decorator for any function which expects a mangled name for one of its arguments.
	The wrapper function mangles the variable name and then calls the function.
	The decorator has an optional (var=param number or param name) that tells
	which parameter is to be mangled.  By default, it is parameter 'name'.
	Parameter 0 is always the ScopeTree which supplies the class name.
	If the name parameter is missing, the default value will be used.
	"""
	def actual_decorator(f: FuncT):
		assert callable(f)
		from functools import wraps
		from scope_common import ScopeTree, TreeRef
		nonlocal var
		if isinstance(var, str):
			import inspect
			sig = inspect.signature(f)
			var = list(sig.parameters).index(var)
		#def fix_args(args) -> list:
		#	""" Mangles the given param in args and returns new args list. """
		#	newargs = list(args)
		#	try: name = newargs[var]
		#	except IndexError: return newargs
		#	if type(name) is VarName: return newargs
		#	assert isinstance(name, str)
		#	self = newargs[0]
		#	newargs[var] = VarName(name, self)
		#	return newargs

		@wraps(func)
		def wrapper(*args, **kwargs):
			newargs: list = _mangle_args(args, var)
			return func(*newargs, **kwargs)
		return wrapper

	if func:
		return actual_decorator(func)
	return actual_decorator

def _class_owner(scope: Scope) -> ClassScope | None:
	class_owner = scope
	while class_owner:
		if class_owner.kind.is_class:
			return class_owner
		class_owner = class_owner.parent
	return None

def _mangle(var: str, clsname: str) -> str:
	""" Return the mangled version of a variable name in a CLASS owner scope.
	Mostly returns same name.
	"""
	# Create copy of scope class with given variable, then look at its locals.
	d = {}
	exec(
f'''
class {clsname}:
	__loc__ = set(locals())
	{var} = 0
	__loc__ = set(locals()) - __loc__
	__loc__.remove('__loc__')
mangled = {clsname}.__loc__.pop()
''',
		d)
	return d['mangled']

