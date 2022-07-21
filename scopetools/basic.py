""" Definitions used in common by modules in the scopetools package. """

from __future__ import annotations

from contextlib import contextmanager
from abc import *
from enum import *

class Basic:
	""" Common base class for Scopes, Namespaces, or other similar objects.
	Defines the building primitive methods, and some enumeration constants.
	"""

	class Kind(Enum):
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

	# Constants for above Kind members, copied into class variables
	locals().update(Kind.__members__)

	def __init__(self, *args, **kwds):
		self.is_built = False

	# TREE BUILDING:

	@contextmanager
	def build(self) -> Self:
		""" Frames all building primitives, static and dynamic. """
		yield self			# Perform tree building primitives in this context.

	@contextmanager
	def nest(self, kind: Kind, name: str = '', **kwds) -> TreeT:
		""" Creates a nested tree object, which is yielded.
		In the context, tree building primitives are called.
		A function or class name is bound in the current (not nested) tree.
		"""
		newtree = self._make_nest(kind, name, **kwds)
		with self.build(): yield newtree
		if kind in (self.CLASS, self.FUNC):
			self.bind(name)

	def nest_func(self, name: str, **kwds) -> Generator:
		return self.nest(self.FUNC, name, **kwds)
	def nest_cls(self, name: str, **kwds) -> Generator:
		return self.nest(self.CLASS, name, **kwds)

	@abstractmethod
	def _make_nest(self, kind, name: str = '', **kwds) -> TreeT:
		""" Create the new tree. """

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

	def nonlocal_stmt(self, var: str, **kwds) -> None:
		""" Declare the var as being nonlocal. """

	def global_stmt(self, var: str, **kwds) -> None:
		""" Declare the var as being add_global. """


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


