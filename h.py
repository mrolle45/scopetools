import ast
import dis
import inspect
import sys
import importlib

def dd(obj, out: str = None, **kwds):
	if out:
		dis.dis(obj, file=open(out, 'w'), **kwds)
	else:
		dis.dis(obj, **kwds)

def reimp(mod):
	importlib.reload(mod)
	glob = inspect.stack()[1].frame.f_locals
	exec(f'from {mod.__name__} import *', glob)

def adp(s: str):
	print(ast.dump(ast.parse(s, type_comments=True),
				indent=4))
def adpf(f: str = 'x.py'):
	adp(rf(f))
def rf(f: str = 'x.py'):
	if not f.endswith('.py'): f += '.py'
	file = open(f)
	return file.read()
def ia(mod):
	print(f'from {mod.__name__} import *')
	exec(f'from {mod.__name__} import *', globals())

def ddf(f: str = 'x.py', out: str = None, **kwds):
	if not f.endswith('.py'): f += '.py'
	s = rf(f)
	dd(compile(s, f, 'exec'), out, **kwds)

ntests = 0
def test(value: str, comp: str, lineno: int):
	if value != comp:
		raise ValueError(f'Line {lineno}: expected {comp!r}, got {value!r}.', lineno) from None
	global ntests
	ntests += 1
	if ntests % 1000 == 0:
		print('\\r' f'{ntests}', end='')

def error(msg: str, lineno: int):
	raise ValueError(f'Line {lineno}: {msg}.', lineno) from None

