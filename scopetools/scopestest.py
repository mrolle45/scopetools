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

if __name__ == '__main__':
	import scopetools.scopestest
else:
	from .variables import *

	from .scope_common import *

	from .scopes import(
		Scope,
		FunctionScope,
		ClassScope,
		GlobalScope,
		ComprehensionScope,
		)

	from .namespaces import(
		BuildT as NsBuildT,
		GlobalNamespace,
		Namespace
		)

	from .treebuild import(
		Builder,
		NamespaceBuilder,
		Traverser,
		)


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
		only_child: int = None	# If an int >= 0, then only the child with this position in children is used.


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
				LIMITED = 0x0
				if LIMITED and self.only_child != -1:
					if self.only_child not in (None, 9): return
					selected = (
						(
							#(VarMode.Anno, ScopeKind.FUNC),		# a_anno
						),
						(
							#(VarMode.Unused, ScopeKind.FUNC),	# b
						),
						(
							#(VarMode.Global, ScopeKind.CLASS),	# C_glob
						),
						(
						),
					)
					nested = selected[self.level]
					if nested:
						for mode, kind in nested:
							yield self.nest(mode, kind)
						return
				count = 0
				for kind in ScopeKind.CLASS, ScopeKind.FUNC:
					for index, mode in enumerate(self.mode.nocapt_modes(self.nocapt)):
						if self.only_child in (-1, None, count):
							yield self.nest(mode, kind)
						count += 1

		def makename(self, suffix: str = ''):
			"Name for a nested scope."
			name = 'aA'[self.kind is self.kind.CLASS]
			name = chr(ord(name) + self.level - 1)
			name += suffix
			return self.mode.name_sfx(name)

	class GenTraverse(Traverser):
		""" Common source of builder commands for both Scope and Namespace tree builders.
		Some commands or parameters are only relevant to one of these and ignored by the other.
		Note, the builders have some added methods and method keywords.
		"""

		def __init__(self, static: bool = False):
			super().__init__()
			self.static = static

		def visit(self, src: SrcT):
			""" Builder commands for a single tree, and recursively called for
			nested trees.
			Note, commands applied to the current tree will be interrupted by commands for
			nested trees.
			"""
			name = self.curr.name

			varname = '__x' if self.do_mangle else 'x'
			var = VarName(varname, self.curr)
			nested_params = list(src.nested_params)

			if not nested_params and src.only_child is not None: return

			if not self.curr.is_scope:
				with self.curr.nestEVAL(None, 'e', with_index=False) as self.curr.ev: pass

			#if src.level == 0:
			#	self.anno('xx', 'str')
			#	self.maketest('xxx')
			#	self.decl_global('xxxx')
			#if src.level == 1:
			#	self.decl_global('xxxxx')

			def allvars() -> Iterable[str]:
				""" Generate var plus all mangled names. """
				if self.curr.is_scope:
					yield var
					return

				yield var
				for name2 in sorted(self.scope.mangled_names):
					if name2 != name:
						yield name2

			def do_exec():
				# Modify local x via exec() if possible.

				if self.static: return

				# Make bound using exec().
				rvalue = self.make_rvalue(varname, 'x', exec=True)
				for var2 in allvars():
					self.store_exec(var2, rvalue)
				for var2 in allvars():
					self.maketest(var2)

				# Make unbound using exec().
				for var2 in allvars():
					self.delete_exec(var2)
				for var2 in allvars():
					if self.is_scope or self.scope.exec_effective(var2):
						self.maketest(var2)

			# 1. Prologue.  This is the initial declaration of name.
			mode = src.mode

			for var2 in allvars():
				if mode is mode.Nonlocal:
					if not self.has_closure: return
					self.decl_nonlocal(var2)
				elif mode is mode.Global:
					self.decl_global(var2)
				elif mode is mode.Anno:
					self.anno(var2, 'str')
					#if var2 == varname: self.anno(var2, 'str')
				elif mode is mode.Local:
					self.bind(var2)		# Do this early so that descendants can resolve free x.
				if mode is not mode.Unused:
					self.maketest(var2)

			if self.do_mangle and self.curr.is_scope:
				self.add_mangled(self, varname)


			# 2. Nested classes and functions, with var in the original state.
			def do_nested(sfx: str = ''):
				for sub_ref in nested_params:
					sub_name = sub_ref.makename(sfx)
					if name: sub_name = name + '_' + sub_name
					with self.nest(sub_ref.kind, sub_ref, sub_name):
						self.visit(sub_ref)
			do_nested()

			if mode.modifies:

				# 3. Modifications to var.
				orig_bounds = dict()
				for var2 in allvars():
					orig_bounds[var2] = (
						isinstance(self.curr, Namespace) and self.has_bind(var2) and self.load(var2))

				rvalue = self.make_rvalue(varname, 'x')

				if not self.static:
					for var2, orig_bound in orig_bounds.items():
						# Make unbound.
						if orig_bounds[var2]:
							self.delete(var2)
							self.maketest(var2)

					# Make bound using nested scope.
					if sys.version_info < (3, 8) or self.curr.isCLASS():
						nest_kind = ScopeKind.FUNC; n = f'{name}_setfunc'
					else:
						nest_kind = ScopeKind.COMP; n = f'{name}_setcomp'
					with self.nest(nest_kind, attrs.evolve(src, kind=nest_kind), n) as nested:
						for var2 in allvars():
							self.store_nested(var2, rvalue, mode)
					for var2 in allvars():
						self.maketest(var2)

					# Make unbound using nested scope.
					nest_kind = ScopeKind.FUNC
					n = name + '_' + 'delfunc'
					with self.nest(nest_kind, attrs.evolve(src, kind=nest_kind), n) as f:
						for var2 in allvars():
							self.delete_nested(var2, mode)
					for var2 in allvars():
						self.maketest(var2)

					if self.curr.isOPEN():
						do_exec()

				# Make bound.
				for var2 in allvars():

					self.store(var2, rvalue)
					self.maketest(var2)

				if not self.static:
					# Make unbound.
					for var2 in allvars():
						self.delete(var2)
						self.maketest(var2)

					# Make the opposite state from originally.
					for var2, orig_bound in orig_bounds.items():
						if not orig_bound:
							self.store(var2, rvalue)
							self.maketest(var2)

					# 4. Similar nested classes and functions, with var in the opposite state.
					do_nested('2')

					# 5. Epilogue.  Restore var to its original state.
					for var2, orig_bound in orig_bounds.items():
						if orig_bound: self.store(var2, orig_bound)
						else: self.delete(var2)
						self.maketest(var2)

			else:
				do_exec()


		def make_rvalue(self, var: VarName, name: str, exec: bool = False) -> str:
			""" Make str value to store in variable {name}. """
			if self.curr.is_scope: return ''
			if exec:
				rvalue = self.name
				if rvalue: rvalue += '_exec'
				else: rvalue = 'exec'
			else:
				scope = self.curr.scope
				try: rvalue: str = scope.binding_scope(var).name
				except (AttributeError, SyntaxError): rvalue = ''
			rvalue += '.' + name
			if rvalue.startswith('.'): rvalue = name
			return rvalue

	class GenBuilder(Builder):
		""" Builder subclass to create both the Scopes tree and the Namespaces tree. """

		def __init__(self, *args, **kwds):
			super().__init__(*args, **kwds)
			self.has_closure: Scope | None = None

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
				kind = newtree.kind
				# In a Class scope, nested scopes bypass the Class to find closures.
				# So has_closure will be the same.
				if newtree.isCLASS():
					pass
				elif src:
					mode = src.mode
					if mode in (mode.Local, mode.Anno):
						self.has_closure = self.curr
					if mode is mode.Global:
						self.has_closure = None
				yield newtree
			self.has_closure = save

	class GenScopes(GenBuilder):
		""" Builder subclass to create the Scopes tree. """

		# Special methods used by the traverser...

		@contextmanager
		def nest(self, kind: Scope.Kind, src: ScopeParams, *args, **kwds) -> Iterator[Scope]:

			# push into nested scope.
			with super().nest(kind, src, *args, **kwds) as newtree:
				newtree.mangled_names = set()
				yield
			if newtree.isFUNC() and newtree.name:
				self.use(newtree.name)

		@var_mangle
		def maketest(self, name: VarName):
			if self.src.mode is self.src.mode.Unused: return
			self.curr.use(name)

		@var_mangle
		def store(self, name: VarName, _rvalue: ValT) -> None:
			self.curr.bind(name)

		@var_mangle
		def store_exec(self, name: VarName, _rvalue: ValT) -> None:
			""" Store a value in variable, using an exec() call.
			The compiler won't see this as binding operation. """
			return

		@var_mangle
		def store_nested(self, name: VarName, _rvalue: ValT, parent_mode: VarMode, **kwds) -> None:
			""" Function or Comprehension that stores a value in the parent. """
			if self.isCOMP():
				# Can use a Comrehension with a walrus if Python 3.8 or later and
				#	parent is not a class.
				# FOR NOW: make another nested COMP.
				with self.nestCOMP(None, f'{self.name}_innercomp'):
					with self.use_walrus(): self.bind(name)
			else:
				# Otherwise must use a Function.
				scope = self.curr

				if scope.parent.isCLASS() and parent_mode.is_loc:
					# For a class, it is necessary to find its stack frame and remove from its locals.
					pass
				else:
					if parent_mode is parent_mode.Global or scope.parent.isGLOB():
						self.decl_global(name)
					else:
						self.decl_nonlocal(name)
					self.bind(name)

		@var_mangle
		def delete(self, name: VarName) -> None:
			self.curr.bind(name)

		@var_mangle
		def delete_nested(self, name: VarName, parent_mode: VarMode, **kwds) -> None:
			""" Function to delete the variable from the parent. """
			scope = self.curr

			if scope.parent.isCLASS() and parent_mode.is_loc:
				# For a class with a Local variable, it is necessary to find its stack frame
				#	and remove from its locals.
				pass
			else:
				if parent_mode is parent_mode.Global or scope.parent.isGLOB():
					self.decl_global(name)
				else:
					self.curr.decl_nonlocal(name)
				self.bind(name)

		def delete_exec(self, name: VarName, **kwds) -> None:
			""" delete the variable from the current using exec(). """
			return

		def add_mangled(self, target: Scope, name: VarName):
			""" Add a mangled name to the target scope that name resolves to, if it is an ancestor
			of the class scope.
			"""
			mode = self.src.mode

			# Find the target, using the VarMode.
			if mode is mode.Global:
				target = self.glob
			elif mode is mode.Nonlocal:
				target = self.has_closure
			elif mode in (mode.Used, mode.Unused):
				target = self.has_closure or self.glob
			else:
				return

			# If the target is larger than the class owner, it won't mangle the same way.
			mangled = VarName(name, target)
			n = VarName(name, self)
			if n != mangled:
				target.mangled_names.add(n)
				target.use(n)
				target.bind(n)
				if target.src.mode is mode.Anno:
					target.anno(n, 'str')

		def write(self, s: str): pass

	class GenNamespaces(GenBuilder, NamespaceBuilder):
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
				if newspace.isCLASS():
					self.write(f'class {objname}:')
				elif newspace.isFUNC():
					self.write(f'def {objname}():')
				self.level += 1
				l = self.lineno
				yield newspace
				if l == self.lineno:
					self.write('pass')
				self.level -= 1
				if newspace.isFUNC():
					self.write(f'{objname}()')

		@contextmanager
		def use_parent(self) -> Iterator[Namespace]:
			""" Adjusts the indent level during the context, as well as switching the current tree. """
			self.level -= 1
			with super().use_parent() as parent:
				yield parent
			self.level += 1

		@var_mangle
		def maketest(self, name: VarName):
			""" Generate code to verify expected value of name in current ns at current time. """
			space: Namespace = self.curr
			self.num_tests += 1

			private = name.unmangle(self.scope)

			with space.nestEVAL(None, 'evalcall', with_index=False) as evex:
				try: ev_value = evex.load(name)
				except (SyntaxError, NameError): ev_value = None
			ev_expr = 'locals()'

			if self.src.mode is self.src.mode.Unused:
				self.write(f'test(None, None, {str(name)!r}, {ev_expr}, {ev_value!r}, {self.lineno})')
			else:
				try: value = space.load(name)
				except NameError: value = None
				self.write(f'try:')
				self.write(f'    test({private}, {value!r}, {str(name)!r}, {ev_expr}, {ev_value!r}, {self.lineno})')
				self.write(f'except NameError:')
				self.write(f'    test(None, {value!r}, {str(name)!r}, {ev_expr}, {ev_value!r}, {self.lineno})')

		@var_mangle
		def decl_nonlocal(self, name: VarName):
			private = name.unmangle(self.scope)
			if not self.curr.binder(name):
				# No nonlocal binding.  There are no nested scopes, but generate a test.

				self.write('# No enclosed binding exists.')
				self.write(f'try: compile("nonlocal {private}", "<string>", "exec")')
				self.write(f'except SyntaxError: test(None, None, {str(private)!r}, None, None, {self.lineno})')
				self.write(f'else: error("Enclosed binding exists", {self.lineno})')
				self.num_tests += 1
				return

			self.write(f'nonlocal {private}')

		@var_mangle
		def decl_global(self, name: VarName):
			private = name.unmangle(self.scope)
			self.write(f'global {private}')

		@var_mangle
		def store(self, name: VarName, rvalue: str, **kwds) -> None:
			""" Output python code to store the expected value of '{name}'. """

			private = name.unmangle(self.scope)
			self.write(f'{private} = "{rvalue}"')
			self.curr.store(name, rvalue, **kwds)

		@var_mangle
		def store_nested(self, name: VarName, rvalue: ValT, parent_mode: VarMode, **kwds) -> None:
			""" Output python code to store the expected value of '{name}'. """

			scope = self.scope
			private = name.unmangle(self.scope)
			if self.isCOMP():
				# Can use a Comrehension with a walrus if Python 3.8 or later and
				#	parent is not a class.
				# HOWEVER, if parent is Global mode, a compiler bug croaks on the private name
				#	as a walrus target, but the mangled name is OK.
				# FOR NOW: make another nested COMP.
				with self.nestCOMP(None, 'innercomp'):
					if parent_mode is parent_mode.Global and name.mangled:
						comm = ' # (mangled target name needed due to compiler bug)'
						private = VarName(name, scope)
					else: comm = ''
					comp = f'[{(private)} := _ for _ in ["{rvalue}"]]'
					# The outer comprehension.
					comp = f'[0 for _ in [0] if 0 in {comp}]'

					with self.use_parent():
						with self.use_parent():
							self.write(f'{comp}{comm}')
					self.curr.store_walrus(name, rvalue)
			else:
				if scope.parent.isCLASS() and parent_mode.is_loc:
					# For a class, it is necessary to find its stack frame and store in its locals.
					self.write(f'inspect.stack()[1].frame.f_locals["{name}"] = "{rvalue}"')
				else:
					if parent_mode is parent_mode.Global:
						self.write(f'global {private}; {private} = "{rvalue}"')
					else:
						self.write(f'nonlocal {private}; {private} = "{rvalue}"')
				with self.use_parent():
					self.curr.store(name, rvalue)

		@var_mangle
		def store_exec(self, name: VarName, rvalue: str, **kwds) -> None:
			""" Output python code to store the expected value of '{name}'.
			This uses an exec() call.
			"""
			# Sometimes, exec() will have no effect.

			effect = self.scope.exec_effective(name)
			if effect:
				comment = ''
			else:
				comment = f'\t# Has no effect on {name!r} or locals()'
			self.write(f'exec(\'{name} = "{rvalue}"\'){comment}')
			if effect:
				self.curr.vars.bind(name, rvalue)

		@var_mangle
		def delete(self, name: VarName, **kwds) -> None:
			private = name.unmangle(self.scope)
			self.write(f'del {private}')
			self.curr.delete(name, **kwds)

		@var_mangle
		def delete_nested(self, name: VarName, parent_mode: VarMode, **kwds) -> None:
			""" Write code to delete value in parent.  There are no nested scopes.
			"""
			scope = self.scope

			if scope.parent.isCLASS() and parent_mode.is_loc:
				# For a class with a Local variable, it is necessary to find its stack frame
				#	and remove from its locals.
				self.write(f'del inspect.stack()[1].frame.f_locals["{name}"]')
			else:
				private = name.unmangle(self.scope)
				if parent_mode is parent_mode.Global or self.parent.isGLOB():
					self.write(f'global {private}; del {private}')
				else:
					self.write(f'nonlocal {private}; del {private}')
			with self.use_parent():
				self.curr.delete(name)

		@var_mangle
		def delete_exec(self, name: VarName, **kwds) -> None:
			if self.scope.exec_effective(name):
				self.write(f'exec("del {name}")')
				self.curr.vars.unbind(name)

		@var_mangle
		def anno(self, name: VarName, anno) -> Self:
			self.curr.anno(name, anno)
			if isinstance(anno, str):
				s = anno
			else:
				s = str(anno)
			private = name.unmangle(self.scope)
			self.write(f'{private}: {s}')


		def write(self, s: str):
			print('    ' * self.level + s, file=out)
			self.lineno += len(s.split('\n'))


	def gen(args, out: TextIO, prolog: list[str], mangle: bool = False, only_child: int | None = None) -> Tuple[int, Namespace]:
		""" Main function to write most of the output. """

		print(f'Generating code... ', end='', flush=True)
		top_ref = ScopeParams(0, args.d, VarMode.Local, only_child=only_child)
		scope = Scope(kind=ScopeKind.GLOB, cache_resolved=False, src=top_ref)
		trav = GenTraverse(static=args.static)
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


	out = StringIO()
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', default = 3, type=int, choices=range(2, 5),
		help='Depth of the scopes and namespaces tree (default 3)')
	parser.add_argument('-s', action='store_true', help='Save the output file')
	parser.add_argument('-t', action='store_true', help='Copy the output file to file with ".txt" appended to the name')
	parser.add_argument('-o', default='sc_test.py', help='Output file name (default "sc_test.py")')
	parser.add_argument('--nomangle', action='store_true', help='Skip tests with mangled names')
	parser.add_argument('--mangle', action='store_true', help='Only tests with mangled names')
	parser.add_argument('--static', action='store_true', help='Only tests for static properties')

	args = parser.parse_args()

	import ast
	from . import treebuild
	with open('x.py') as f:
		src = ast.parse(f.read())
	root = GlobalNamespace(src=src)
	trav = treebuild.ASTTraverser()
	build = treebuild.NamespaceBuilder(root, trav, indexed=True)
	build.build()

	prolog = (
'''from __future__ import annotations
from __future__ import annotations
import inspect, sys
ntests = 0
def test(value: str | None, comp: str | None, name: VarName, locs: dict[str, Any], ev_comp: str | None, lineno: int):
	if value != comp:
		raise ValueError(f'Line {lineno}: expected {comp!r}, got {value!r}.', lineno) from None
	try: ev_val = eval(name, globals(), locs)
	except NameError: ev_val = None
	if ev_val != ev_comp:
		raise ValueError(f'Line {lineno}: eval() expected {ev_comp!r}, got {ev_val!r}.', lineno) from None
	global ntests
	ntests += 1
	if ntests % 1000 == 0:
		print('\\r' f'{ntests}', end='')

def ev(name: str, globs: dict, locs: dict) -> str | None:
    try: return eval(name, globs, locs)
    except NameError: return None

def error(msg: str, lineno: int):
	raise ValueError(f'Line {lineno}: {msg}.', lineno) from None

''').splitlines()

	def symtab_test(scope: Scope):
		import symtable as st
		# Table for module level.
		stab = st.symtable(out.getvalue(), 'mod.py', 'exec')

		def test(scope: Scope, stab: SymbolTable):
			#print('  ' * scope.nest_depth() + scope.name)
			# Check all the symbols
			syms: list = stab.get_symbols()
			import operator
			syms.sort(key=operator.methodcaller('get_name'))
			vars: dict = scope.scope.vars

			for sym in syms:
				name = sym.get_name()
				try: var: VarUse = vars[name]
				except KeyError:
					assert name in 'test eval exec locals NameError str inspect _ .0'.split(), name
					continue
				# Compare sym with var in scope.
				del vars[name]
				try:
					assert (var.hasFREE() or var.hasCELL())  == sym.is_free(), 'FREE'
					if scope.isGLOB():
						assert sym.is_global(), 'GLOBAL'
						assert var.hasBINDING()  == sym.is_local(), 'LOCAL'
					else:
						assert var.hasGLOBAL()  == sym.is_global(), 'GLOBAL'
						assert var.hasLOCAL()  == sym.is_local(), 'LOCAL'
					assert var.hasUSE()  == sym.is_referenced(), 'USE'
					assert var.hasNESTED()  == bool(sym.get_namespaces()), 'NESTED'
					assert var.hasPARAM()  == sym.is_parameter(), 'PARAM'
					assert var.hasNLOC_DECL()  == sym.is_nonlocal(), 'NLOC_DECL'
					assert var.hasGLOB_DECL()  == sym.is_declared_global(), 'GLOB_DECL'
					assert var.hasANNO()  == sym.is_annotated(), 'ANNO'
					assert var.hasIMPORT()  == sym.is_imported(), 'IMPORT'
					assert var.hasBINDING()  == sym.is_assigned(), 'BINDING'
				except Exception as e:
					print(f'Mismatched {scope!r} {e} {name} {var.ctx!r} {hex(sym._Symbol__flags)}')
					for n in dir(sym):
						if n.startswith('_'): continue
						try:
							value = getattr(sym, n)()
							if value: print(f'{n} = {value}')
						except: pass

			for var in vars.values():
				if var.hasGLOBAL() and var.hasWALRUS(): continue
				assert 0, (scope, var)

			# Recursively do nested items.
			nested = scope.nested
			nested_names = ['listcomp' if n.isCOMP() else str(n.name) for n in nested]
			child_names = [child._table.name for child in stab.get_children()]
			assert nested_names == child_names, (scope, stab)

			for n, c in zip(nested, stab.get_children()):
				test(n, c)
			x = 0
		test(scope, stab)
		x = 0

	def run_test(mangle: bool = False, only_child: int | None = None) -> str:
		global out
		if args.d == 4 and only_child is None:
			# Perform several shorter tests each with a different only child index.
			top_ref = ScopeParams(0, args.d, VarMode.Local, only_child=-1)
			nested = list(top_ref.nested_params)
			text_count = 0
			result = ''
			for only_child, params in enumerate(nested):
				name = params.mode.name_sfx('aA'[params.kind.is_class])
				print(f'{only_child + 1} of {len(nested)} ({name}).')
				text = run_test(mangle, only_child)
				if text: text_count += 1; result = text
			return result if text_count == 1 else ''
		num_tests, root_ns = gen(args, out, prolog, mangle=mangle, only_child=only_child)
		if num_tests == 0: return ''
		print('Compiling... ', end='', flush=True)
		lines = [*prolog, *out.getvalue().splitlines()]
		if args.d < 4 and args.static:root_ns.scope.dump_vars()
		try: symtab_test(root_ns.scope)
		except:
			print()
			import traceback
			traceback.print_exc()
			with open('mod.py', 'w') as m:
				m.write('\n'.join(lines))
			print ('\a')
			return out.getvalue()

		import ast
		try: code = compile('\n'.join(lines), '<generated>', 'exec')
		except:
			print ('\a')
			import traceback
			traceback.print_exc()
			return out.getvalue()

		print('done')
		print('Running tests. ')
		with open('mod.py', 'w') as m:
			m.write('\n'.join(lines))
		import importlib
		try: importlib.import_module('mod')
		except ValueError as exc:
			print()
			msg, lineno = exc.args
			lines = out.getvalue().splitlines()
			print(*lines[max(lineno - 11, 0):lineno], sep='\n')
			print('\a---- ' + msg)
			print(*lines[lineno: lineno + 10], sep='\n')
			return out.getvalue()
		else:
			if num_tests % 1000: print('\r' f'{num_tests}', end='', flush=True)
			print(' done')
			print(f'All {num_tests} tests passed.')

		# Regression test.  Generate trees from the output code.
		print('Analyzing output file...', end='', flush=True)
		from . import treebuild
		import ast
		src = ast.parse(out.getvalue())
		root = GlobalNamespace(src=src)
		trav = treebuild.ASTTraverser()
		build = treebuild.NamespaceBuilder(root, trav, indexed=True)
		try:
			build.build()
			print('')
			x = 0
			from itertools import zip_longest
			var = '__x' if mangle else 'x'
			# Compare the scopes trees.
			def compare(scope1, scope2) -> bool:
				if scope1.name != scope2.name:
					if not scope2.isCOMP():
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
			print('')
			# Compare the namespace trees.
			def compare(ns1, ns2) -> bool:
				if ns1.name != ns2.name and ns1.kind is not ns1.COMP:
					raise ValueError(f"Namespaces {ns1!r} and {ns2!r} don't match")
				nest1 = ns1.nested
				nest2 = ns2.nested
				if len(nest1) != len(nest1):
					print ('\a')
					raise ValueError(f"Namespaces {ns1!r} and {ns2!r} don't match")
				for ns1, ns2 in zip(nest1, nest2):
					compare(ns1, ns2)
			print('Comparing namespaces...', end='', flush=True)
			print('')
		except:
			import traceback
			traceback.print_exc()

		return out.getvalue()

	text = ''
	if not args.mangle:
		print('Testing.')
		text += run_test()
	if not args.nomangle:
		print('Testing mangled names.')
		text += run_test(mangle=True)
	filename = args.o
	if text:
		if args.s:
			with open(filename, 'w') as f:
				any(print(line, file=f) for line in prolog)
				f.write(text)
				print(f'Writing to "{f.name}."')
		if args.t:
			with open(f'{filename}.txt', 'w') as f:
				any(print(line, file=f) for line in prolog)
				f.write(text)
				print(f'Writing to "{f.name}."')
