a = b = c = d = e = f = 'glob'
a2 = b2 = c2 = d2 = e2 = f2 = 'glob'		# Names not in outer()

def outer(f = 'outerparam'):
	a = b = c = d = e = 'outer'

	class Inner:
		print('in class...')
		global a, a2
		nonlocal b		# Not b2.
		c = c2 = 'Inner'
		d: str
		(d2): str

		pd(locals())
		print(a, b, c, d, e, f)
		print(a2, b2, c2, d2, e2, f2)
		print()

		for var in 'a b c d e f'.split():
			exec(f'{var} = "extra"')
			exec(f'{var}2 = "extra"')
		del var
		pd(locals())
		print(a, b, c, d, e, f)
		print(a2, b2, c2, d2, e2, f2)

	pd(Inner.__dict__)

	def inner(f = 'innerparam'):
		print()
		print('in function...')
		global a, a2
		nonlocal b		# Not b2.
		c = c2 = 'inner'
		d: str
		(d2): str

		pd(locals())
		print(a, b, c, 'dx', e, f)
		print(a2, b2, c2, d2, e2, f2)
		print()

		for var in 'a b c d e f'.split():
			exec(f'{var} = "extra"')
			exec(f'{var}2 = "extra"')
		del var
		pd(locals())
		print(a, b, c, 'dx', e, f)
		print(a2, b2, c2, d2, e2, f2)

	inner()

def pd(d: dict):
	for name in sorted(d):
		print(f'{name} -> {d[name]!r}')