class A:
    def A_b():
        exec('_A__x = "A_b_exec.x"')
        test(None, None, '_A__x', locals(), 'A_b_exec.x', 602)
        exec("del _A__x")
        test(None, None, '_A__x', locals(), None, 604)
    A_b()
    def A_b_use():
        try:
            test(__x, None, '_A__x', locals(), None, 608)
        except NameError:
            test(None, None, '_A__x', locals(), None, 610)
        exec('_A__x = "A_b_use_exec.x"')
        try:
            test(__x, None, '_A__x', locals(), 'A_b_use_exec.x', 613)
        except NameError:
            test(None, None, '_A__x', locals(), 'A_b_use_exec.x', 615)
        exec("del _A__x")
        try:
            test(__x, None, '_A__x', locals(), None, 618)
        except NameError:
            test(None, None, '_A__x', locals(), None, 620)
    A_b_use()
