""" Package with various tools to analyze scope and name resolution in a Python program. """

import scopetools

if __name__ != '__main__':

	from .scope_common import(
		mangle,
		ScopeTree)
