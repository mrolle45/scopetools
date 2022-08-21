""" Definitions used in common by modules in the scopetools package. """

from __future__ import annotations

from contextlib import contextmanager
from abc import *
from enum import *
from typing import Generic, TypeVar, Iterator

TreeT = TypeVar('TreeT')


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
	def nestGLOB(self, *args, _kind = _Kind.GLOB, **kwds) -> TreeT:
		return self.nest(_kind, *args, **kwds)
	def nestFUNC(self, *args, _kind = _Kind.FUNC, **kwds) -> TreeT:
		return self.nest(_kind, *args, **kwds)
	def nestCLASS(self, *args, _kind = _Kind.CLASS, **kwds) -> TreeT:
		return self.nest(_kind, *args, **kwds)
	def nestLAMB(self, *args, _kind = _Kind.LAMB, **kwds) -> TreeT:
		return self.nest(_kind, *args, **kwds)
	def nestCOMP(self, *args, _kind = _Kind.COMP, **kwds) -> TreeT:
		return self.nest(_kind, *args, **kwds)

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
	locals().update(Kind.__members__)


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

	def __init__(self, src: SrcT, parent: TreeT = None, name: str = '', kind: Kind = None, **kwds):
		self.is_built = False
		# If self.kind exists it must match kind.  Otherwise set self.kind
		try: assert self.kind is kind or kind is None, 'tree kinds don\'t match'
		except AttributeError: self.kind = kind

		assert parent != (kind is self.ROOT), 'tree parent required except for ROOT.'
		self.parent = parent

		if self.is_scope:
			self.scope = self
			if kind in (self.FUNC, self.CLASS):
				assert name, f'name required for {type(self).__name__} tree'
			self.name, self.src = name, src
		else:
			if self.parent:
				# Match the src to child of parent's scope.
				scope = self.scope = self.parent.scope.child_scope(src)
			else:
				# ROOT tree, needs corresponding ROOT scope...
				scope = self.scope
			self.name, self.src = scope.name, scope.src
			if name and name != self.name:
				raise ValueError(f'name {name!r} doesn\'t match {scope!r}.')

	# TREE BUILDING:

	# Build an object with
	#
	#	with obj:
	#		call building methods on obj...

	def __enter__(self) -> Self:
		return self

	def __exit__(self, exc_type, exc_value, traceback) -> None:
		if exc_type: return
		if self.parent: self.parent.nested.append(self)
		if self.kind in (self.CLASS, self.FUNC):
			self.parent.bind(self.name, nested=True)
			self.parent.store(self.name, self)

	@contextmanager
	def build(self) -> Self:
		""" Frames all building primitives, static and dynamic. """
		yield self			# Perform tree building primitives in this context.

	@contextmanager
	def nest(self, kind: Kind, src: SrcT, name: str = '', **kwds) -> TreeT:
		""" Creates a nested tree object, which is yielded.
		Caller does building methods in the context.
		Followed by assignment of a FUNC or CLASS to its name.
		"""
		newtree = self.tree_type(src, self, name, kind=kind, **kwds)
		with newtree.build(): yield newtree
		if kind in (self.CLASS, self.FUNC):
			self.bind(name)
			self.store(name, newtree)

	# STATIC PROPERTIES:

	# Building primitives.

	# These all supply some information about a particular var.
	# Some combinations of these will raise a SyntaxError
	# They are generally ignored except in Scope classes.

	def use(self, var: str, **kwds) -> None:
		""" A var which appears somewhere in this Scope, as a bare unannotated name. """
		
	def bind(self, var: str,
			 anno: bool = False,			# Variable is annotated
			 param: bool = False,			# Variable is a function parameter
			 nested: bool = False,			# Variable is a nested tree
			 walrus: bool = False,			# In (var := rvalue) expression,
											#	special behavior in comprehensions.
			 ):
		""" A var which appears in some binding operation.
		If var does not yet have a binding (it only has possibly been used), then 
		a binding is created in this scope and var becomes Local.
		Includes assignments, annotations (with or without a value), deletes, etc.
		iF walrus is true, in a comprehension, then the binding occurs in the first 
			non-comprehension enclosing scope, and may be a syntax error.
		"""

	@contextmanager
	def use_walrus(self):
		""" Any call in this context is a walrus operator.  Only matters in Scope. """
		yield

	def anno(self, var: str, anno, **kwds) -> None:
		""" Define an annotated variable, without an assigned value.  
		Default implementation is to bind it and ignore the annotation.
		"""
		self.bind(var)

	def decl_nonlocal(self, var: str, **kwds) -> None:
		""" Declare the var as being nonlocal. """

	def decl_global(self, var: str, **kwds) -> None:
		""" Declare the var as being global. """


	# DYNAMIC PROPERTIES:

	# These refer to current types or values of a variable at runtime.
	# They may be further modified both during and after building the tree.
	# Scope objects ignore these primitives.

	def store(self, var: str, value, **_kwds) -> None:
		pass

	def delete(self, var: str, **_kwds) -> None:
		pass

	def anno_assign(self, var: str, anno, rvalue: ValT, **kwds) -> None:
		""" Define an annotation and a value for var, as in 'var: anno = rvalue'. """
		# Default implementation is to do separate anno() and store().
		# Subclass may treat this as a single operation.
		self.anno(var, anno, **kwds)
		self.store(var, rvalue, **kwds)
	
	class ArgValue:
		""" A placeholder to represent the initial value of a function argument. """
		def __init__(self, name: str):
			self.name: Final[str] = name
		def __repr__(self) -> str:
			return f'<Arg {self.name}.'

	# NAME MANGLING:
	@staticmethod
	def mangle(var: str, class_name: str) -> str:
		""" Return the mangled version of a variable name in a scope of a given kind.
		Mostly returns same name.  In a CLASS scope, some names get changed.
		"""
		if kind is not kind.CLASS:
			return var
		if not var.startswith('__') or var.endswith('__'):
			return var
		# Create copy of scope class with given variable, then look at its locals.
		d = {}
		exec(f'''
		class {class_name}:
			__loc__ = set(locals())
			{var} = 0
			__loc__ = set(locals()) - __loc__
			__loc__.remove('__loc__')
		mangled = {class_name}.__loc__.pop()
		''',  d)
		return d['mangled']

	def __repr__(self) -> str:
		return f"{self.__class__.__qualname__}({self.name!r})"

class TreeRef(_NestMixin):
	""" Movable pointer to a tree or subtree.
	All attributes are delegated to the current tree.
	Optional iterator of SrcT's for nested trees.
	Current tree changed to a nested subtree by a context manager.
	"""
	curr: TreeT
	_nest_iter: Iterator[ScopeT] | None

	def __init__(self, curr: TreeT):
		self.curr = curr
		self._nest_iter = None

	def __getattr__(self, attr: str) -> Any:
		""" Delegate undefined attributes to the current tree. """
		try: return getattr(self.curr, attr)
		except AttributeError: return self.__getattribute__(attr)

	@contextmanager
	def nest(self, kind: _Kind, src: SrtT, *args, **kwds) -> Iterable[TreeT]:
		""" Create a nested tree and point to it during the context. """
		oldtree: TreeT = self.curr
		newtree: TreeT
		olditer: Iterator[SrcT] | None = self._nest_iter
		self._nest_iter = None
		if olditer:
			# Use the iterator to get src.  It should be == provided src.
			s = src
			src = next(olditer).src
			if s and s != src:
				raise ValueError(f'src {s!r} for nest() does not match next nested src {src!r}.')
		with self.curr.nest(kind, src, *args, **kwds) as newtree:
			self.curr = newtree
			yield newtree
		self.curr = oldtree
		self._nest_iter = olditer

	@contextmanager
	def use_scope_srcs(self) -> Iterable[Iterator[SrcT] | None]:
		""" In this context, all nest() calls will use consecutive src's from curr scope.
		Only happens in non-scope TreeT.  For scopes, do nothing and yield None.
		"""
		if self.curr.is_scope:
			yield None
			return
		save: Iterator[SrcT] | None = self._nest_iter
		self._nest_iter = iter(self.curr.scope.child_scopes)
		yield self._nest_iter
		self._nest_iter = save
