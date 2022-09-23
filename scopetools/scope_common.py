""" Definitions used in common by modules in the scopetools package. """

from __future__ import annotations

from contextlib import contextmanager
from abc import *
from enum import *
from typing import Generic, TypeVar, Iterator

import attrs

TreeT = TypeVar('TreeT')

NEW: Final[bool] = 0x01

class ScopeMeta(type):
	""" Metaclass for ScopeTree and its subclasses.
	Sets up kind-to-class lookup for new trees.
	"""

	def __new__(mcls, name, bases, namespace, **kwds):
		cls = type.__new__(mcls, name, bases, namespace)
		return cls

	def __init__(cls, name, bases, namespace, _root: bool = False, kind: ScopeTree.Kind = None, **kwds):
		""" Add kind => class mapping to the class. """
		# Do nothing for the root class
		if _root: return
		
		# If a direct base class, define tree_type and _kind_map.
		try: cls.tree_type
		except AttributeError:
			cls.tree_type = cls
			cls._kind_map = dict()
			return

		# If kind is provided, then register it.
		if kind and kind not in cls._kind_map:
			cls.kind = kind
			cls._kind_map[kind] = cls

class _Kind(Enum):
	""" Distinguishes the different kinds of scope which can be in the program.
	This includes the runtime environment which contains imported modules.
	"""
	ROOT = 'Root'				# Very top level, common to all modules.
								# Resolves names in the builtins module.
	GLOB = 'Global'				# Top level of a module.
	CLASS = 'Class'
	FUNC = 'Function'
	LAMB = 'Lambda'
	COMP = 'Comprehension'		# From a (List/Dict/Set)Comp or a GeneratorExp

	@property
	def is_root(self) -> bool: return self is self.ROOT
	@property
	def is_global(self) -> bool: return self is self.GLOB
	@property
	def is_class(self) -> bool: return self is self.CLASS
	@property
	def is_function(self) -> bool: return self is self.FUNC
	@property
	def is_lambda(self) -> bool: return self is self.LAMB
	@property
	def is_comp(self) -> bool: return self is self.COMP
	@property
	def is_closed(self) -> bool: return self in (self.FUNC, self.LAMB, self.COMP)

	def make_name(self, template: str = '%s') -> str:
		return template % self.value

	def __repr__(self): return self.name

class _NestMixin(Generic[TreeT]):
	""" Define nest_Module, etc. methods """
	from functools import partialmethod
	def nest2(self, *args, **kwds): return self.nest(*args, **kwds)
	nestGLOB = partialmethod(nest2, _Kind.GLOB)
	nestFUNC = partialmethod(nest2, _Kind.FUNC)
	nestCLASS = partialmethod(nest2, _Kind.CLASS)
	nestLAMB = partialmethod(nest2, _Kind.LAMB)
	nestCOMP = partialmethod(nest2, _Kind.COMP)

class ScopeTree(_NestMixin[TreeT], metaclass=ScopeMeta, _root = True):
	""" Common base class for Scopes, Namespaces, or other similar objects.
	Defines the building primitive methods, and some enumeration constants.
	"""
	is_scope: ClassVar[bool] = False

	# Has the build completed?  Set False as an instance variable from the constructor
	# until the end of the build() context manager.  It prevents resolving vars.
	is_built: bool = True

	name: str | NNone				# Name required for CLASS and FUNC, otherwise optional

	Kind = _Kind
	# Constants for above Kind members, copied into class variables
	for kind, x in Kind.__members__.items():
		exec(f'{kind} = {x}')

	# Index of self in parent.nested list (or None for ROOT)
	index: int | None

	def __new__(cls, *args, kind: Kind = None, **kwds):
		""" Factory for all tree objects.
		Use optional kind to determine actual class.
		"""
		assert hasattr(cls, 'tree_type'), f'{cls.__name__!r} class cannot be instantiated.'
		if kind:
			cls = cls._kind_map.get(kind, cls.tree_type)
		else:
			cls.kind				# Verify that cls.kind exists.
		return super().__new__(cls)

	def __init__(self, src: SrcT = None, parent: TreeT = None, name: str = '', *,
			index: int = None, kind: Kind = None, scope: ScopeT = None, **kwds):
		self.is_built = False
		# If self.kind exists it must match kind.  Otherwise set self.kind
		try: assert self.kind is kind or kind is None, 'tree kinds don\'t match'
		except AttributeError: self.kind = kind

		assert parent != (self.kind.is_root), 'tree parent required except for ROOT.'
		self.parent = parent
		if parent:
			if index is None: index = len(parent.nested)
			parent.nested.append(self)
			assert self.parent.nested[index] is self
		else:
			assert index is None
		self.index = index

		self.scope = scope
		if self.is_scope:
			if kind in (self.FUNC, self.CLASS):
				assert name, f'name required for {type(self).__name__} tree'
			self.name, self.src = name, src
		else:
			if not scope:
				# Make a Scope from other parameters.
				with parent.scope.nest(self.kind, src, name) as scope:
					self.scope = scope
			assert scope, f'Scope object required to initialize {type(self).__name__} tree'
			self.name, self.src = scope.name, scope.src
			if name and name != self.name:
				raise ValueError(f'name {name!r} doesn\'t match {scope!r}.')
		self.nested = []

	def __getattr__(self, name: str) -> Any:
		try:
			if self.scope is not self: return getattr(self.scope, name)
		except AttributeError: pass
		return self.__getattribute__(name)

	def search_scope(self, scope: Scope) -> TreeT:
		""" Find ancestor (or self) having given scope. """
		while self:
			if scope is self.scope: return self
			self = self.parent
		raise ValueError(f'No ancestor of {self!r} for scope {scope!r}')

	@property
	def root(self) -> TreeT:
		return self.parent and self.parent.root or self

	@property
	def glob(self) -> TreeT:
		parent = self.parent
		return parent and (parent and parent.glob or self)

	# DECORATORS

	# Decorator to mangle a variable name.
	# @mangler, or @mangler(var name) or @mangler(var position).

	def mangler(func: FuncT = None, *, var: str | int = 'var') -> FuncT:
		def actual_decorator(f):
			assert callable(f)
			from functools import wraps
			import inspect
			sig = inspect.signature(f)
			nonlocal var
			if isinstance(var, str):
				var = list(sig.parameters).index(var)
			def fix_args(args) -> list:
				self = args[0]
				# If the arg is missing, assume it defaults to ''.
				try:
					name = args[var]
					name2 = self.mangle(name)
					if name != name2:
						args = list(args)
						args[var] = name2
				except IndexError: pass
				return args

			@wraps(f)
			def wrapper(*args, **kwargs):
				# Do stuff with var here...
				args = fix_args(args)
				return f(*args, **kwargs)
			return wrapper
		if func:
			return actual_decorator(func)
		return actual_decorator
	
	# Decorator to dispatch type comment separately.
	def has_type_comment(func: FuncT = None, *, var: str | int = 'var') -> FuncT:
		def actual_decorator(f):
			assert callable(f)
			from functools import wraps
			import inspect
			sig = inspect.signature(f)
			nonlocal var
			if isinstance(var, str):
				var = list(sig.parameters).index(var)
			@wraps(func)
			def wrapper(*args, **kwargs):
				# Do stuff with type comment here...
				self = args[0]
				name = args[var]
				# Separate out the type_comment.
				comm = kwargs.pop('type_comment', '')
				if comm:
					self.type_hint(name, comm)
				return func(*args, **kwargs)
			return wrapper
		if func:
			return actual_decorator(func)
		return actual_decorator

	# TREE BUILDING:

	@contextmanager
	def build(self) -> Self:
		""" Frames all building primitives, static and dynamic. """
		yield self			# Perform tree building primitives in this context.

	@contextmanager
	@mangler(var='name')
	def nest(self, kind: Kind, src: SrcT, name: str = '', index: int = None, **kwds) -> Iterable[TreeT]:
		""" Finds or creates a nested tree object, which is yielded.
		Caller does building methods in the context.
		Followed by assignment of a FUNC or CLASS to its name.
		"""
		if self.is_built and self.parent:
			newtree = self.nested[index]
			yield newtree
		else:
			newtree = self.tree_type(src, self, name, kind=kind, index=index, **kwds)
			with newtree.build(): yield newtree
		if kind in (self.CLASS, self.FUNC):
			self.bind(name)
			self.store(name, newtree)

	def add_nested(self) -> None:
		""" Create nested trees at all levels, parallel with self.scope.
		Ignored for Scope trees.
		"""
		if self.is_scope: return
		for scope in self.scope.nested:
			sub = self.tree_type(scope.src, self, kind=scope.kind, scope=scope)
			sub.add_nested()
		del self.is_built

	# STATIC PROPERTIES:

	# Building primitives.

	# These all supply some information about a particular var.
	# Some combinations of these will raise a SyntaxError
	# They are generally ignored except in Scope classes.

	def use(self, var: str, **kwds) -> None:
		""" A var which appears somewhere in this Scope, as a bare unannotated name. """
		return
	
	def bind(self, var: str,
			 **kwds) -> None:
		""" A var which appears in some binding operation.
		"""
		return

	@contextmanager
	def use_walrus(self):
		""" Any call in this context is a walrus operator.  Only matters in Scope. """
		yield

	def decl_nonlocal(self, var: str, **kwds) -> None:
		""" Declare the var as being nonlocal. """
		return

	def decl_global(self, var: str, **kwds) -> None:
		""" Declare the var as being global. """
		return


	# DYNAMIC PROPERTIES:

	# These refer to current types or values of a variable at runtime.
	# They may be further modified both during and after building the tree.
	# Scope objects ignore these primitives.

	def store(self, var: str, value, **_kwds) -> None:
		return

	def delete(self, var: str, **_kwds) -> None:
		return

	class ArgValue:
		""" A placeholder to represent the initial value of a function argument. """
		def __init__(self, name: str):
			self.name: Final[str] = name
		def __repr__(self) -> str:
			return f'<Arg {self.name}.'

	# TYPING PROPERTIES

	def type_hint(self, var: str, typ: str, **kwds) -> None:
		pass

	# COMPOUND EVENTS

	def anno(self, var: str, anno: str, **kwds) -> None:
		self.bind(var, self.ANNO, **kwds)
		self.type_hint(var, anno, **kwds)

	def anno_store(self, var: str, anno: str, rvalue: ValT, **kwds) -> None:
		""" Define an annotation and a value for var, as in 'var: anno = rvalue'. """
		# Default implementation is to do separate anno() and store().
		# Subclass may treat this as a single operation.
		self.anno(var, anno, **kwds)
		self.store(var, rvalue, **kwds)
	
	# NAME MANGLING:
	def class_tree(self, _class_kind = Kind.CLASS, _glob_root_kind = (Kind.GLOB, Kind.ROOT)
			) -> TreeT | None:
		""" Look for a CLASS tree in the parent chain. """
		if self.kind is _class_kind: return self
		if self.kind in _glob_root_kind: return None
		return self.parent.class_tree()

	def mangle(self, var: str) -> str:
		""" Return the mangled version of a variable name in a scope of a given kind.
		Mostly returns same name.  In a CLASS scope, some names get changed.
		"""
		# Most common case: the name is not private.
		if not var.startswith('__') or var.endswith('__'):
			return var
		class_tree = self.class_tree()
		if not class_tree:
			return var
		return mangle(class_tree.name, var)

	@mangler
	def f(self, var): print(var); return var

	@mangler(var='foo')
	def g(self, foo): print(foo); return foo

	@mangler
	@has_type_comment
	def h(self, var, *, type_comment: bool = ''): print(var); return var

	def __repr__(self) -> str:
		return f"{self.__class__.__qualname__}({self.name!r})"

class TreeRef(_NestMixin):
	""" Movable pointer to a tree or subtree.
	All attributes are delegated to the current tree.
	Optional iterator of SrcT's for nested trees.
	Current tree changed to a nested subtree by a context manager.
	"""
	curr: TreeT
	state: State

	def __init__(self, curr: TreeT):
		self.curr = curr
		self.state = self.State(curr)

	def __getattr__(self, attr: str) -> Any:
		""" Delegate undefined attributes to the current tree. """
		try: return getattr(self.curr, attr)
		except AttributeError: return self.__getattribute__(attr)

	@contextmanager
	def nest(self, kind: _Kind, src: SrcT, *args, scope: ScopeT = None, **kwds) -> Iterable[TreeT]:
		""" Create a nested tree and point to it during the context. """
		oldstate = self.state
		scope = None
		with self.curr.nest(kind, src, *args, scope=scope, index=oldstate.nest_count, **kwds) as newtree:
			self.curr = newtree
			self.state = self.State(newtree)
			yield newtree
			oldstate.nest_count += 1
		self.curr = oldstate.curr
		self.state = oldstate

	@contextmanager
	def use_parent(self) -> None:
		save, self.curr = self.curr, self.curr.parent
		assert self.curr, f'No parent for {save!r}.'
		yield
		self.curr = save

	@attrs.define
	class State:
		curr: TreeT
		nest_count: int = 0

def mangle(clsname: str, var: str) -> str:
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

