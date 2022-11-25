"""
A Target is an abstraction for something that can hold a value (or not).
It is referred to in the Python Language doc as a "target".
It corresponds to something that can appear in a program as:

1.	target = [target = ]* rvalue
	Corresponds to the operation store(target, rvalue), for each target
2.	del target
	Corresponds to the operation delete(target).
3.	target (as an expression other than either of the above)
	Correponds to the operation load(target).

The AST for the target, and targets nested within it, indicates the context as
	Store(), Delte(), or Load(), respectively.

The environment:

	There is an environment object in which operations on Targets are performed.
	The function of the environment is to dynamically supply values, bind values,
	or unbind values, for any given variable name.

Subclasses of Target are Vector, Starred, and Scalar.

A Vector represents a sequence of other targets, such as in
	a, *b, c = 1, 2.  a, *b, and c are elements of the vector.
The '*' is optional, and is indicated by a Starred target.
If a store is being performed, then at most one Starred target is
allowed in a single Vector.  A standalone *x is not allowed in the Python grammar.

In a function call, the list of positional arguments will be represented as a Vector.

A Starred object represents '*x' as an element of a Vector.  'x' is given as another Target.

The other types of targets are derived from a Scalar.  A Scalar has
1. A primary object.
2. A key.
The container and key have different meanings and types in different subclasses.
All operations are delegated to the primary using the key.

Name: Primary is the Environment, and key is a variable name.

Attribute: Primary is, or represents, a python object which supports attribute operations
as required by the context.  Key is an attribute name.

Subscript: Primary is, or represents, a python object which supports subscripted operations
as required by the context.  Key is, or represents, a Python object for the subscript.

A Target performs these operations:

1. Load.  Evaluates the Target, returning a value or values.

2. Delete.  Removes the value(s) stored in the Target.

3. Store.  Stores a given rvalue in the Target.

4. Augmented Store.  Similar to a store, except there is an operator supplied as well.
It corresponds to, for example,
	target += rvalue
The operator is callable(left, right) -> result.
For the above example, if the values are actual Python runtime objects, then
	def operator(left, right): left += right; return left
Only allowed by Scalars.
It is performed as follows:
	1. Get value = target.load().
	2. Calculate result of operator(value, rvalue).  This could be the same object as value, if it
		supports in-place operation.
	3. Call target.store(result)

5. Store Expr (i.e. walrus).  Similar to Store, where the target is a Name.  It differs only in the
	external location where the store is performed.  The target must appear by itself.

Env class:

This is needed to perform any operation on any Target.  It has a reference to the abstract environment.
Typically, the client application needs only one Env object.  The Env can be modified by
target operations, and also by the client itself (such as switching to use a different ns).

Through subclassing, the behavior can be customized:

1. How an iterable rvalue is unpacked into an iterable of rvalues,
	to be assigned to items in a Vector target.
	The default is a generator containing 'yield from rvalue'.
	In the subclass, rvalue doesn't have to be an iterable.

2. How Augmented Assignment treats its operator, converting the supplied operator object into
	an operator Callable[[ValT, ValT], ValT].
	The default interprets the operator as an ast.operator object.

Order of operations:

An operation on an Target will perform various operations on external entities,
like namespaces, lists, or dicts.  The overall operation will perform these smaller
operations in the same order as would be done by the analogous Python code.

1.	In an Environ, the rvalue is evaluated once, then assigned to each of
	the targets on the left side, in program order.

2.	For a store, if the target is a Vector, then the rvalue is unpacked.
	The individual unpacked values are then assigned to each target in the Vector
	(with special handling for starred targets).
	Each target is completely assigned before the next one is.

3.	If the target is a Scalar, then the primary expression and the key are evaluated,
	in that order.  These evaluations can get values from the external environment,
	and an assignment expression can change a value.

	Finally, the operation is performed on the primary object.

4.	For a load from a Vector, a tuple is formed (recursively) from the results of loads
	on the individual elements (unpacking starred targets).  The only thing that might
	alter the extenal environment would be an iteration method for a starred target.

"""

from __future__ import annotations
from typing import *
import functools
import ast
from abc import *
from operator import *
from itertools import chain
from contextlib import contextmanager

from . import treebuild

TargT = TypeVar('TargT')
KeyT = TypeVar('KeyT')
ValT = TypeVar('ValT')
OperT = TypeVar('OperT')
BinOpT = Callable[[ValT, ValT], ValT]
BuildT = TypeVar('BuildT')

class Target(Generic[TargT]):
	is_starred: Final[bool] = False
	target: TargT

	@abstractmethod
	def __init__(self, target: TargT):
		self.target = target

	def store(self, bldr: BuildT, value: ValT):
		return NotImplemented

	def augstore(self, bldr: BuildT, op: AugOpT, value: ValT):
		raise TypeError(f'Augmented assign requires a scalar target, not {type(self).__name__}.')

	def delete(self, bldr: BuildT):
		return NotImplemented

	def load(self, bldr: BuildT):
		return NotImplemented

	def _values(self, bldr: BuildT) -> Iterable[ValT]:
		""" Iterable of all the values, used to chain together targets in a Vector.
		Every Target yields just its load() value, except for Starred, which
		yields the iteration of its load() value.
		"""
		yield self.load(bldr)

class Vector(Target[Iterable[TargT]]):
	targets: Tuple[TargT, ...]

	def __init__(self, *targets: TargT, **kwds):
		self.targets = targets

	def add(self, *targets: TargT):
		self.targets += targets

	def load(self, bldr: BuildT) -> list[ValT]:
		return tuple(chain(*(target._values(bldr) for target in self.targets)))

	def store(self, bldr: BuildT, rvalue: Iterable[ValT], unpacker: Callable[ValT, Iterable[ValT]] = iter):
		""" Store items in value iterable in corresponding targets.
		Use a Starred target if present.
		"""
		values = list(unpacker(rvalue))
		nv = len(values)
		n = len(self.targets)
		stars = [i for i, target in enumerate(self.targets) if target.is_starred]
		if stars:
			if len(stars) > 1:
				raise TypeError('At most one starred target allowed in assignment.')
			star = stars[0]
			if nv < n - 1:
				raise ValueError(f'Expected at least {n - 1} values to unpack, got {nv}')
			after = nv - (n - star - 1)
			values[star:after] = [tuple(values[star:after])]
		elif nv != n:
			raise ValueError(f'Expected {n} values to unpack, got {nv}')

		for target, val in zip(self.targets, values):
			target.store(bldr, val, unpacker=unpacker)

	def delete(self, bldr: BuildT) -> None:
		any(map(methodcaller('delete', bldr), self.targets))

class Starred(Target[TargT]):
	is_starred: Final[bool] = True

	def _values(self, bldr: BuildT) -> Iterable[ValT]:
		""" Iterable of all the values, used to chain together targets in a Vector.
		Every Target yields just its load() value, except for Starred, which
		yields the iteration of its load() value.
		"""
		yield from self.load(bldr)

	# Delegate methods to the target.
	def load(self, bldr: BuildT) -> ValT:
		return self.target.load(bldr)

	def store(self, bldr: BuildT, value: ValT, **kwds):
		self.target.store(bldr, value)

	def delete(self, bldr: BuildT):
		self.target.store(bldr)


class Scalar(Target[TargT], Generic[TargT, KeyT]):
	key: KeyT

	@abstractmethod
	def __init__(self, target: TargT, key: KeyT, **kwds):
		super().__init__(target, **kwds)
		self.key = key

	def augstore(self, bldr: BuildT, op: AugOpT, rvalue: ValT):
		""" Implement target (op)= value, where (op) is a numerical binary operator.
		This is done for all classes by getting the target, getting its value,
		performing the augmented operation with the given value as the rhs,
		then storing the result.  Depending on the implementation, the current
		target value could be updated in place.
		"""
		current = self.load(bldr)
		self.store(bldr, op(current, rvalue))

class Name(Scalar[None, str]):
	def __init__(self, *args, **kwds):
		super().__init__(None, *args, **kwds)

	def load(self, bldr: BuildT) -> ValT:
		return bldr.load(self.key)

	def store(self, bldr: BuildT, rvalue: ValT, **kwds) -> None:
		bldr.store(self.key, rvalue)

	def delete(self, bldr: BuildT) -> None:
		bldr.delete(self.key)

class Attribute(Scalar[Any, str]):
	""" Location is an attribute of the target. """
	def load(self, bldr: BuildT) -> ValT:
		return getattr(self.target, self.key)

	def store(self, bldr: BuildT, rvalue: ValT, **kwds) -> None:
		setattr(self.target, self.key, rvalue)

	def delete(self, bldr: BuildT) -> None:
		delattr(self.target, self.key)

class Subscript(Scalar['MutableSequence | MutableMapping', KeyT]):
	""" Location is a subscripted element, or slice, of the target. """
	def load(self, bldr: BuildT) -> ValT:
		return self.target[self.key]

	def store(self, bldr: BuildT, rvalue: ValT, **kwds) -> None:
		self.target[self.key] = rvalue

	def delete(self, bldr: BuildT) -> None:
		del self.target[self.key]

class BinaryOp(Generic[ValT, OperT]):
	""" Performs binary or augmented operations on values, or makes callable to do the same. """
	@staticmethod
	def name(op: OperT, aug: bool = False) -> str:
		" Get the python name for the operator, as in '+' or '+='."

	@staticmethod
	def caller(op: OperT, aug: bool = False) -> BinOpT:
		" Return callable to perform the operation. "

class ASTBinOp(BinaryOp[ValT, ast.operator]):
	""" Performs binary or augmented operations on values, or makes callable to do the same. """
	@staticmethod
	def name(op: ast.operator, aug: bool = False) -> str:
		" Get the python name for the operator, as in '+' or '+='."
		# Make 'left (op} right' string from an ast Node.
		expr: ast.Expr = ast.BinOp(ast.Name('left'), op, ast.Name('right'))
		text: str = ast.unparse(expr)
		text = text.split()[1]
		if aug: text += '='
		return text

	@classmethod
	@functools.lru_cache(maxsize=None)
	def caller(cls, op: OperT, aug: bool = False) -> BinOpT:
		# Make 'left (op} right' string
		name = cls.name(op, aug)
		text = f'left {name} right'

		if aug:
			code = compile(text, '<binary_aug_op>', 'exec')
			def func(left: ValT, right: ValT) -> ValT:
				loc = dict(locals())
				exec(code, loc)
				return loc['left']

		else:
			code = compile(text, '<binary_op>', 'eval')
			def func(left: ValT, right: ValT) -> ValT:
				return eval(code)
		
		return func

class Environ(treebuild.Traverser):
	""" Use to perform various types of assignments, in the role of a treebuild.Traverser.
	It references a treebuild.Builder, which is used to perform the operations.

	Performs an Assignment statement, using one or more targets and an rvalue.
	Performs an Augmented Assignment statement, using a Scalar target, an rvalue, and an operator.
		The interpretation of the operator is customizable with a subclass.
		By default, the operator is an ast.operator object, and it performs the operation on python values.
	Performs an Annotated Assignment statement, using a Name target, an optional rvalue, and an annotation.
	Performs a NamedExpression (i.e., x := rvalue).  Same effect as an Assignment (x = rvalue)
		except that the location of x will be different if x is a Name in a comprehension scope.
	It can also perform loads and deletes.
	It can evaluate expressions used by targets, recursively, while performing another operation.
	"""
	binop: BinOp = ASTBinOp()
	bldr: BuildT

	def __init__(self, bldr: BuildT):
		self.bldr = bldr

	def load(self, target: Target) -> ValT:
		return target.load(self.bldr)

	def store(self, target: Target, rvalue: ValT) -> None:
		target.store(self.bldr, rvalue)

	def delete(self, target: Target) -> None:
		return target.delete(self.bldr)

	def assign(self, targets: Iterable[Target], rvalue: ValT) -> None:
		for target in targets:
			target.store(self.bldr, rvalue)

	def store_walrus(self, target: Name, rvalue: ValT) -> None:
		target.store_walrus(self.bldr, rvalue)

	def augstore(self, target: Scalar, op: OperT, rvalue: ValT) -> None:
		target.augstore(self.bldr, self.binop.caller(op, aug=True), rvalue)

	@staticmethod
	def unpack(value: Iterable[ValT]) -> Iterable[ValT]:
		yield from value


class Builder(Vector):
	""" A factory for constructing any Target tree one step at a time,
	such as while traversing a syntax tree.  Assignables are added individually.
	Construction may be recursive, using a context manager to switch to a nested tree.
	After construction is completed, the result is a Vector of all targets added
	at the top level, or the only target if only one target was added.

	Since the Builder is a Vector, target operations may be performed directly on
	the Builder.  Alternatively, the result may be saved in another Target to
	be operated on, allowing a single Builder object to be used many times.

	The Scalar classes can be subclassed and these subclasses known to a subclass
	of Builder.
	"""
	name_class: Type[Name] = Name
	attr_class: Type[Name] = Attribute
	subscr_class: Type[Name] = Subscript

	def __init__(self):
		super().__init__()
		self.curr = self

	@contextmanager
	def add_vector(self):
		save, self.curr = self.curr, Vector()
		save.add(self.curr)
		yield
		self.curr = save

	def add_name(self, name: str, **kwds):
		self.curr.add(self.name_class(name, **kwds))

	def add_attr(self, target: TargT, name: str, **kwds):
		self.curr.add(self.attr_class(target, name, **kwds))

	def add_subscript(self, target: TargT, key: KeyT, **kwds):
		self.curr.add(self.subscr_class(target, key, **kwds))

	@property
	def result(self):
		if len(self.targets) == 1:
			return self.targets[0]
		else:
			return Vector(*self.targets)

class ASTBuilder(Builder, ast.NodeVisitor):
	""" Specialized Builder which traverses an AST tree.
	self.visit(node) creates the Target in self.curr.
	"""
	def visit_Tuple(self, node: ast.Tuple | ast.List) -> None:
		with self.add_vector():
			self.generic_visit(node)

	visit_List = visit_Tuple

	def visit_Name(self, node: ast.Name) -> None:
		self.add_name()


from . import namespaces

bld = Builder()
root = namespaces.GlobalNamespace()
asn = Environ(treebuild.Builder(root=root))

l, r = [1], [2]
op = ast.Add()
b = asn.binop.caller(op)
bb = asn.binop.caller(op, aug=True)
print(b(l, r))
print(bb(l, r))
print(l)
class X: pass

x = Subscript(dict(), 'x')
y = Starred(Name('y'))
z = Name('z')
asn.store(x, 42)
asn.store(y, [[43]])
asn.store(z, 44)
print(asn.load(x))
asn.assign((x, y), (42, 43))
print(asn.load(x), asn.load(y))

asn.store(x, [42])
oldx = asn.load(x)
print(oldx)
asn.augstore(x, ast.Add(), [43])
print(oldx, asn.load(x))
print(asn.load(x) is oldx)

bld.add(x, y, z)
with bld.add_vector():
	bld.add_name('z')
print(asn.load(bld.result))
asn.store(bld, (*range(10), (42, )))	# x, *y, z, [z] = 0, [1, ..., 8], 9, (42,).  z assigned twice.
print(asn.load(bld))
aa = ast.parse('a += b + c', mode='exec')
aa
a, b, c = 42, 3, 10
exec(compile(aa, '', 'exec'))
print(a, b, c)