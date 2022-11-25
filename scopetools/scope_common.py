""" Definitions used in common by modules in the scopetools package. """

from __future__ import annotations

from contextlib import contextmanager
from abc import *
from enum import *
from typing import Generic, TypeVar, Iterator

import attrs

from .variables import *

TreeT = TypeVar('TreeT')

NEW: Final[bool] = 0x01

class ScopeMeta(type):
	""" Metaclass for ScopeTree and its subclasses.
	Sets up kind-to-class lookup for new trees.
	"""

	def __new__(mcls, name, bases, ns, **kwds):
		cls = type.__new__(mcls, name, bases, ns)
		return cls

	def __init__(cls, name, bases, ns, _root: bool = False, kind: ScopeTree.Kind = None, **kwds):
		""" Add kind => class mapping to the class. """
		# Do nothing for the root class
		if _root: return
		
		# If a direct base class, define tree_type, _kind_map and isKIND() tests.
		try: cls.tree_type
		except AttributeError:
			cls.tree_type = cls
			cls._kind_map = dict()
			#for name, x in ScopeKind.__members__.items():
			#	kind_name = x.make_name(f"%s{cls.__name__}")
			#	exec(	f'def is{name}(self) -> bool:\n'
			#			f'\treturn isinstance(self, {kind_name})\n'
			#			f'cls.is{name} = is{name}')
			return

		# If kind is provided, then register it.
		if kind and kind not in cls._kind_map:
			cls.kind = kind
			cls._kind_map[kind] = cls
			test = lambda self: isinstance(self, cls)
			setattr(cls.tree_type, f'is{kind.name}', test)

class ScopeKind(Enum):
	""" Distinguishes the different kinds of scope which can be in the program.
	This includes the runtime environment which contains imported modules.
	"""
	ROOT = 'Root'				# Very top level, common to all modules.
								# Resolves names in the builtins module.
	GLOB = 'Global'				# Top level of a module.
	CLASS = 'Class'
	FUNC = 'Function'
	LAMB = 'Lambda'
	COMP = 'Comprehension'		# From a (List/Dict/Set)Comp or a GeneratorExp.
	EVEX = 'ExecEval'			# Source for exec() or eval() call, not specified which .
	EXEC = 'Exec'				# Source for exec() call.
	EVAL = 'Eval'				# Source for eval() call.
	LOCS = 'Locals'				# Evaluates locals() call.  No source.
	OPEN = 'Open'
	CLOS = 'Closed'

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
	def is_closed(self) -> bool: return self in (self.CLOS, self.FUNC, self.LAMB, self.COMP)
	@property
	def is_open(self) -> bool: return self not in (self.CLOS, self.FUNC, self.LAMB, self.COMP)

	def make_name(self, template: str = '%s') -> str:
		return template % self.value

	def __repr__(self): return self.name

class _NestMixin(Generic[TreeT]): 
	""" Define nestROOT(), etc. methods """
	from functools import partialmethod
	def nest2(self, *args, **kwds): return self.nest(*args, **kwds)
	for name, k in ScopeKind.__members__.items():
		exec(f'def nest{name}(self, *args, **kwds): return self.nest({k}, *args, **kwds)')
	del name, k

class ScopeTree(_NestMixin[TreeT], metaclass=ScopeMeta, _root = True):
	""" Common base class for Scopes, Namespaces, or other similar objects.
	Defines the building primitive methods, and some enumeration constants.
	"""
	is_scope: ClassVar[bool] = False

	# Has the build completed?  Set False as an instance variable from the constructor
	# until the end of the build() context manager.  It prevents resolving vars.
	is_built: bool = True

	name: str | NNone				# Name required for CLASS and FUNC, otherwise optional

	Kind = ScopeKind
	#kind: Kind = None

	# Constants for above Kind members, copied into class methods
	#	and corresponding isinstance() tests.
	for k, x in Kind.__members__.items():
		exec(	f'@staticmethod\n'
				f'def {k}():\n'
				f'\treturn {x}')
	del x, k

	# Index of self in parent.nested list (or None for ROOT or if not in the list)
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
			index: int = None, kind: Kind = None, scope: ScopeT = None,
			with_index: bool = True, **kwds):
		self.is_built = False
		self.scope = scope
		# If self.kind exists it must match kind.  Otherwise set self.kind
		if hasattr(self, 'kind'): assert self.kind is kind or kind is None, 'tree kinds don\'t match'
		else: self.kind = kind

		assert parent != (self.isROOT()), 'tree parent required except for ROOT.'
		self.parent = parent
		if parent:
			if with_index:
				if index is None:
					index = len(parent.nested)
				if index == len(parent.nested):
					parent.nested.append(self)
				assert self.parent.nested[index] is self
		else:
			assert index is None
		self.index = index

		if self.is_scope:
			if kind in (self.FUNC, self.CLASS):
				assert name, f'name required for {type(self).__name__} tree'
			self.name, self.src = name, src
		else:
			if not scope:
				# Make a Scope from other parameters.
				with parent.scope.nest(self.kind, src, name, with_index=with_index) as scope:
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
	def nest(self, kind: Kind, src: SrcT, name: str = '', index: int = None, with_index: bool = True, **kwds) -> Iterable[TreeT]:
		""" Finds or creates a nested tree object, which is yielded.
		Caller does building methods in the context.
		Followed by assignment of a FUNC or CLASS to its name.
		"""
		if self.is_built and self.parent and index is not None and with_index:
			newtree = self.nested[index]
			yield newtree
		else:
			newtree = self.tree_type(
				src, self, name, kind=kind, index=index, with_index=with_index, **kwds)
			with newtree.build(): yield newtree
		if newtree.isCLASS() or newtree.isFUNC():
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

	def use(self, name: VarName, **kwds) -> None:
		""" A var which appears somewhere in this Scope, as a bare unannotated name. """
		return
	
	def bind(self, name: VarName,
			flags: VarCtx = VarCtx(0),
			**kwds):
		""" A var which appears in some binding operation.
		"""
		return

	@contextmanager
	def use_walrus(self):
		""" Any call in this context is a walrus operator.  Only matters in Scope. """
		yield

	def decl_nonlocal(self, name: VarName, **kwds) -> None:
		""" Declare the var as being nonlocal. """
		return

	def decl_global(self, name: VarName, **kwds) -> None:
		""" Declare the var as being global. """
		return


	# DYNAMIC PROPERTIES:

	# These refer to current types or values of a variable at runtime.
	# They may be further modified both during and after building the tree.
	# Scope objects ignore these primitives.

	def load(self, name: VarName) -> ValT:
		return None

	def store(self, name: VarName, value, **_kwds) -> None:
		return

	def delete(self, name: VarName, **_kwds) -> None:
		return

	class ArgValue:
		""" A placeholder to represent the initial value of a function argument. """
		def __init__(self, name: VarName):
			self.name: Final[str] = name
		def __repr__(self) -> str:
			return f'<Arg {self.name}.'

	# TYPING PROPERTIES

	@var_mangle
	def type_hint(self, name: VarName, typ: str, **kwds) -> None:
		pass

	# COMPOUND EVENTS

	@var_mangle
	def anno(self, name: VarName, anno: str, **kwds) -> None:
		self.bind(name, VarCtx.ANNO, **kwds)
		self.type_hint(name, anno, **kwds)

	@var_mangle
	def anno_store(self, name: VarName, anno: str, rvalue: ValT, **kwds) -> None:
		""" Define an annotation and a value for var, as in 'var: anno = rvalue'. """
		# Default implementation is to do separate anno() and store().
		# Subclass may treat this as a single operation.
		self.anno(name, anno, **kwds)
		self.store(name, rvalue, **kwds)

	# OTHER METHODS

	def nest_depth(self) -> int:
		depth = 0
		while self.parent:
			depth += 1
			self = self.parent
		return depth
	
	def mangle(self, name: str) -> MangledT:
		""" Return the mangled version of a variable name in this scope.
		Mostly returns same name.
		"""
		# Most common case: the name is not private.
		if name.startswith('__') and not name.endswith('__'):
			return mangle(name, self)
		return name, None

	def __repr__(self) -> str:
		return f"{self.__class__.__qualname__}({self.name!r})"

class ProxyMeta(type):
	""" Metaclass for ScopeTreeProxy and its subclasses.
	Sets up kind-to-class lookup for new trees.
	Switches all methods with a method.mangler to call method.mangler instead.
	"""

	def __new__(mcls, name, bases, ns, **kwds):
		""" Change methods to their mangler versions where they exist. """
		for key, func in ns.items():
			try: ns[key] = func.mangler
			except AttributeError: pass
		return super().__new__(mcls, name, bases, ns, **kwds)

class ScopeTreeProxy(_NestMixin, metaclass=ProxyMeta):
	""" Movable pointer to a tree or subtree.
	All attributes are delegated to the current tree.  
	If a method has a '{method}.mangler' member, then proxy.{method} calls proxy.curr.{method}.mangler.

	This should be used for all accesses to a ScopeTree from something that is not a ScopeTree.

	It's OK to directly get a Tree attribute if it doesn't involve mangling of a private name.
	Or explicitly request `tree.{method}.mangled` attribute.

	For a method defined on a Proxy subclass, the mangler method is substituted for the
	method name by the @var_mangle decorator.

	"""
	curr: TreeT
	state: State

	def __init__(self, curr: TreeT):
		self.curr = curr
		self.state = self.State(curr)

	def __getattr__(self, attr: str) -> Any:
		""" Delegate undefined attributes to the current tree.
		Will use mangled version if found either here or in the current tree.
		"""
		try: attr = getattr(self.curr, attr)
		except AttributeError: return self.__getattribute__(attr)	# Will raise correct error.
		import functools
		try: return functools.partial(attr.mangler, attr.__self__)

		#try: return attr.mangler
		except AttributeError: pass
		return attr

	def mangle(self, name: str) -> MangledT:
		""" Return the mangled version of a variable name in this scope.
		Mostly returns same name.
		"""
		# Most common case: the name is not private.
		if name.startswith('__') and not name.endswith('__'):
			return mangle(name, self.curr.scope)
		return name, None

	@contextmanager
	def nest(self, kind: _Kind, src: SrcT, name: str, *args, scope: ScopeT = None, **kwds) -> Iterable[TreeT]:
		""" Create a nested tree and point to it during the context.
		Mangle the nested tree name (if given) within the current tree.
		"""
		oldstate = self.state
		oldtree = self.curr
		mangled = VarName(name, oldtree)
		with oldtree.nest(kind, src, mangled, *args, scope=scope, index=oldstate.nest_count, **kwds) as newtree:
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

