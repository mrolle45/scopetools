from __future__ import annotations
from ast import Try
from re import X

import sys, os
from contextlib import contextmanager
from io import StringIO
from typing import NamedTuple, Iterable, Iterator

from enum import *
import attrs
import argparse

from scopes import(
	Scope,
	FunctionScope,
	ClassScope,
	GlobalScope,
	ComprehensionScope,
	)

from namespaces import(
	BuildT as NsBuildT,
	GlobalNamespace,
	Namespace
	)

from treebuild import(
	ScopeBuilder,
	NamespaceBuilder,
	Traverser,
	)

_noarg: Final = object()				# Use as some argument default values.

class VarMode(Enum):
	""" Defines how a scope uses the variable 'x'.
	Except for LocalNoCapt, makes no restrictions on nested classes.
	"""
	Unused = 'none'
	Used = 'use'
	Anno = 'anno'
	Nonlocal = 'nloc'		# x is declared nonlocal in the scope. If this is not allowed,
							# the Scope will be left as Unused, but the genenrated code will
							# verify that the nonlocal declaration is a syntax error.
	Global = 'glob'
	Local = 'loc'			# x will be bound in this scope by an assignment.
	LocalNoCapt = 'ncap'	# same, but nested scopes may not capture x.
							# used as a mode for a nested scope, nested.mode = Local and nested.nocapt = True.

	@classmethod
	def nocapt_modes(cls, nocapt: bool = True) -> Iterable[VarMode]:
		""" Gives all the possible modes, based on whether "no captures" is in effect,
		which defaults to True.
		"""
		if nocapt:
			yield cls.Unused
			yield cls.Global
			yield cls.Local
		else:
			yield from cls.__members__.values()

	@property
	def is_loc(self) -> bool:
		return self in (self.Local, self.LocalNoCapt)

	@property
	def modifies(self) -> bool:
		return self in (self.Local, self.LocalNoCapt, self.Nonlocal, self.Global, )

	def name_sfx(self, name: str = '') -> str:
		""" Suffix for a scope name, optionally added to given name. """
		if self is self.Unused: return name
		return f'{name}_{self.value}'

@attrs.define(frozen=True)
class ScopeParams:
	""" Everything the builder needs to know about building a scope,
	other than attributes of the scope itself.
	"""
	level: int				# How deep in the scope tree.  Global scope is level 0.
	depth: int				# How much deeper to make nested scopes.  0 means no nested.
	mode: VarMode			# How the variable 'x' will be used in this scope.
	nocapt: bool = False	# If true, restricts nested scopes to those that don't capture
							# 'x' from this scope.
	kind: ScopeKind = None

	def nest(self, mode: VarMode, kind: ScopeKind) -> ScopeParams:
		""" New object to go with a nested scope. """
		nocapt = self.nocapt
		if mode is mode.LocalNoCapt:
			nocapt = True
		return attrs.evolve(self,
				level=self.level + 1,
				depth=self.depth - 1,
				mode=mode,
				nocapt=nocapt,
				kind=kind,
				)

	def nested_params(self) -> Iterable[ScopeParams]:
		""" Characterizes all of the set of nested scopes to generate.
		Tuple of (is class, var type).
		At the bottom nesting level, the iterator is empty.
		"""
		if self.depth:
			for kind in Scope.CLASS, Scope.FUNC:
				for mode in self.mode.nocapt_modes(self.nocapt):
					yield self.nest(mode, kind)

	def makename(self, suffix: str = ''):
		"Name for a nested scope."
		name = 'aA'[self.kind.is_class]
		name = chr(ord(name) + self.level - 1)
		name += suffix
		return self.mode.name_sfx(name)

class GenTraverse(Traverser):
	""" Common source of builder commands for both Scope and Namespace tree builders.
	Some commands or parameters are only relevant to one of these and ignored by the other.
	Note, the builders have some added methods and method keywords.
	"""

	def visit(self, ref: ScopeParams, name: str = ''):
		""" Builder commands for a single tree, and recursively called for
		nested trees.
		Note, commands applied to the current tree will be interrupted by commands for
		nested trees.
		"""

		var = 'x'
		rvalue = self.make_rvalue(var)

		# 1. Prologue.  This is the initial declarations or settings of name.
		mode = ref.mode

		if mode is mode.Nonlocal:
			try: self.nonlocal_stmt(var)
			except SyntaxError: return
		elif mode is mode.Global:
			self.global_stmt(var)
		elif mode is mode.Anno:
			self.anno(var, 'str')

		if mode is not mode.Unused:
			self.maketest(var)

		# 2. Nested classes and functions, with var in the original state.
		def do_nested(sfx: str = ''):
			for sub_ref in ref.nested_params():
				sub_name = sub_ref.makename(sfx)
				if name: sub_name = name + '_' + sub_name
				with self.nest(sub_ref.kind, sub_name, ref=sub_ref):
					self.visit(sub_ref, sub_name)
		do_nested()

		if mode.modifies:

			# 3. Modifications to var.
			orig_bound = isinstance(self.curr, Namespace) and self.has_bind(var)
			# Make unbound.
			if orig_bound:
				self.delete(var)
				self.maketest(var)

			# Make bound using nested scope.
			if sys.version_info < (3, 8) or self.curr.kind.is_class:
				nest_kind = self.FUNC; n = f'{name}_setfunc'
			else:
				nest_kind = self.COMP; n = ''
			with self.nest(nest_kind, n): self.store_nested(var, rvalue, mode)
			self.maketest(var)

			# Make unbound using nested scope.
			nest_kind = self.FUNC
			with self.nest(nest_kind, name + '_' + 'delfunc'): self.delete_nested(var, mode)
			self.maketest(var)

			# Make the opposite state from originally.
			if not orig_bound:
				self.store(var, rvalue)
				self.maketest(var)

			# 4. Similar nested classes and functions, with var in the opposite state.
			do_nested('2')

			# 5. Epilogue.  Restore var to its original state.
			if orig_bound: self.store(var, rvalue)
			else: self.delete(var)
			self.maketest(var)


class GenScopes(ScopeBuilder):
	""" Builder subclass to create the Scopes tree. """

	def __init__(self, *args, **kwds):
		super().__init__(*args, **kwds)
		self.has_closure = False

	# Special methods used by the traverser...

	@contextmanager
	def nest(self, *args, ref: ScopeParams = None, **kwds) -> Generator:
		""" Preserve and update whether the scope has a closure scope for 'x'.
		This is possible because the scope.ref.mode indicates how closure is
		propagated to nested classes.
		"""
		save = self.has_closure

		# push into nested scope.
		with super().nest(*args, **kwds):
			# Update has_closure based on new scope.
			kind = self.curr.kind
			# In a Class scope, nested scopes bypass the Class to find closures.
			# So has_closure will be the same.
			if kind.is_class:
				pass
			elif ref:
				mode = ref.mode
				if mode in (mode.Local, mode.Anno):
					self.has_closure = True

			yield
		self.has_closure = save

	def maketest(self, name: str): pass

	def make_rvalue(self, name: str) -> str:
		""" Make str value to store in variable {name}. """
		return ''

	def store(self, name: str, _rvalue: ValT) -> None:
		self.bind(name)

	def store_nested(self, name: str, _rvalue: ValT, parent_mode: VarMode, **kwds) -> None:
		""" Function or Comprehension that stores a value in the parent. """
		if self.kind.is_comp:
			# Can use a Comrehension with a walrus if Python 3.8 or later and
			#	parent is not a class.
			with self.use_walrus(): self.bind(name)
		else:
			# Otherwise must use a Function.
			scope = self.curr

			if scope.parent.kind.is_class and parent_mode.is_loc:
				# For a class, it is necessary to find its stack frame and remove from its locals.
				pass
			else:
				if parent_mode is parent_mode.Global or scope.parent.kind.is_global:
					self.global_stmt(name)
				else:
					self.nonlocal_stmt(name)

	def delete(self, name: str) -> None:
		self.bind(name)

	def delete_nested(self, name: str, parent_mode: VarMode, **kwds) -> None:
		""" Function to delete the variable from the parent. """
		scope = self.curr

		if scope.parent.kind.is_class and parent_mode.is_loc:
			# For a class with a Local variable, it is necessary to find its stack frame
			#	and remove from its locals.
			pass
		else:
			if parent_mode is parent_mode.Global or scope.parent.kind.is_global:
				self.global_stmt(name)
			else:
				self.curr.nonlocal_stmt(name)

	def build_scope(self, ref: ScopeParams):
		""" Define the static properties of the scope and create and build the nested scopes.
		"""
		self.trav.build(self, ref)

	def nonlocal_stmt(self, name):
		""" Check if the name is resolvable. """
		if not self.has_closure:
			raise SyntaxError()
		self.curr.nonlocal_stmt(name)

class GenNamespaces(NamespaceBuilder):
	""" Builder subclass to create the Namespaces tree, and write python test code. """

	def scope_builder(self) -> ScopeBuilder:
		""" A Builder to build the current scope, called if scope is not yet built. """
		return GenScopes(self.curr.scope, self.trav)

	def build_all(self, ref: ScopeParams, out: TextIO = StringIO(), prolog: list[str] = []):
		self.num_tests: int = 0
		self.out = out
		self.level: int = 0
		self.lineno = len(prolog) + 1
		self.write('')
		self.build(ref)

	@contextmanager
	def nest_tree(self, space: Namespace) -> Generator:
		""" Moves to new nested Namespace, also saves and restores some things.
		Writes the definition of the scope and a call to it if it is a function.
		"""
		kind = space.kind
		objname = space.scope.scope_name
		if kind.is_class:
			self.write(f'class {objname}:')
		elif kind.is_function:
			self.write(f'def {objname}():')
		self.level += 1
		l = self.lineno
		with super().nest_tree(space):
			yield space
		if l == self.lineno:
			self.write('pass')
		self.level -= 1
		if kind.is_function:
			self.write(f'{objname}()')

	@contextmanager
	def use_parent(self) -> Generator:
		""" Adjusts the indent level during the context, as well as switching the current tree. """
		self.level -= 1
		with super().use_parent() as parent:
			yield parent
		self.level += 1

	def maketest(self, name: str):
		""" Generate code to verify expected value of name in current namespace at current time. """
		space: Namespace = self.curr
		self.num_tests += 1
		value = space.has(name) and space.load(name) or None
		self.write(f'try: test({name}, {value!r}, {self.lineno})')
		self.write(f'except NameError: test(None, {value!r}, {self.lineno})')

	def nonlocal_stmt(self, name):
		binding = self.scope.binding(name)
		scope = binding and binding.scope
		if not (scope and scope.kind.is_closed):
		#if not self.scope.has_closure:
			# No nonlocal binding.  There are no nested scopes, but generate a test.

			self.write('# No enclosed binding exists.')
			self.write(f'try: compile("nonlocal {name}", "<string>", "exec")')
			self.write(f'except SyntaxError: test(None, None, {self.lineno})')
			self.write(f'else: error("Enclosed binding exists", {self.lineno})')
			self.num_tests += 1
			raise SyntaxError
		self.write(f'nonlocal {name}')

	def global_stmt(self, name):
		self.write(f'global {name}')

	def make_rvalue(self, name: str) -> str:
		""" Make str value to store in variable {name}. """
		scope = self.curr.scope
		try: rvalue: str = scope.binding_scope(name).scope_name + '.' + name
		except SyntaxError: rvalue = name
		if rvalue.startswith('.'): rvalue = name
		return rvalue

	def store(self, name: str, rvalue: str, **kwds) -> None:
		""" Output python code to store the expected value of '{name}'. """

		self.write(f'{name} = "{rvalue}"')
		self.curr.store(name, rvalue, **kwds)

	def store_nested(self, name: str, rvalue: ValT, parent_mode: VarMode, **kwds) -> None:
		""" Output python code to store the expected value of '{name}'. """

		scope = self.scope
		if self.kind.is_comp:
			# Can use a Comrehension with a walrus if Python 3.8 or later and
			#	parent is not a class.
			with self.use_parent(): self.write(f'[{name} := _ for _ in ["{rvalue}"]]')
			self.store_walrus(name, rvalue)
		else:
			status = scope.parent.status(name)

			if scope.parent.kind.is_class and parent_mode.is_loc:
				# For a class, it is necessary to find its stack frame and store in its locals.
				self.write(f'inspect.stack()[1].frame.f_locals["{name}"] = "{rvalue}"')
			else:
				if parent_mode is parent_mode.Global:
					self.write(f'global {name}; {name} = "{rvalue}"')
				else:
					self.write(f'nonlocal {name}; {name} = "{rvalue}"')
			with self.use_parent():
				self.curr.store(name, rvalue)

	def delete(self, name: str, **kwds) -> None:
		self.write(f'del {name}')
		self.curr.delete(name, **kwds)

	def delete_nested(self, name: str, parent_mode: VarMode, **kwds) -> None:
		""" Write code to delete value in parent.  There are no nested scopes.
		"""
		scope = self.scope
		status = scope.parent.status(name)

		if scope.parent.kind.is_class and status.is_local:
			# For a class with a Local variable, it is necessary to find its stack frame
			#	and remove from its locals.
			self.write(f'del inspect.stack()[1].frame.f_locals["{name}"]')
		else:
			if status.is_global or self.parent.kind.is_global:
				self.write(f'global {name}; del {name}')
			else:
				self.write(f'nonlocal {name}; del {name}')
		with self.use_parent():
			self.curr.delete(name)

	def anno(self, name: str, anno, rvalue: ValT = _noarg) -> Self:
		self.curr.anno(name, anno, rvalue)
		if isinstance(anno, str):
			s = anno
		else:
			s = str(anno)
		if rvalue is _noarg:
			self.write(f'{name}: {s}')
		else:
			self.write(f'{name}: {s} = {rvalue!r}')

	def write(self, s: str):
		print('    ' * self.level + s, file=out)
		self.lineno += len(s.split('\n'))


def gen(args, out: TextIO, prolog: list[str]) -> Tuple[int, Namespace]:
	""" Main function to write most of the output. """

	top_ref = ScopeParams(0, args.d, VarMode.Local)
	scope = GlobalScope(cache_resolved=False, ref=top_ref)
	# TODO: Let the namespace builder build the scope.
	trav = GenTraverse()
	#scope_bldr = GenScopes(scope, trav)
	#with scope_bldr.build():
	#	scope_bldr.build_scope(top_ref)
	ns = GlobalNamespace(scope, key=43)
	ns_bldr = GenNamespaces(ns, trav, indexed=True)
	try: ns_bldr.build_all(top_ref, out, prolog)
	finally:
		print(f'{ns_bldr.num_tests} tests')
		if args.s:
			with open(args.o, 'w') as f:
				map(f.write, prolog)
				f.write(out.getvalue())
				print(f'Writing to "{f.name}."')
		if args.t:
			with open(f'{args.o}.txt', 'w') as f:
				map(f.write, prolog)
				f.write(out.getvalue())
				print(f'Copying to "{f.name}."')
	return ns_bldr.num_tests, ns

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-d', default = 3, type=int, choices=range(2, 5),
		help='Depth of the scopes and namespaces tree (default 3)')
	parser.add_argument('-s', action='store_true', help='Save the output file')
	parser.add_argument('-t', action='store_true', help='Copy the output file to file with ".txt" appended to the name')
	parser.add_argument('-o', default='sc_test.py', help='Output file name (default "sc_test.py")')

	args = parser.parse_args()
	print(f'Generating code... ', end='', flush=True)

	out = StringIO()
	prolog = (
'''from __future__ import annotations
import inspect
ntests = 0
def test(value: str | None, comp: str | None, lineno: int):
	if value != comp:
		raise ValueError(f'Line {lineno}: expected {comp!r}, got {value!r}.', lineno) from None
	global ntests
	ntests += 1
	if ntests % 1000 == 0:
		print('\\r' f'{ntests}', end='')

def error(msg: str, lineno: int):
	raise ValueError(f'Line {lineno}: {msg}.', lineno) from None

print('Running tests. ')
''').splitlines()

	num_tests, root_ns = gen(args, out, prolog)

	print('Compiling... ', end='', flush=True)
	code = compile('\n'.join((*prolog, out.getvalue())), '<generated>', 'exec')
	print('done')
	try: exec(code)
	except ValueError as exc:
		print()
		msg, lineno = exc.args
		lines = out.getvalue().splitlines()
		lineno -= len(prolog.splitlines())
		print(*lines[max(lineno - 11, 0):lineno], sep='\n')
		print('---- ' + msg)
		print(*lines[lineno: lineno + 10], sep='\n')
	else:
		print(' done')
		print(f'All {num_tests} tests passed.')

	# Regression test.  Generate trees from the output code.
	import treebuild, ast
	root = GlobalNamespace()
	trav = treebuild.ASTTraverser()
	build = treebuild.NamespaceBuilder(root, trav, indexed=True)
	build.build(ast.parse(out.getvalue()))
	x = 0
	from itertools import zip_longest
	# Compare the scopes trees.
	def compare(scope1, scope2) -> bool:
		if scope1.scope_name != scope2.scope_name:
			if scope2.kind is not ScopeKind.COMP:
				raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match")
		b1, b2 = scope1.vars.get('x'), scope2.vars.get('x')
		if (b1 is None) != (b2 is None):
			raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match")
		if b1 and (b1.scope is None) != (b2.scope is None):
			raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match")
		if b1 and b1.scope and b1.scope.scope_name != b2.scope.scope_name:
			raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match")
		for n1, n2 in zip_longest(scope1.nested, scope2.nested):
			if n1 is None or n2 is None:
				raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match")
			compare(n1, n2)
	compare(root_ns.scope, root.scope)
	# Compare the namespace trees.
	def compare(ns1, ns2) -> bool:
		if ns1.scope.scope_name != ns2.scope.scope_name:
			raise ValueError(f"Namespaces {ns1!r} and {ns2!r} don't match")
		names = sorted(set(ns1.nested))
		if names != sorted(set(ns2.nested)):
			raise ValueError(f"Namespaces {ns1!r} and {ns2!r} don't match")
		for name in names:
			compare(ns1.nested[name], ns2.nested[name])
	compare(root_ns, root)
			