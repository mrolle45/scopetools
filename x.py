def f():
	x = 1
	y = 2
	class A:
		nonlocal x
		def g():
			nonlocal y
			print(y)
		y = 3
		x
		print(y)
	return A

