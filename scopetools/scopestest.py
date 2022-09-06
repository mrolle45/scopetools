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
import functools

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
	Builder,
	NamespaceBuilder,
	Traverser,
	)

_noarg: Final = object()				# Use as some argument default values.

class VarMode(Enum):
	""" Defines how a scope uses the variable 'x'.
	Except for NoCap, makes no restrictions on nested classes.
	"""
	Unused = 'none'
	Used = 'use'
	Anno = 'anno'
	Nonlocal = 'nloc'		# x is declared nonlocal in the scope. If this is not allowed,
							# the Scope will be left as Unused, but the genenrated code will
							# verify that the nonlocal declaration is a syntax error.
	Global = 'glob'
	Local = 'loc'			# x will be bound in this scope by an assignment.
	NoCap = 'ncap'			# same, but nested scopes may not capture x.
							# used as a mode for a nested scope, nested.mode = Local and nested.nocapt = True.

	@classmethod
	def nocapt_modes(cls, nocapt: bool = True) -> Iterator[VarMode]:
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
		return self in (self.Local, self.NoCap)

	@property
	def modifies(self) -> bool:
		return self in (self.Local, self.NoCap, self.Nonlocal, self.Global, )

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
	only_child: int + None = None	# If an int, then only the child with this position in children is used.


	def nest(self, mode: VarMode, kind: ScopeKind) -> ScopeParams:
		""" New object to go with a nested scope. """
		nocapt = self.nocapt
		if mode is mode.NoCap:
			nocapt = True
		return attrs.evolve(self,
				level=self.level + 1,
				depth=self.depth - 1,
				mode=mode,
				nocapt=nocapt,
				kind=kind,
				only_child = None,
				)

	@property
	def nested_params(self) -> Iterable[ScopeParams]:
		if self.depth:
			index = 0
			for kind in Scope.CLASS, Scope.FUNC:
				for index, mode in enumerate(self.mode.nocapt_modes(self.nocapt), index):
					if self.only_child is None or self.only_child == index:
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

	def visit(self, src: SrcT):
		""" Builder commands for a single tree, and recursively called for
		nested trees.
		Note, commands applied to the current tree will be interrupted by commands for
		nested trees.
		"""
		name = self.curr.name

		varname = '__x' if self.do_mangle else 'x'
		rvalue = self.make_rvalue(varname, 'x')

		def allvars() -> Iterable[str]:
			""" Generate var plus all mangled names. """
			yield varname
			for name in sorted(self.scope.mangled_names):
				if name != self.mangle(varname):
					yield name

		# 1. Prologue.  This is the initial declaration of name.
		mode = src.mode

		for var in allvars():
			if mode is mode.Nonlocal:
				try: self.decl_nonlocal(var)
				except SyntaxError: return
			elif mode is mode.Global:
				self.decl_global(var)
			elif mode is mode.Anno:
				self.anno(var, 'str')

			if mode is not mode.Unused:
				self.maketest(var)

		# 2. Nested classes and functions, with var in the original state.
		def do_nested(sfx: str = ''):
			for sub_ref in src.nested_params:
				sub_name = sub_ref.makename(sfx)
				if name: sub_name = name + '_' + sub_name
				with self.nest(sub_ref.kind, sub_ref, sub_name):
					self.visit(sub_ref)
		do_nested()

		if mode.modifies:

			# 3. Modifications to var.
			orig_bounds = dict()
			for var in allvars():
				orig_bound = orig_bounds[var] = isinstance(self.curr, Namespace) and self.has_bind(var)
				# Make unbound.
				if orig_bound:
					self.delete(var)
					self.maketest(var)

			# Make bound using nested scope.
			if sys.version_info < (3, 8) or self.curr.kind.is_class:
				nest_kind = self.FUNC; n = f'{name}_setfunc'
			else:
				nest_kind = self.COMP; n = f'{name}_setcomp'
			with self.nest(nest_kind, attrs.evolve(src, kind=nest_kind), n):
				for var in allvars():
					self.store_nested(var, rvalue, mode)
			for var in allvars():
				self.maketest(var)

			# Make unbound using nested scope.
			nest_kind = self.FUNC
			n = name + '_' + 'delfunc'
			with self.nest(nest_kind, attrs.evolve(src, kind=nest_kind), n):
				for var in allvars():
					self.delete_nested(var, mode)
			for var in allvars():
				self.maketest(var)

			# Make bound.
			for var in allvars():
				self.store(var, rvalue)
				self.maketest(var)

			# Make unbound.
			for var in allvars():
				self.delete(var)
				self.maketest(var)

			# Make the opposite state from originally.
			for var, orig_bound in orig_bounds.items():
				if not orig_bound:
					self.store(var, rvalue)
					self.maketest(var)

			# 4. Similar nested classes and functions, with var in the opposite state.
			do_nested('2')

			# 5. Epilogue.  Restore var to its original state.
			for var in allvars():
				if orig_bound: self.store(var, rvalue)
				else: self.delete(var)
				self.maketest(var)

class GenScopes(Builder):
	""" Builder subclass to create the Scopes tree. """

	def __init__(self, *args, **kwds):
		super().__init__(*args, **kwds)
		self.has_closure: Scope | None = None

	# Special methods used by the traverser...

	@contextmanager
	def nest(self, kind: Scope.Kind, src: ScopeParams, *args, **kwds) -> Iterator[Scope]:
		""" Preserve and update whether the scope has a closure scope for 'x'.
		This is possible because the scope.src.mode indicates how closure is
		propagated to nested classes.
		"""
		save = self.has_closure

		# push into nested scope.
		with super().nest(kind, src, *args, **kwds) as newtree:
			# Update has_closure based on new scope.
			newtree.mangled_names = set()
			kind = newtree.kind
			# In a Class scope, nested scopes bypass the Class to find closures.
			# So has_closure will be the same.
			if kind.is_class:
				pass
			elif src:
				mode = src.mode
				if mode in (mode.Local, mode.Anno):
					self.has_closure = self.curr
				if mode is mode.Global:
					self.has_closure = None
			yield
		self.has_closure = save

	def maketest(self, name: str): self.use(name)

	def make_rvalue(self, *args) -> str:
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
					self.decl_global(name)
				else:
					self.decl_nonlocal(name)

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
				self.decl_global(name)
			else:
				self.curr.decl_nonlocal(name)

	def decl_nonlocal(self, name):
		""" Check if the name is resolvable. """
		if not self.has_closure:
			raise SyntaxError()
		self.add_mangled(self.has_closure, name)
		self.curr.decl_nonlocal(name)

	def decl_global(self, name):
		self.add_mangled(self.glob, name)
		self.curr.decl_global(name)

	def add_mangled(self, target: Scope, name: str):
		# Set target to use mangled name for '__x' in curr scope.
		n = self.mangle(name)
		if n != name:
			target.mangled_names.add(n)
			target.bind(n)

class GenNamespaces(NamespaceBuilder):
	""" Builder subclass to create the Namespaces tree, and write python test code. """

	scope_builder_class: ClassVar[Type[Builder]] = GenScopes

	def __init__(self, *args, mangle: bool = False, **kwds):
		self.do_mangle = mangle
		super().__init__(*args, **kwds)

	def build_all(self, out: TextIO = StringIO(), mangle: bool = False):
		self.num_tests: int = 0
		self.out = out
		self.level: int = 0
		self.lineno = len(out.getvalue().splitlines()) + 1
		out.truncate(0)
		out.seek(0)
		self.write('')
		self.trav.do_mangle = mangle
		self.build()

	@contextmanager
	def nest(self, kind: _Kind, *args, **kwds) -> Iterable[TreeT]:
		""" Moves to new nested Namespace, also saves and restores some things.
		Writes the definition of the scope and a call to it if it is a function.
		"""
		newspace: Namespace
		with super().nest(kind, *args, **kwds) as newspace:
			objname = newspace.name
			if kind.is_class:
				self.write(f'class {objname}:')
			elif kind.is_function:
				self.write(f'def {objname}():')
			self.level += 1
			l = self.lineno
			yield newspace
			if l == self.lineno:
				self.write('pass')
			self.level -= 1
			if kind.is_function:
				self.write(f'{objname}()')

	@contextmanager
	def use_parent(self) -> Iterator[Namespace]:
		""" Adjusts the indent level during the context, as well as switching the current tree. """
		self.level -= 1
		with super().use_parent() as parent:
			yield parent
		self.level += 1

	@Scope.mangler(var='name')
	def maketest(self, name: str):
		""" Generate code to verify expected value of name in current namespace at current time. """
		space: Namespace = self.curr
		self.num_tests += 1
		value = space.has(name) and space.load(name) or None
		self.write(f'try: test({name}, {value!r}, {self.lineno})')
		self.write(f'except NameError: test(None, {value!r}, {self.lineno})')

	#@Scope.mangler(var='name')
	def decl_nonlocal(self, name):
		binding = self.scope.binding(name)
		scope = binding and binding.scope
		if not (scope and scope.kind.is_closed):
			# No nonlocal binding.  There are no nested scopes, but generate a test.

			self.write('# No enclosed binding exists.')
			self.write(f'try: compile("nonlocal {name}", "<string>", "exec")')
			self.write(f'except SyntaxError: test(None, None, {self.lineno})')
			self.write(f'else: error("Enclosed binding exists", {self.lineno})')
			self.num_tests += 1
			raise SyntaxError
		self.write(f'nonlocal {name}')

	#@Scope.mangler(var='name')
	def decl_global(self, name):
		self.write(f'global {name}')

	@Scope.mangler
	def make_rvalue(self, var: str, name: str) -> str:
		""" Make str value to store in variable {name}. """
		scope = self.curr.scope
		try: rvalue: str = scope.binding_scope(var).name + '.' + name
		except SyntaxError: rvalue = name
		if rvalue.startswith('.'): rvalue = name
		return rvalue

	#@Scope.mangler(var='name')
	def store(self, name: str, rvalue: str, **kwds) -> None:
		""" Output python code to store the expected value of '{name}'. """

		self.write(f'{name} = "{rvalue}"')
		self.curr.store(name, rvalue, **kwds)

	#@Scope.mangler(var='name')
	def store_nested(self, name: str, rvalue: ValT, parent_mode: VarMode, **kwds) -> None:
		""" Output python code to store the expected value of '{name}'. """

		scope = self.scope
		if self.kind.is_comp:
			# Can use a Comrehension with a walrus if Python 3.8 or later and
			#	parent is not a class.
			# HOWEVER, if parent is Global mode, a compiler bug croaks on the private name
			#	as a walrus target, but the mangled name is OK.
			if scope.parent.src.mode is scope.parent.src.mode.Global and name != self.mangle(name):
				name = self.mangle(name)
				comm = ' # (mangled target name needed due to compiler bug)'
			else: comm = ''
			with self.use_parent(): self.write(f'[{(name)} := _ for _ in ["{rvalue}"]]{comm}')
			self.store_walrus(name, rvalue)
		else:
			if scope.parent.kind.is_class and parent_mode.is_loc:
				# For a class, it is necessary to find its stack frame and store in its locals.
				self.write(f'inspect.stack()[1].frame.f_locals["{self.mangle(name)}"] = "{rvalue}"')
			else:
				if parent_mode is parent_mode.Global:
					self.write(f'global {name}; {name} = "{rvalue}"')
				else:
					self.write(f'nonlocal {name}; {name} = "{rvalue}"')
			with self.use_parent():
				self.curr.store(name, rvalue)

	#@Scope.mangler(var='name')
	def delete(self, name: str, **kwds) -> None:
		self.write(f'del {name}')
		self.curr.delete(name, **kwds)

	#@Scope.mangler(var='name')
	def delete_nested(self, name: str, parent_mode: VarMode, **kwds) -> None:
		""" Write code to delete value in parent.  There are no nested scopes.
		"""
		scope = self.scope
		context = scope.parent.context(name)

		if scope.parent.kind.is_class and context.is_local:
			# For a class with a Local variable, it is necessary to find its stack frame
			#	and remove from its locals.
			self.write(f'del inspect.stack()[1].frame.f_locals["{self.mangle(name)}"]')
		else:
			if context.is_global or self.parent.kind.is_global:
				self.write(f'global {name}; del {name}')
			else:
				self.write(f'nonlocal {name}; del {name}')
		with self.use_parent():
			self.curr.delete(name)

	#@Scope.mangler(var='name')
	def anno(self, name: str, anno) -> Self:
		self.curr.anno(name, anno)
		if isinstance(anno, str):
			s = anno
		else:
			s = str(anno)
		self.write(f'{name}: {s}')


	def write(self, s: str):
		print('    ' * self.level + s, file=out)
		self.lineno += len(s.split('\n'))


def gen(args, out: TextIO, prolog: list[str], mangle: bool = False, only_child: int | None = None) -> Tuple[int, Namespace]:
	""" Main function to write most of the output. """

	print(f'Generating code... ', end='', flush=True)
	top_ref = ScopeParams(0, args.d, VarMode.Local, only_child=only_child)
	scope = Scope(kind=Scope.GLOB, cache_resolved=False, src=top_ref)
	# TODO: Let the namespace builder build the scope.
	trav = GenTraverse()
	try:
		num_tests = 0
		ns = GlobalNamespace(top_ref, None, key=43)
		ns.scope.mangled_names = set()
		ns_bldr = GenNamespaces(ns, trav, indexed=True)
		ns_bldr.build_all(out, mangle=mangle)
		num_tests += ns_bldr.num_tests
	finally:
		print(f'{num_tests} tests')
	return num_tests, ns


g = GlobalScope(None)
with g.nestCLASS(None, name='c') as c:
	with c.nestFUNC(None, name='f') as f:
		pass

n = GlobalNamespace(None, scope=g)
n.add_nested()
assert n.nested[0].nested[0].mangle('__x') == '_c__x'

if __name__ == '__main__':
	out = StringIO()
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', default = 3, type=int, choices=range(2, 5),
		help='Depth of the scopes and namespaces tree (default 3)')
	parser.add_argument('-s', action='store_true', help='Save the output file')
	parser.add_argument('-t', action='store_true', help='Copy the output file to file with ".txt" appended to the name')
	parser.add_argument('-o', default='sc_test.py', help='Output file name (default "sc_test.py")')
	parser.add_argument('--nomangle', action='store_true', help='Skip tests with mangled names')

	args = parser.parse_args()

	#out = StringIO()
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

''').splitlines()

	def run_test(mangle: bool = False, only_child: int | None = None) -> str:
		global out
		if args.d == 4 and only_child is None:
			# Perform several shorter tests each with a different only child index.
			top_ref = ScopeParams(0, args.d, VarMode.Local)
			nested = list(top_ref.nested_params)
			for only_child, params in enumerate(nested):
				name = params.mode.name_sfx('aA'[params.kind.is_class])
				print(f'{only_child + 1} of {len(nested)} ({name}).')
				run_test(mangle, only_child)
			return ''
		num_tests, root_ns = gen(args, out, prolog, mangle=mangle, only_child=only_child)

		print('Compiling... ', end='', flush=True)
		lines = [*prolog, *out.getvalue().splitlines()]
		import ast
		code = compile('\n'.join(lines), '<generated>', 'exec')

		print('done')
		print('Running tests. ')
		try: exec(code, globals())
		except ValueError as exc:
			print()
			msg, lineno = exc.args
			lines = out.getvalue().splitlines()
			print(*lines[max(lineno - 11, 0):lineno], sep='\n')
			print('---- ' + msg)
			print(*lines[lineno: lineno + 10], sep='\n')
			raise
		else:
			if num_tests % 1000: print('\r' f'{num_tests}', end='', flush=True)
			print(' done')
			print(f'All {num_tests} tests passed.')

		# Regression test.  Generate trees from the output code.
		print('Analyzing output file...', end='', flush=True)
		import treebuild, ast
		src = ast.parse(out.getvalue())
		root = GlobalNamespace(src=src)
		trav = treebuild.ASTTraverser()
		build = treebuild.NamespaceBuilder(root, trav, indexed=True)
		build.build()
		print('')
		x = 0
		from itertools import zip_longest
		var = '__x' if mangle else 'x'
		# Compare the scopes trees.
		def compare(scope1, scope2) -> bool:
			if scope1.name != scope2.name:
				if scope2.kind is not scope2.kind.COMP:
					raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match")
			b1, b2 = scope1.vars.get('x'), scope2.vars.get('x')
			if (b1 is None) != (b2 is None):
				raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match: {b1}, {b2}")
			if b1 and (b1.scope is None) != (b2.scope is None):
				raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match: {b1.scope!r}, {b2.scope!r}")
			if b1 and b1.scope and b1.scope.name != b2.scope.name:
				raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match: {b1.scope.name}, {b2.scope.name}")
			for n1, n2 in zip_longest(scope1.nested, scope2.nested):
				if n1 is None or n2 is None:
					raise ValueError(f"Scopes {scope1!r} and {scope2!r} don't match")
				compare(n1, n2)
		print('Comparing scopes...', end='', flush=True)
		#compare(root_ns.scope, root.scope)
		print('')
		# Compare the namespace trees.
		def compare(ns1, ns2) -> bool:
			if ns1.name != ns2.name and ns1.kind is not ns1.COMP:
				raise ValueError(f"Namespaces {ns1!r} and {ns2!r} don't match")
			nest1 = ns1.nested
			nest2 = ns2.nested
			if len(nest1) != len(nest1):
				raise ValueError(f"Namespaces {ns1!r} and {ns2!r} don't match")
			for ns1, ns2 in zip(nest1, nest2):
				compare(ns1, ns2)
		print('Comparing namespaces...', end='', flush=True)
		#compare(root_ns, root)
		print('')
		return out.getvalue()

	print('Testing.')
	text = run_test()
	#text = ''; print()
	if not args.nomangle:
		print('Testing mangled names.')
		text += run_test(mangle=True)
	filename = args.o
	if args.d < 4:
		if args.s:
			with open(filename, 'w') as f:
				map(f.write, prolog)
				f.write(text)
				print(f'Writing to "{f.name}."')
		if args.t:
			with open(f'{filename}.txt', 'w') as f:
				map(f.write, prolog)
				f.write(text)
				print(f'Copying to "{f.name}."')
