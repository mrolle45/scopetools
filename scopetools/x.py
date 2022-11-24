class A:
    def A_b_anno():
        __x: str
        def A_b_anno_c_nloc():
            nonlocal __x
            try:
                test(__x, None, '_A__x', locals(), None, 9830)
            except NameError:
                test(None, None, '_A__x', locals(), None, 9832)
            [0 for _ in [0] if 0 in [__x := _ for _ in ["x"]]]
            try:
                test(__x, 'x', '_A__x', locals(), 'x', 9835)
            except NameError:
                test(None, 'x', '_A__x', locals(), 'x', 9837)
            def A_b_anno_c_nloc_delfunc():
                nonlocal __x; del __x
            A_b_anno_c_nloc_delfunc()
            try:
                test(__x, None, '_A__x', locals(), None, 9842)
            except NameError:
                test(None, None, '_A__x', locals(), None, 9844)
            __x = "x"
            try:
                test(__x, 'x', '_A__x', locals(), 'x', 9847)
            except NameError:
                test(None, 'x', '_A__x', locals(), 'x', 9849)
            del __x
            try:
                test(__x, None, '_A__x', locals(), None, 9852)
            except NameError:
                test(None, None, '_A__x', locals(), None, 9854)
            __x = "x"
            try:
                test(__x, 'x', '_A__x', locals(), 'x', 9857)
            except NameError:
                test(None, 'x', '_A__x', locals(), 'x', 9859)
            del __x
            try:
                test(__x, None, '_A__x', locals(), None, 9862)
            except NameError:
                test(None, None, '_A__x', locals(), None, 9864)
        A_b_anno_c_nloc()

