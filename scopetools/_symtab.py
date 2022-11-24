""" Module _symtab

Some utilities wrapping around the standard library 'symtable' module.

The SymTab and Sym classes are subclasses of corresponding classes in symtable.
"""

from __future__ import annotations

import symtable as stmod

__all__ = ['SymTab']

# Collect type and usage names.
types: dict[str, int] = dict()
flags: dict[str, int] = dict()

for name, value in vars(stmod).items():
	import re
	if re.fullmatch('[A-Z_]+', name):
		if name in 'CELL FREE LOCAL GLOBAL_IMPLICIT GLOBAL_EXPLICIT'.split():
			types[name] = value
		elif not name.startswith('SCOPE_'):
			flags[name] = value


class SymTab(stmod.SymbolTable):

	count = 0

	def __new__(cls, filename: str = '<string>', code: str = ''):
		""" Top-level SymTab.  Make from either the python code or the name of a module file. """
		if not code and filename != '<string>':
			# Read the file to get the code.
			if not filename.endswith('.py'): filename += '.py'
			with open(filename) as f:
				code = f.read()
		symtab = stmod.symtable(code, filename, 'exec')
		symtab.__class__ = SymTab
		return symtab

	def __init__(self, *args, **kwds):
		__class__.count += 1
		pass

	def __getitem__(self, name: str) -> SymTab:
		""" Gets Sym for given name, or raise KeyError """
		sym = self.lookup(name)
		sym.__class__ = Sym
		return sym

	@property
	def syms(self) -> Iterable[Sym]:
		syms = self.get_symbols()
		for sym in syms:
			sym.__class__ = Sym
		return syms

	@property
	def children(self) -> Iterable[SymTab]:
		""" List of nested tables, reclassed as SymTab """
		children = self.get_children()
		for child in children:
			child.__class__ = SymTab
		return children

	def child(self, *keys: str | int) -> SymTab:
		if not keys: keys = [0]
		for key in keys:
			children = self.children
			if isinstance(key, int):
				self = children[key]
				continue
			# key is child's name
			for child in children:
				if child.get_name() == key:
					self = child
					break
			else:
				# No match
				raise KeyError(name)
		return self

	def show(self, name: str = '', all: bool = False, leader: str = '', **kwds) -> None:
		#print(f'{leader}SymbolTable ({self.count}) {self!r}', **kwds)
		print(f'{leader}SymbolTable {self.get_name()}', **kwds)
		leader += '  '
		for sym in self.syms:
			if not name or name == sym.name:
				sym.show(leader, **kwds)
		if all:
			for child in self.children:
				child.show('', all=all, leader=leader)

	def showall(self) -> None:
		self.show('', all=True)

class Sym(stmod.Symbol):

	@property
	def name(self) -> str: return self.get_name()

	def show(self, leader: str = '', **kwds) -> None:
		flags_: int = self._Symbol__flags
		type: int = flags_ >> stmod.SCOPE_OFF
		flags_ -= type << stmod.SCOPE_OFF
		print(f'{leader}Symbol {self.get_name()}', end='', **kwds)
		for name, value in types.items():
			if type == value: print('', name, end='', **kwds)
		for name, value in flags.items():
			if flags_ & value: print('', name, end='', **kwds)
		print(**kwds)
		for n in dir(self):
			if n.startswith('_'): continue
			try: v = getattr(super(), n)()
			except: continue
			if v: print(f'{leader}  {n}() = {v}')

symtab = SymTab(code='x = 2\ndef f(n): pass\nclass f: pass')
sym = symtab['x']

#symtab.show()
symtab.child()
symtab.showall()
#sym.show()
#SymTab('scopetools/_symtab').showall()



