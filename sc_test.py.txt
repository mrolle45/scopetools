
try: test(x, None, 2)
except NameError: test(None, None, 3)
class A:
    class A_B:
        pass
    class A_B_use:
        try: test(x, None, 8)
        except NameError: test(None, None, 9)
    class A_B_anno:
        x: str
        try: test(x, None, 12)
        except NameError: test(None, None, 13)
    class A_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 17)
        else: error("Enclosed binding exists", 18)
    class A_B_glob:
        global x
        try: test(x, None, 21)
        except NameError: test(None, None, 22)
        def A_B_glob_setfunc():
            global x; x = "x"
        A_B_glob_setfunc()
        try: test(x, 'x', 26)
        except NameError: test(None, 'x', 27)
        def A_B_glob_delfunc():
            global x; del x
        A_B_glob_delfunc()
        try: test(x, None, 31)
        except NameError: test(None, None, 32)
        x = "x"
        try: test(x, 'x', 34)
        except NameError: test(None, 'x', 35)
        del x
        try: test(x, None, 37)
        except NameError: test(None, None, 38)
    class A_B_loc:
        try: test(x, None, 40)
        except NameError: test(None, None, 41)
        def A_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_B_loc.x"
        A_B_loc_setfunc()
        try: test(x, 'A_B_loc.x', 45)
        except NameError: test(None, 'A_B_loc.x', 46)
        def A_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_B_loc_delfunc()
        try: test(x, None, 50)
        except NameError: test(None, None, 51)
        x = "A_B_loc.x"
        try: test(x, 'A_B_loc.x', 53)
        except NameError: test(None, 'A_B_loc.x', 54)
        del x
        try: test(x, None, 56)
        except NameError: test(None, None, 57)
    class A_B_ncap:
        try: test(x, None, 59)
        except NameError: test(None, None, 60)
        def A_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_B_ncap.x"
        A_B_ncap_setfunc()
        try: test(x, 'A_B_ncap.x', 64)
        except NameError: test(None, 'A_B_ncap.x', 65)
        def A_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_B_ncap_delfunc()
        try: test(x, None, 69)
        except NameError: test(None, None, 70)
        x = "A_B_ncap.x"
        try: test(x, 'A_B_ncap.x', 72)
        except NameError: test(None, 'A_B_ncap.x', 73)
        del x
        try: test(x, None, 75)
        except NameError: test(None, None, 76)
    def A_b():
        pass
    A_b()
    def A_b_use():
        try: test(x, None, 81)
        except NameError: test(None, None, 82)
    A_b_use()
    def A_b_anno():
        x: str
        try: test(x, None, 86)
        except NameError: test(None, None, 87)
    A_b_anno()
    def A_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 92)
        else: error("Enclosed binding exists", 93)
    A_b_nloc()
    def A_b_glob():
        global x
        try: test(x, None, 97)
        except NameError: test(None, None, 98)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 100)
        except NameError: test(None, 'x', 101)
        def A_b_glob_delfunc():
            global x; del x
        A_b_glob_delfunc()
        try: test(x, None, 105)
        except NameError: test(None, None, 106)
        x = "x"
        try: test(x, 'x', 108)
        except NameError: test(None, 'x', 109)
        del x
        try: test(x, None, 111)
        except NameError: test(None, None, 112)
    A_b_glob()
    def A_b_loc():
        try: test(x, None, 115)
        except NameError: test(None, None, 116)
        [x := _ for _ in ["A_b_loc.x"]]
        try: test(x, 'A_b_loc.x', 118)
        except NameError: test(None, 'A_b_loc.x', 119)
        def A_b_loc_delfunc():
            nonlocal x; del x
        A_b_loc_delfunc()
        try: test(x, None, 123)
        except NameError: test(None, None, 124)
        x = "A_b_loc.x"
        try: test(x, 'A_b_loc.x', 126)
        except NameError: test(None, 'A_b_loc.x', 127)
        del x
        try: test(x, None, 129)
        except NameError: test(None, None, 130)
    A_b_loc()
    def A_b_ncap():
        try: test(x, None, 133)
        except NameError: test(None, None, 134)
        [x := _ for _ in ["A_b_ncap.x"]]
        try: test(x, 'A_b_ncap.x', 136)
        except NameError: test(None, 'A_b_ncap.x', 137)
        def A_b_ncap_delfunc():
            nonlocal x; del x
        A_b_ncap_delfunc()
        try: test(x, None, 141)
        except NameError: test(None, None, 142)
        x = "A_b_ncap.x"
        try: test(x, 'A_b_ncap.x', 144)
        except NameError: test(None, 'A_b_ncap.x', 145)
        del x
        try: test(x, None, 147)
        except NameError: test(None, None, 148)
    A_b_ncap()
class A_use:
    try: test(x, None, 151)
    except NameError: test(None, None, 152)
    class A_use_B:
        pass
    class A_use_B_use:
        try: test(x, None, 156)
        except NameError: test(None, None, 157)
    class A_use_B_anno:
        x: str
        try: test(x, None, 160)
        except NameError: test(None, None, 161)
    class A_use_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 165)
        else: error("Enclosed binding exists", 166)
    class A_use_B_glob:
        global x
        try: test(x, None, 169)
        except NameError: test(None, None, 170)
        def A_use_B_glob_setfunc():
            global x; x = "x"
        A_use_B_glob_setfunc()
        try: test(x, 'x', 174)
        except NameError: test(None, 'x', 175)
        def A_use_B_glob_delfunc():
            global x; del x
        A_use_B_glob_delfunc()
        try: test(x, None, 179)
        except NameError: test(None, None, 180)
        x = "x"
        try: test(x, 'x', 182)
        except NameError: test(None, 'x', 183)
        del x
        try: test(x, None, 185)
        except NameError: test(None, None, 186)
    class A_use_B_loc:
        try: test(x, None, 188)
        except NameError: test(None, None, 189)
        def A_use_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_use_B_loc.x"
        A_use_B_loc_setfunc()
        try: test(x, 'A_use_B_loc.x', 193)
        except NameError: test(None, 'A_use_B_loc.x', 194)
        def A_use_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_use_B_loc_delfunc()
        try: test(x, None, 198)
        except NameError: test(None, None, 199)
        x = "A_use_B_loc.x"
        try: test(x, 'A_use_B_loc.x', 201)
        except NameError: test(None, 'A_use_B_loc.x', 202)
        del x
        try: test(x, None, 204)
        except NameError: test(None, None, 205)
    class A_use_B_ncap:
        try: test(x, None, 207)
        except NameError: test(None, None, 208)
        def A_use_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_use_B_ncap.x"
        A_use_B_ncap_setfunc()
        try: test(x, 'A_use_B_ncap.x', 212)
        except NameError: test(None, 'A_use_B_ncap.x', 213)
        def A_use_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_use_B_ncap_delfunc()
        try: test(x, None, 217)
        except NameError: test(None, None, 218)
        x = "A_use_B_ncap.x"
        try: test(x, 'A_use_B_ncap.x', 220)
        except NameError: test(None, 'A_use_B_ncap.x', 221)
        del x
        try: test(x, None, 223)
        except NameError: test(None, None, 224)
    def A_use_b():
        pass
    A_use_b()
    def A_use_b_use():
        try: test(x, None, 229)
        except NameError: test(None, None, 230)
    A_use_b_use()
    def A_use_b_anno():
        x: str
        try: test(x, None, 234)
        except NameError: test(None, None, 235)
    A_use_b_anno()
    def A_use_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 240)
        else: error("Enclosed binding exists", 241)
    A_use_b_nloc()
    def A_use_b_glob():
        global x
        try: test(x, None, 245)
        except NameError: test(None, None, 246)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 248)
        except NameError: test(None, 'x', 249)
        def A_use_b_glob_delfunc():
            global x; del x
        A_use_b_glob_delfunc()
        try: test(x, None, 253)
        except NameError: test(None, None, 254)
        x = "x"
        try: test(x, 'x', 256)
        except NameError: test(None, 'x', 257)
        del x
        try: test(x, None, 259)
        except NameError: test(None, None, 260)
    A_use_b_glob()
    def A_use_b_loc():
        try: test(x, None, 263)
        except NameError: test(None, None, 264)
        [x := _ for _ in ["A_use_b_loc.x"]]
        try: test(x, 'A_use_b_loc.x', 266)
        except NameError: test(None, 'A_use_b_loc.x', 267)
        def A_use_b_loc_delfunc():
            nonlocal x; del x
        A_use_b_loc_delfunc()
        try: test(x, None, 271)
        except NameError: test(None, None, 272)
        x = "A_use_b_loc.x"
        try: test(x, 'A_use_b_loc.x', 274)
        except NameError: test(None, 'A_use_b_loc.x', 275)
        del x
        try: test(x, None, 277)
        except NameError: test(None, None, 278)
    A_use_b_loc()
    def A_use_b_ncap():
        try: test(x, None, 281)
        except NameError: test(None, None, 282)
        [x := _ for _ in ["A_use_b_ncap.x"]]
        try: test(x, 'A_use_b_ncap.x', 284)
        except NameError: test(None, 'A_use_b_ncap.x', 285)
        def A_use_b_ncap_delfunc():
            nonlocal x; del x
        A_use_b_ncap_delfunc()
        try: test(x, None, 289)
        except NameError: test(None, None, 290)
        x = "A_use_b_ncap.x"
        try: test(x, 'A_use_b_ncap.x', 292)
        except NameError: test(None, 'A_use_b_ncap.x', 293)
        del x
        try: test(x, None, 295)
        except NameError: test(None, None, 296)
    A_use_b_ncap()
class A_anno:
    x: str
    try: test(x, None, 300)
    except NameError: test(None, None, 301)
    class A_anno_B:
        pass
    class A_anno_B_use:
        try: test(x, None, 305)
        except NameError: test(None, None, 306)
    class A_anno_B_anno:
        x: str
        try: test(x, None, 309)
        except NameError: test(None, None, 310)
    class A_anno_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 314)
        else: error("Enclosed binding exists", 315)
    class A_anno_B_glob:
        global x
        try: test(x, None, 318)
        except NameError: test(None, None, 319)
        def A_anno_B_glob_setfunc():
            global x; x = "x"
        A_anno_B_glob_setfunc()
        try: test(x, 'x', 323)
        except NameError: test(None, 'x', 324)
        def A_anno_B_glob_delfunc():
            global x; del x
        A_anno_B_glob_delfunc()
        try: test(x, None, 328)
        except NameError: test(None, None, 329)
        x = "x"
        try: test(x, 'x', 331)
        except NameError: test(None, 'x', 332)
        del x
        try: test(x, None, 334)
        except NameError: test(None, None, 335)
    class A_anno_B_loc:
        try: test(x, None, 337)
        except NameError: test(None, None, 338)
        def A_anno_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_anno_B_loc.x"
        A_anno_B_loc_setfunc()
        try: test(x, 'A_anno_B_loc.x', 342)
        except NameError: test(None, 'A_anno_B_loc.x', 343)
        def A_anno_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_anno_B_loc_delfunc()
        try: test(x, None, 347)
        except NameError: test(None, None, 348)
        x = "A_anno_B_loc.x"
        try: test(x, 'A_anno_B_loc.x', 350)
        except NameError: test(None, 'A_anno_B_loc.x', 351)
        del x
        try: test(x, None, 353)
        except NameError: test(None, None, 354)
    class A_anno_B_ncap:
        try: test(x, None, 356)
        except NameError: test(None, None, 357)
        def A_anno_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_anno_B_ncap.x"
        A_anno_B_ncap_setfunc()
        try: test(x, 'A_anno_B_ncap.x', 361)
        except NameError: test(None, 'A_anno_B_ncap.x', 362)
        def A_anno_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_anno_B_ncap_delfunc()
        try: test(x, None, 366)
        except NameError: test(None, None, 367)
        x = "A_anno_B_ncap.x"
        try: test(x, 'A_anno_B_ncap.x', 369)
        except NameError: test(None, 'A_anno_B_ncap.x', 370)
        del x
        try: test(x, None, 372)
        except NameError: test(None, None, 373)
    def A_anno_b():
        pass
    A_anno_b()
    def A_anno_b_use():
        try: test(x, None, 378)
        except NameError: test(None, None, 379)
    A_anno_b_use()
    def A_anno_b_anno():
        x: str
        try: test(x, None, 383)
        except NameError: test(None, None, 384)
    A_anno_b_anno()
    def A_anno_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 389)
        else: error("Enclosed binding exists", 390)
    A_anno_b_nloc()
    def A_anno_b_glob():
        global x
        try: test(x, None, 394)
        except NameError: test(None, None, 395)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 397)
        except NameError: test(None, 'x', 398)
        def A_anno_b_glob_delfunc():
            global x; del x
        A_anno_b_glob_delfunc()
        try: test(x, None, 402)
        except NameError: test(None, None, 403)
        x = "x"
        try: test(x, 'x', 405)
        except NameError: test(None, 'x', 406)
        del x
        try: test(x, None, 408)
        except NameError: test(None, None, 409)
    A_anno_b_glob()
    def A_anno_b_loc():
        try: test(x, None, 412)
        except NameError: test(None, None, 413)
        [x := _ for _ in ["A_anno_b_loc.x"]]
        try: test(x, 'A_anno_b_loc.x', 415)
        except NameError: test(None, 'A_anno_b_loc.x', 416)
        def A_anno_b_loc_delfunc():
            nonlocal x; del x
        A_anno_b_loc_delfunc()
        try: test(x, None, 420)
        except NameError: test(None, None, 421)
        x = "A_anno_b_loc.x"
        try: test(x, 'A_anno_b_loc.x', 423)
        except NameError: test(None, 'A_anno_b_loc.x', 424)
        del x
        try: test(x, None, 426)
        except NameError: test(None, None, 427)
    A_anno_b_loc()
    def A_anno_b_ncap():
        try: test(x, None, 430)
        except NameError: test(None, None, 431)
        [x := _ for _ in ["A_anno_b_ncap.x"]]
        try: test(x, 'A_anno_b_ncap.x', 433)
        except NameError: test(None, 'A_anno_b_ncap.x', 434)
        def A_anno_b_ncap_delfunc():
            nonlocal x; del x
        A_anno_b_ncap_delfunc()
        try: test(x, None, 438)
        except NameError: test(None, None, 439)
        x = "A_anno_b_ncap.x"
        try: test(x, 'A_anno_b_ncap.x', 441)
        except NameError: test(None, 'A_anno_b_ncap.x', 442)
        del x
        try: test(x, None, 444)
        except NameError: test(None, None, 445)
    A_anno_b_ncap()
class A_nloc:
    # No enclosed binding exists.
    try: compile("nonlocal x", "<string>", "exec")
    except SyntaxError: test(None, None, 450)
    else: error("Enclosed binding exists", 451)
class A_glob:
    global x
    try: test(x, None, 454)
    except NameError: test(None, None, 455)
    class A_glob_B:
        pass
    class A_glob_B_use:
        try: test(x, None, 459)
        except NameError: test(None, None, 460)
    class A_glob_B_anno:
        x: str
        try: test(x, None, 463)
        except NameError: test(None, None, 464)
    class A_glob_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 468)
        else: error("Enclosed binding exists", 469)
    class A_glob_B_glob:
        global x
        try: test(x, None, 472)
        except NameError: test(None, None, 473)
        def A_glob_B_glob_setfunc():
            global x; x = "x"
        A_glob_B_glob_setfunc()
        try: test(x, 'x', 477)
        except NameError: test(None, 'x', 478)
        def A_glob_B_glob_delfunc():
            global x; del x
        A_glob_B_glob_delfunc()
        try: test(x, None, 482)
        except NameError: test(None, None, 483)
        x = "x"
        try: test(x, 'x', 485)
        except NameError: test(None, 'x', 486)
        del x
        try: test(x, None, 488)
        except NameError: test(None, None, 489)
    class A_glob_B_loc:
        try: test(x, None, 491)
        except NameError: test(None, None, 492)
        def A_glob_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_glob_B_loc.x"
        A_glob_B_loc_setfunc()
        try: test(x, 'A_glob_B_loc.x', 496)
        except NameError: test(None, 'A_glob_B_loc.x', 497)
        def A_glob_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_glob_B_loc_delfunc()
        try: test(x, None, 501)
        except NameError: test(None, None, 502)
        x = "A_glob_B_loc.x"
        try: test(x, 'A_glob_B_loc.x', 504)
        except NameError: test(None, 'A_glob_B_loc.x', 505)
        del x
        try: test(x, None, 507)
        except NameError: test(None, None, 508)
    class A_glob_B_ncap:
        try: test(x, None, 510)
        except NameError: test(None, None, 511)
        def A_glob_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_glob_B_ncap.x"
        A_glob_B_ncap_setfunc()
        try: test(x, 'A_glob_B_ncap.x', 515)
        except NameError: test(None, 'A_glob_B_ncap.x', 516)
        def A_glob_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_glob_B_ncap_delfunc()
        try: test(x, None, 520)
        except NameError: test(None, None, 521)
        x = "A_glob_B_ncap.x"
        try: test(x, 'A_glob_B_ncap.x', 523)
        except NameError: test(None, 'A_glob_B_ncap.x', 524)
        del x
        try: test(x, None, 526)
        except NameError: test(None, None, 527)
    def A_glob_b():
        pass
    A_glob_b()
    def A_glob_b_use():
        try: test(x, None, 532)
        except NameError: test(None, None, 533)
    A_glob_b_use()
    def A_glob_b_anno():
        x: str
        try: test(x, None, 537)
        except NameError: test(None, None, 538)
    A_glob_b_anno()
    def A_glob_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 543)
        else: error("Enclosed binding exists", 544)
    A_glob_b_nloc()
    def A_glob_b_glob():
        global x
        try: test(x, None, 548)
        except NameError: test(None, None, 549)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 551)
        except NameError: test(None, 'x', 552)
        def A_glob_b_glob_delfunc():
            global x; del x
        A_glob_b_glob_delfunc()
        try: test(x, None, 556)
        except NameError: test(None, None, 557)
        x = "x"
        try: test(x, 'x', 559)
        except NameError: test(None, 'x', 560)
        del x
        try: test(x, None, 562)
        except NameError: test(None, None, 563)
    A_glob_b_glob()
    def A_glob_b_loc():
        try: test(x, None, 566)
        except NameError: test(None, None, 567)
        [x := _ for _ in ["A_glob_b_loc.x"]]
        try: test(x, 'A_glob_b_loc.x', 569)
        except NameError: test(None, 'A_glob_b_loc.x', 570)
        def A_glob_b_loc_delfunc():
            nonlocal x; del x
        A_glob_b_loc_delfunc()
        try: test(x, None, 574)
        except NameError: test(None, None, 575)
        x = "A_glob_b_loc.x"
        try: test(x, 'A_glob_b_loc.x', 577)
        except NameError: test(None, 'A_glob_b_loc.x', 578)
        del x
        try: test(x, None, 580)
        except NameError: test(None, None, 581)
    A_glob_b_loc()
    def A_glob_b_ncap():
        try: test(x, None, 584)
        except NameError: test(None, None, 585)
        [x := _ for _ in ["A_glob_b_ncap.x"]]
        try: test(x, 'A_glob_b_ncap.x', 587)
        except NameError: test(None, 'A_glob_b_ncap.x', 588)
        def A_glob_b_ncap_delfunc():
            nonlocal x; del x
        A_glob_b_ncap_delfunc()
        try: test(x, None, 592)
        except NameError: test(None, None, 593)
        x = "A_glob_b_ncap.x"
        try: test(x, 'A_glob_b_ncap.x', 595)
        except NameError: test(None, 'A_glob_b_ncap.x', 596)
        del x
        try: test(x, None, 598)
        except NameError: test(None, None, 599)
    A_glob_b_ncap()
    def A_glob_setfunc():
        global x; x = "x"
    A_glob_setfunc()
    try: test(x, 'x', 604)
    except NameError: test(None, 'x', 605)
    def A_glob_delfunc():
        global x; del x
    A_glob_delfunc()
    try: test(x, None, 609)
    except NameError: test(None, None, 610)
    x = "x"
    try: test(x, 'x', 612)
    except NameError: test(None, 'x', 613)
    class A_glob_B2:
        pass
    class A_glob_B2_use:
        try: test(x, 'x', 617)
        except NameError: test(None, 'x', 618)
    class A_glob_B2_anno:
        x: str
        try: test(x, 'x', 621)
        except NameError: test(None, 'x', 622)
    class A_glob_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 626)
        else: error("Enclosed binding exists", 627)
    class A_glob_B2_glob:
        global x
        try: test(x, 'x', 630)
        except NameError: test(None, 'x', 631)
        del x
        try: test(x, None, 633)
        except NameError: test(None, None, 634)
        def A_glob_B2_glob_setfunc():
            global x; x = "x"
        A_glob_B2_glob_setfunc()
        try: test(x, 'x', 638)
        except NameError: test(None, 'x', 639)
        def A_glob_B2_glob_delfunc():
            global x; del x
        A_glob_B2_glob_delfunc()
        try: test(x, None, 643)
        except NameError: test(None, None, 644)
        x = "x"
        try: test(x, 'x', 646)
        except NameError: test(None, 'x', 647)
    class A_glob_B2_loc:
        try: test(x, 'x', 649)
        except NameError: test(None, 'x', 650)
        def A_glob_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_glob_B2_loc.x"
        A_glob_B2_loc_setfunc()
        try: test(x, 'A_glob_B2_loc.x', 654)
        except NameError: test(None, 'A_glob_B2_loc.x', 655)
        def A_glob_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_glob_B2_loc_delfunc()
        try: test(x, 'x', 659)
        except NameError: test(None, 'x', 660)
        x = "A_glob_B2_loc.x"
        try: test(x, 'A_glob_B2_loc.x', 662)
        except NameError: test(None, 'A_glob_B2_loc.x', 663)
        del x
        try: test(x, 'x', 665)
        except NameError: test(None, 'x', 666)
    class A_glob_B2_ncap:
        try: test(x, 'x', 668)
        except NameError: test(None, 'x', 669)
        def A_glob_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_glob_B2_ncap.x"
        A_glob_B2_ncap_setfunc()
        try: test(x, 'A_glob_B2_ncap.x', 673)
        except NameError: test(None, 'A_glob_B2_ncap.x', 674)
        def A_glob_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_glob_B2_ncap_delfunc()
        try: test(x, 'x', 678)
        except NameError: test(None, 'x', 679)
        x = "A_glob_B2_ncap.x"
        try: test(x, 'A_glob_B2_ncap.x', 681)
        except NameError: test(None, 'A_glob_B2_ncap.x', 682)
        del x
        try: test(x, 'x', 684)
        except NameError: test(None, 'x', 685)
    def A_glob_b2():
        pass
    A_glob_b2()
    def A_glob_b2_use():
        try: test(x, 'x', 690)
        except NameError: test(None, 'x', 691)
    A_glob_b2_use()
    def A_glob_b2_anno():
        x: str
        try: test(x, None, 695)
        except NameError: test(None, None, 696)
    A_glob_b2_anno()
    def A_glob_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 701)
        else: error("Enclosed binding exists", 702)
    A_glob_b2_nloc()
    def A_glob_b2_glob():
        global x
        try: test(x, 'x', 706)
        except NameError: test(None, 'x', 707)
        del x
        try: test(x, None, 709)
        except NameError: test(None, None, 710)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 712)
        except NameError: test(None, 'x', 713)
        def A_glob_b2_glob_delfunc():
            global x; del x
        A_glob_b2_glob_delfunc()
        try: test(x, None, 717)
        except NameError: test(None, None, 718)
        x = "x"
        try: test(x, 'x', 720)
        except NameError: test(None, 'x', 721)
    A_glob_b2_glob()
    def A_glob_b2_loc():
        try: test(x, None, 724)
        except NameError: test(None, None, 725)
        [x := _ for _ in ["A_glob_b2_loc.x"]]
        try: test(x, 'A_glob_b2_loc.x', 727)
        except NameError: test(None, 'A_glob_b2_loc.x', 728)
        def A_glob_b2_loc_delfunc():
            nonlocal x; del x
        A_glob_b2_loc_delfunc()
        try: test(x, None, 732)
        except NameError: test(None, None, 733)
        x = "A_glob_b2_loc.x"
        try: test(x, 'A_glob_b2_loc.x', 735)
        except NameError: test(None, 'A_glob_b2_loc.x', 736)
        del x
        try: test(x, None, 738)
        except NameError: test(None, None, 739)
    A_glob_b2_loc()
    def A_glob_b2_ncap():
        try: test(x, None, 742)
        except NameError: test(None, None, 743)
        [x := _ for _ in ["A_glob_b2_ncap.x"]]
        try: test(x, 'A_glob_b2_ncap.x', 745)
        except NameError: test(None, 'A_glob_b2_ncap.x', 746)
        def A_glob_b2_ncap_delfunc():
            nonlocal x; del x
        A_glob_b2_ncap_delfunc()
        try: test(x, None, 750)
        except NameError: test(None, None, 751)
        x = "A_glob_b2_ncap.x"
        try: test(x, 'A_glob_b2_ncap.x', 753)
        except NameError: test(None, 'A_glob_b2_ncap.x', 754)
        del x
        try: test(x, None, 756)
        except NameError: test(None, None, 757)
    A_glob_b2_ncap()
    del x
    try: test(x, None, 760)
    except NameError: test(None, None, 761)
class A_loc:
    try: test(x, None, 763)
    except NameError: test(None, None, 764)
    class A_loc_B:
        pass
    class A_loc_B_use:
        try: test(x, None, 768)
        except NameError: test(None, None, 769)
    class A_loc_B_anno:
        x: str
        try: test(x, None, 772)
        except NameError: test(None, None, 773)
    class A_loc_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 777)
        else: error("Enclosed binding exists", 778)
    class A_loc_B_glob:
        global x
        try: test(x, None, 781)
        except NameError: test(None, None, 782)
        def A_loc_B_glob_setfunc():
            global x; x = "x"
        A_loc_B_glob_setfunc()
        try: test(x, 'x', 786)
        except NameError: test(None, 'x', 787)
        def A_loc_B_glob_delfunc():
            global x; del x
        A_loc_B_glob_delfunc()
        try: test(x, None, 791)
        except NameError: test(None, None, 792)
        x = "x"
        try: test(x, 'x', 794)
        except NameError: test(None, 'x', 795)
        del x
        try: test(x, None, 797)
        except NameError: test(None, None, 798)
    class A_loc_B_loc:
        try: test(x, None, 800)
        except NameError: test(None, None, 801)
        def A_loc_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_loc_B_loc.x"
        A_loc_B_loc_setfunc()
        try: test(x, 'A_loc_B_loc.x', 805)
        except NameError: test(None, 'A_loc_B_loc.x', 806)
        def A_loc_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_loc_B_loc_delfunc()
        try: test(x, None, 810)
        except NameError: test(None, None, 811)
        x = "A_loc_B_loc.x"
        try: test(x, 'A_loc_B_loc.x', 813)
        except NameError: test(None, 'A_loc_B_loc.x', 814)
        del x
        try: test(x, None, 816)
        except NameError: test(None, None, 817)
    class A_loc_B_ncap:
        try: test(x, None, 819)
        except NameError: test(None, None, 820)
        def A_loc_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_loc_B_ncap.x"
        A_loc_B_ncap_setfunc()
        try: test(x, 'A_loc_B_ncap.x', 824)
        except NameError: test(None, 'A_loc_B_ncap.x', 825)
        def A_loc_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_loc_B_ncap_delfunc()
        try: test(x, None, 829)
        except NameError: test(None, None, 830)
        x = "A_loc_B_ncap.x"
        try: test(x, 'A_loc_B_ncap.x', 832)
        except NameError: test(None, 'A_loc_B_ncap.x', 833)
        del x
        try: test(x, None, 835)
        except NameError: test(None, None, 836)
    def A_loc_b():
        pass
    A_loc_b()
    def A_loc_b_use():
        try: test(x, None, 841)
        except NameError: test(None, None, 842)
    A_loc_b_use()
    def A_loc_b_anno():
        x: str
        try: test(x, None, 846)
        except NameError: test(None, None, 847)
    A_loc_b_anno()
    def A_loc_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 852)
        else: error("Enclosed binding exists", 853)
    A_loc_b_nloc()
    def A_loc_b_glob():
        global x
        try: test(x, None, 857)
        except NameError: test(None, None, 858)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 860)
        except NameError: test(None, 'x', 861)
        def A_loc_b_glob_delfunc():
            global x; del x
        A_loc_b_glob_delfunc()
        try: test(x, None, 865)
        except NameError: test(None, None, 866)
        x = "x"
        try: test(x, 'x', 868)
        except NameError: test(None, 'x', 869)
        del x
        try: test(x, None, 871)
        except NameError: test(None, None, 872)
    A_loc_b_glob()
    def A_loc_b_loc():
        try: test(x, None, 875)
        except NameError: test(None, None, 876)
        [x := _ for _ in ["A_loc_b_loc.x"]]
        try: test(x, 'A_loc_b_loc.x', 878)
        except NameError: test(None, 'A_loc_b_loc.x', 879)
        def A_loc_b_loc_delfunc():
            nonlocal x; del x
        A_loc_b_loc_delfunc()
        try: test(x, None, 883)
        except NameError: test(None, None, 884)
        x = "A_loc_b_loc.x"
        try: test(x, 'A_loc_b_loc.x', 886)
        except NameError: test(None, 'A_loc_b_loc.x', 887)
        del x
        try: test(x, None, 889)
        except NameError: test(None, None, 890)
    A_loc_b_loc()
    def A_loc_b_ncap():
        try: test(x, None, 893)
        except NameError: test(None, None, 894)
        [x := _ for _ in ["A_loc_b_ncap.x"]]
        try: test(x, 'A_loc_b_ncap.x', 896)
        except NameError: test(None, 'A_loc_b_ncap.x', 897)
        def A_loc_b_ncap_delfunc():
            nonlocal x; del x
        A_loc_b_ncap_delfunc()
        try: test(x, None, 901)
        except NameError: test(None, None, 902)
        x = "A_loc_b_ncap.x"
        try: test(x, 'A_loc_b_ncap.x', 904)
        except NameError: test(None, 'A_loc_b_ncap.x', 905)
        del x
        try: test(x, None, 907)
        except NameError: test(None, None, 908)
    A_loc_b_ncap()
    def A_loc_setfunc():
        inspect.stack()[1].frame.f_locals["x"] = "A_loc.x"
    A_loc_setfunc()
    try: test(x, 'A_loc.x', 913)
    except NameError: test(None, 'A_loc.x', 914)
    def A_loc_delfunc():
        del inspect.stack()[1].frame.f_locals["x"]
    A_loc_delfunc()
    try: test(x, None, 918)
    except NameError: test(None, None, 919)
    x = "A_loc.x"
    try: test(x, 'A_loc.x', 921)
    except NameError: test(None, 'A_loc.x', 922)
    class A_loc_B2:
        pass
    class A_loc_B2_use:
        try: test(x, None, 926)
        except NameError: test(None, None, 927)
    class A_loc_B2_anno:
        x: str
        try: test(x, None, 930)
        except NameError: test(None, None, 931)
    class A_loc_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 935)
        else: error("Enclosed binding exists", 936)
    class A_loc_B2_glob:
        global x
        try: test(x, None, 939)
        except NameError: test(None, None, 940)
        def A_loc_B2_glob_setfunc():
            global x; x = "x"
        A_loc_B2_glob_setfunc()
        try: test(x, 'x', 944)
        except NameError: test(None, 'x', 945)
        def A_loc_B2_glob_delfunc():
            global x; del x
        A_loc_B2_glob_delfunc()
        try: test(x, None, 949)
        except NameError: test(None, None, 950)
        x = "x"
        try: test(x, 'x', 952)
        except NameError: test(None, 'x', 953)
        del x
        try: test(x, None, 955)
        except NameError: test(None, None, 956)
    class A_loc_B2_loc:
        try: test(x, None, 958)
        except NameError: test(None, None, 959)
        def A_loc_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_loc_B2_loc.x"
        A_loc_B2_loc_setfunc()
        try: test(x, 'A_loc_B2_loc.x', 963)
        except NameError: test(None, 'A_loc_B2_loc.x', 964)
        def A_loc_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_loc_B2_loc_delfunc()
        try: test(x, None, 968)
        except NameError: test(None, None, 969)
        x = "A_loc_B2_loc.x"
        try: test(x, 'A_loc_B2_loc.x', 971)
        except NameError: test(None, 'A_loc_B2_loc.x', 972)
        del x
        try: test(x, None, 974)
        except NameError: test(None, None, 975)
    class A_loc_B2_ncap:
        try: test(x, None, 977)
        except NameError: test(None, None, 978)
        def A_loc_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_loc_B2_ncap.x"
        A_loc_B2_ncap_setfunc()
        try: test(x, 'A_loc_B2_ncap.x', 982)
        except NameError: test(None, 'A_loc_B2_ncap.x', 983)
        def A_loc_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_loc_B2_ncap_delfunc()
        try: test(x, None, 987)
        except NameError: test(None, None, 988)
        x = "A_loc_B2_ncap.x"
        try: test(x, 'A_loc_B2_ncap.x', 990)
        except NameError: test(None, 'A_loc_B2_ncap.x', 991)
        del x
        try: test(x, None, 993)
        except NameError: test(None, None, 994)
    def A_loc_b2():
        pass
    A_loc_b2()
    def A_loc_b2_use():
        try: test(x, None, 999)
        except NameError: test(None, None, 1000)
    A_loc_b2_use()
    def A_loc_b2_anno():
        x: str
        try: test(x, None, 1004)
        except NameError: test(None, None, 1005)
    A_loc_b2_anno()
    def A_loc_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1010)
        else: error("Enclosed binding exists", 1011)
    A_loc_b2_nloc()
    def A_loc_b2_glob():
        global x
        try: test(x, None, 1015)
        except NameError: test(None, None, 1016)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1018)
        except NameError: test(None, 'x', 1019)
        def A_loc_b2_glob_delfunc():
            global x; del x
        A_loc_b2_glob_delfunc()
        try: test(x, None, 1023)
        except NameError: test(None, None, 1024)
        x = "x"
        try: test(x, 'x', 1026)
        except NameError: test(None, 'x', 1027)
        del x
        try: test(x, None, 1029)
        except NameError: test(None, None, 1030)
    A_loc_b2_glob()
    def A_loc_b2_loc():
        try: test(x, None, 1033)
        except NameError: test(None, None, 1034)
        [x := _ for _ in ["A_loc_b2_loc.x"]]
        try: test(x, 'A_loc_b2_loc.x', 1036)
        except NameError: test(None, 'A_loc_b2_loc.x', 1037)
        def A_loc_b2_loc_delfunc():
            nonlocal x; del x
        A_loc_b2_loc_delfunc()
        try: test(x, None, 1041)
        except NameError: test(None, None, 1042)
        x = "A_loc_b2_loc.x"
        try: test(x, 'A_loc_b2_loc.x', 1044)
        except NameError: test(None, 'A_loc_b2_loc.x', 1045)
        del x
        try: test(x, None, 1047)
        except NameError: test(None, None, 1048)
    A_loc_b2_loc()
    def A_loc_b2_ncap():
        try: test(x, None, 1051)
        except NameError: test(None, None, 1052)
        [x := _ for _ in ["A_loc_b2_ncap.x"]]
        try: test(x, 'A_loc_b2_ncap.x', 1054)
        except NameError: test(None, 'A_loc_b2_ncap.x', 1055)
        def A_loc_b2_ncap_delfunc():
            nonlocal x; del x
        A_loc_b2_ncap_delfunc()
        try: test(x, None, 1059)
        except NameError: test(None, None, 1060)
        x = "A_loc_b2_ncap.x"
        try: test(x, 'A_loc_b2_ncap.x', 1062)
        except NameError: test(None, 'A_loc_b2_ncap.x', 1063)
        del x
        try: test(x, None, 1065)
        except NameError: test(None, None, 1066)
    A_loc_b2_ncap()
    del x
    try: test(x, None, 1069)
    except NameError: test(None, None, 1070)
class A_ncap:
    try: test(x, None, 1072)
    except NameError: test(None, None, 1073)
    class A_ncap_B:
        pass
    class A_ncap_B_glob:
        global x
        try: test(x, None, 1078)
        except NameError: test(None, None, 1079)
        def A_ncap_B_glob_setfunc():
            global x; x = "x"
        A_ncap_B_glob_setfunc()
        try: test(x, 'x', 1083)
        except NameError: test(None, 'x', 1084)
        def A_ncap_B_glob_delfunc():
            global x; del x
        A_ncap_B_glob_delfunc()
        try: test(x, None, 1088)
        except NameError: test(None, None, 1089)
        x = "x"
        try: test(x, 'x', 1091)
        except NameError: test(None, 'x', 1092)
        del x
        try: test(x, None, 1094)
        except NameError: test(None, None, 1095)
    class A_ncap_B_loc:
        try: test(x, None, 1097)
        except NameError: test(None, None, 1098)
        def A_ncap_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_ncap_B_loc.x"
        A_ncap_B_loc_setfunc()
        try: test(x, 'A_ncap_B_loc.x', 1102)
        except NameError: test(None, 'A_ncap_B_loc.x', 1103)
        def A_ncap_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_ncap_B_loc_delfunc()
        try: test(x, None, 1107)
        except NameError: test(None, None, 1108)
        x = "A_ncap_B_loc.x"
        try: test(x, 'A_ncap_B_loc.x', 1110)
        except NameError: test(None, 'A_ncap_B_loc.x', 1111)
        del x
        try: test(x, None, 1113)
        except NameError: test(None, None, 1114)
    def A_ncap_b():
        pass
    A_ncap_b()
    def A_ncap_b_glob():
        global x
        try: test(x, None, 1120)
        except NameError: test(None, None, 1121)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1123)
        except NameError: test(None, 'x', 1124)
        def A_ncap_b_glob_delfunc():
            global x; del x
        A_ncap_b_glob_delfunc()
        try: test(x, None, 1128)
        except NameError: test(None, None, 1129)
        x = "x"
        try: test(x, 'x', 1131)
        except NameError: test(None, 'x', 1132)
        del x
        try: test(x, None, 1134)
        except NameError: test(None, None, 1135)
    A_ncap_b_glob()
    def A_ncap_b_loc():
        try: test(x, None, 1138)
        except NameError: test(None, None, 1139)
        [x := _ for _ in ["A_ncap_b_loc.x"]]
        try: test(x, 'A_ncap_b_loc.x', 1141)
        except NameError: test(None, 'A_ncap_b_loc.x', 1142)
        def A_ncap_b_loc_delfunc():
            nonlocal x; del x
        A_ncap_b_loc_delfunc()
        try: test(x, None, 1146)
        except NameError: test(None, None, 1147)
        x = "A_ncap_b_loc.x"
        try: test(x, 'A_ncap_b_loc.x', 1149)
        except NameError: test(None, 'A_ncap_b_loc.x', 1150)
        del x
        try: test(x, None, 1152)
        except NameError: test(None, None, 1153)
    A_ncap_b_loc()
    def A_ncap_setfunc():
        inspect.stack()[1].frame.f_locals["x"] = "A_ncap.x"
    A_ncap_setfunc()
    try: test(x, 'A_ncap.x', 1158)
    except NameError: test(None, 'A_ncap.x', 1159)
    def A_ncap_delfunc():
        del inspect.stack()[1].frame.f_locals["x"]
    A_ncap_delfunc()
    try: test(x, None, 1163)
    except NameError: test(None, None, 1164)
    x = "A_ncap.x"
    try: test(x, 'A_ncap.x', 1166)
    except NameError: test(None, 'A_ncap.x', 1167)
    class A_ncap_B2:
        pass
    class A_ncap_B2_glob:
        global x
        try: test(x, None, 1172)
        except NameError: test(None, None, 1173)
        def A_ncap_B2_glob_setfunc():
            global x; x = "x"
        A_ncap_B2_glob_setfunc()
        try: test(x, 'x', 1177)
        except NameError: test(None, 'x', 1178)
        def A_ncap_B2_glob_delfunc():
            global x; del x
        A_ncap_B2_glob_delfunc()
        try: test(x, None, 1182)
        except NameError: test(None, None, 1183)
        x = "x"
        try: test(x, 'x', 1185)
        except NameError: test(None, 'x', 1186)
        del x
        try: test(x, None, 1188)
        except NameError: test(None, None, 1189)
    class A_ncap_B2_loc:
        try: test(x, None, 1191)
        except NameError: test(None, None, 1192)
        def A_ncap_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_ncap_B2_loc.x"
        A_ncap_B2_loc_setfunc()
        try: test(x, 'A_ncap_B2_loc.x', 1196)
        except NameError: test(None, 'A_ncap_B2_loc.x', 1197)
        def A_ncap_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_ncap_B2_loc_delfunc()
        try: test(x, None, 1201)
        except NameError: test(None, None, 1202)
        x = "A_ncap_B2_loc.x"
        try: test(x, 'A_ncap_B2_loc.x', 1204)
        except NameError: test(None, 'A_ncap_B2_loc.x', 1205)
        del x
        try: test(x, None, 1207)
        except NameError: test(None, None, 1208)
    def A_ncap_b2():
        pass
    A_ncap_b2()
    def A_ncap_b2_glob():
        global x
        try: test(x, None, 1214)
        except NameError: test(None, None, 1215)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1217)
        except NameError: test(None, 'x', 1218)
        def A_ncap_b2_glob_delfunc():
            global x; del x
        A_ncap_b2_glob_delfunc()
        try: test(x, None, 1222)
        except NameError: test(None, None, 1223)
        x = "x"
        try: test(x, 'x', 1225)
        except NameError: test(None, 'x', 1226)
        del x
        try: test(x, None, 1228)
        except NameError: test(None, None, 1229)
    A_ncap_b2_glob()
    def A_ncap_b2_loc():
        try: test(x, None, 1232)
        except NameError: test(None, None, 1233)
        [x := _ for _ in ["A_ncap_b2_loc.x"]]
        try: test(x, 'A_ncap_b2_loc.x', 1235)
        except NameError: test(None, 'A_ncap_b2_loc.x', 1236)
        def A_ncap_b2_loc_delfunc():
            nonlocal x; del x
        A_ncap_b2_loc_delfunc()
        try: test(x, None, 1240)
        except NameError: test(None, None, 1241)
        x = "A_ncap_b2_loc.x"
        try: test(x, 'A_ncap_b2_loc.x', 1243)
        except NameError: test(None, 'A_ncap_b2_loc.x', 1244)
        del x
        try: test(x, None, 1246)
        except NameError: test(None, None, 1247)
    A_ncap_b2_loc()
    del x
    try: test(x, None, 1250)
    except NameError: test(None, None, 1251)
def a():
    class a_B:
        pass
    class a_B_use:
        try: test(x, None, 1256)
        except NameError: test(None, None, 1257)
    class a_B_anno:
        x: str
        try: test(x, None, 1260)
        except NameError: test(None, None, 1261)
    class a_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1265)
        else: error("Enclosed binding exists", 1266)
    class a_B_glob:
        global x
        try: test(x, None, 1269)
        except NameError: test(None, None, 1270)
        def a_B_glob_setfunc():
            global x; x = "x"
        a_B_glob_setfunc()
        try: test(x, 'x', 1274)
        except NameError: test(None, 'x', 1275)
        def a_B_glob_delfunc():
            global x; del x
        a_B_glob_delfunc()
        try: test(x, None, 1279)
        except NameError: test(None, None, 1280)
        x = "x"
        try: test(x, 'x', 1282)
        except NameError: test(None, 'x', 1283)
        del x
        try: test(x, None, 1285)
        except NameError: test(None, None, 1286)
    class a_B_loc:
        try: test(x, None, 1288)
        except NameError: test(None, None, 1289)
        def a_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_B_loc.x"
        a_B_loc_setfunc()
        try: test(x, 'a_B_loc.x', 1293)
        except NameError: test(None, 'a_B_loc.x', 1294)
        def a_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_B_loc_delfunc()
        try: test(x, None, 1298)
        except NameError: test(None, None, 1299)
        x = "a_B_loc.x"
        try: test(x, 'a_B_loc.x', 1301)
        except NameError: test(None, 'a_B_loc.x', 1302)
        del x
        try: test(x, None, 1304)
        except NameError: test(None, None, 1305)
    class a_B_ncap:
        try: test(x, None, 1307)
        except NameError: test(None, None, 1308)
        def a_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_B_ncap.x"
        a_B_ncap_setfunc()
        try: test(x, 'a_B_ncap.x', 1312)
        except NameError: test(None, 'a_B_ncap.x', 1313)
        def a_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_B_ncap_delfunc()
        try: test(x, None, 1317)
        except NameError: test(None, None, 1318)
        x = "a_B_ncap.x"
        try: test(x, 'a_B_ncap.x', 1320)
        except NameError: test(None, 'a_B_ncap.x', 1321)
        del x
        try: test(x, None, 1323)
        except NameError: test(None, None, 1324)
    def a_b():
        pass
    a_b()
    def a_b_use():
        try: test(x, None, 1329)
        except NameError: test(None, None, 1330)
    a_b_use()
    def a_b_anno():
        x: str
        try: test(x, None, 1334)
        except NameError: test(None, None, 1335)
    a_b_anno()
    def a_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1340)
        else: error("Enclosed binding exists", 1341)
    a_b_nloc()
    def a_b_glob():
        global x
        try: test(x, None, 1345)
        except NameError: test(None, None, 1346)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1348)
        except NameError: test(None, 'x', 1349)
        def a_b_glob_delfunc():
            global x; del x
        a_b_glob_delfunc()
        try: test(x, None, 1353)
        except NameError: test(None, None, 1354)
        x = "x"
        try: test(x, 'x', 1356)
        except NameError: test(None, 'x', 1357)
        del x
        try: test(x, None, 1359)
        except NameError: test(None, None, 1360)
    a_b_glob()
    def a_b_loc():
        try: test(x, None, 1363)
        except NameError: test(None, None, 1364)
        [x := _ for _ in ["a_b_loc.x"]]
        try: test(x, 'a_b_loc.x', 1366)
        except NameError: test(None, 'a_b_loc.x', 1367)
        def a_b_loc_delfunc():
            nonlocal x; del x
        a_b_loc_delfunc()
        try: test(x, None, 1371)
        except NameError: test(None, None, 1372)
        x = "a_b_loc.x"
        try: test(x, 'a_b_loc.x', 1374)
        except NameError: test(None, 'a_b_loc.x', 1375)
        del x
        try: test(x, None, 1377)
        except NameError: test(None, None, 1378)
    a_b_loc()
    def a_b_ncap():
        try: test(x, None, 1381)
        except NameError: test(None, None, 1382)
        [x := _ for _ in ["a_b_ncap.x"]]
        try: test(x, 'a_b_ncap.x', 1384)
        except NameError: test(None, 'a_b_ncap.x', 1385)
        def a_b_ncap_delfunc():
            nonlocal x; del x
        a_b_ncap_delfunc()
        try: test(x, None, 1389)
        except NameError: test(None, None, 1390)
        x = "a_b_ncap.x"
        try: test(x, 'a_b_ncap.x', 1392)
        except NameError: test(None, 'a_b_ncap.x', 1393)
        del x
        try: test(x, None, 1395)
        except NameError: test(None, None, 1396)
    a_b_ncap()
a()
def a_use():
    try: test(x, None, 1400)
    except NameError: test(None, None, 1401)
    class a_use_B:
        pass
    class a_use_B_use:
        try: test(x, None, 1405)
        except NameError: test(None, None, 1406)
    class a_use_B_anno:
        x: str
        try: test(x, None, 1409)
        except NameError: test(None, None, 1410)
    class a_use_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1414)
        else: error("Enclosed binding exists", 1415)
    class a_use_B_glob:
        global x
        try: test(x, None, 1418)
        except NameError: test(None, None, 1419)
        def a_use_B_glob_setfunc():
            global x; x = "x"
        a_use_B_glob_setfunc()
        try: test(x, 'x', 1423)
        except NameError: test(None, 'x', 1424)
        def a_use_B_glob_delfunc():
            global x; del x
        a_use_B_glob_delfunc()
        try: test(x, None, 1428)
        except NameError: test(None, None, 1429)
        x = "x"
        try: test(x, 'x', 1431)
        except NameError: test(None, 'x', 1432)
        del x
        try: test(x, None, 1434)
        except NameError: test(None, None, 1435)
    class a_use_B_loc:
        try: test(x, None, 1437)
        except NameError: test(None, None, 1438)
        def a_use_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_use_B_loc.x"
        a_use_B_loc_setfunc()
        try: test(x, 'a_use_B_loc.x', 1442)
        except NameError: test(None, 'a_use_B_loc.x', 1443)
        def a_use_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_use_B_loc_delfunc()
        try: test(x, None, 1447)
        except NameError: test(None, None, 1448)
        x = "a_use_B_loc.x"
        try: test(x, 'a_use_B_loc.x', 1450)
        except NameError: test(None, 'a_use_B_loc.x', 1451)
        del x
        try: test(x, None, 1453)
        except NameError: test(None, None, 1454)
    class a_use_B_ncap:
        try: test(x, None, 1456)
        except NameError: test(None, None, 1457)
        def a_use_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_use_B_ncap.x"
        a_use_B_ncap_setfunc()
        try: test(x, 'a_use_B_ncap.x', 1461)
        except NameError: test(None, 'a_use_B_ncap.x', 1462)
        def a_use_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_use_B_ncap_delfunc()
        try: test(x, None, 1466)
        except NameError: test(None, None, 1467)
        x = "a_use_B_ncap.x"
        try: test(x, 'a_use_B_ncap.x', 1469)
        except NameError: test(None, 'a_use_B_ncap.x', 1470)
        del x
        try: test(x, None, 1472)
        except NameError: test(None, None, 1473)
    def a_use_b():
        pass
    a_use_b()
    def a_use_b_use():
        try: test(x, None, 1478)
        except NameError: test(None, None, 1479)
    a_use_b_use()
    def a_use_b_anno():
        x: str
        try: test(x, None, 1483)
        except NameError: test(None, None, 1484)
    a_use_b_anno()
    def a_use_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1489)
        else: error("Enclosed binding exists", 1490)
    a_use_b_nloc()
    def a_use_b_glob():
        global x
        try: test(x, None, 1494)
        except NameError: test(None, None, 1495)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1497)
        except NameError: test(None, 'x', 1498)
        def a_use_b_glob_delfunc():
            global x; del x
        a_use_b_glob_delfunc()
        try: test(x, None, 1502)
        except NameError: test(None, None, 1503)
        x = "x"
        try: test(x, 'x', 1505)
        except NameError: test(None, 'x', 1506)
        del x
        try: test(x, None, 1508)
        except NameError: test(None, None, 1509)
    a_use_b_glob()
    def a_use_b_loc():
        try: test(x, None, 1512)
        except NameError: test(None, None, 1513)
        [x := _ for _ in ["a_use_b_loc.x"]]
        try: test(x, 'a_use_b_loc.x', 1515)
        except NameError: test(None, 'a_use_b_loc.x', 1516)
        def a_use_b_loc_delfunc():
            nonlocal x; del x
        a_use_b_loc_delfunc()
        try: test(x, None, 1520)
        except NameError: test(None, None, 1521)
        x = "a_use_b_loc.x"
        try: test(x, 'a_use_b_loc.x', 1523)
        except NameError: test(None, 'a_use_b_loc.x', 1524)
        del x
        try: test(x, None, 1526)
        except NameError: test(None, None, 1527)
    a_use_b_loc()
    def a_use_b_ncap():
        try: test(x, None, 1530)
        except NameError: test(None, None, 1531)
        [x := _ for _ in ["a_use_b_ncap.x"]]
        try: test(x, 'a_use_b_ncap.x', 1533)
        except NameError: test(None, 'a_use_b_ncap.x', 1534)
        def a_use_b_ncap_delfunc():
            nonlocal x; del x
        a_use_b_ncap_delfunc()
        try: test(x, None, 1538)
        except NameError: test(None, None, 1539)
        x = "a_use_b_ncap.x"
        try: test(x, 'a_use_b_ncap.x', 1541)
        except NameError: test(None, 'a_use_b_ncap.x', 1542)
        del x
        try: test(x, None, 1544)
        except NameError: test(None, None, 1545)
    a_use_b_ncap()
a_use()
def a_anno():
    x: str
    try: test(x, None, 1550)
    except NameError: test(None, None, 1551)
    class a_anno_B:
        pass
    class a_anno_B_use:
        try: test(x, None, 1555)
        except NameError: test(None, None, 1556)
    class a_anno_B_anno:
        x: str
        try: test(x, None, 1559)
        except NameError: test(None, None, 1560)
    class a_anno_B_nloc:
        nonlocal x
        try: test(x, None, 1563)
        except NameError: test(None, None, 1564)
        def a_anno_B_nloc_setfunc():
            nonlocal x; x = "a_anno.x"
        a_anno_B_nloc_setfunc()
        try: test(x, 'a_anno.x', 1568)
        except NameError: test(None, 'a_anno.x', 1569)
        def a_anno_B_nloc_delfunc():
            nonlocal x; del x
        a_anno_B_nloc_delfunc()
        try: test(x, None, 1573)
        except NameError: test(None, None, 1574)
        x = "a_anno.x"
        try: test(x, 'a_anno.x', 1576)
        except NameError: test(None, 'a_anno.x', 1577)
        del x
        try: test(x, None, 1579)
        except NameError: test(None, None, 1580)
    class a_anno_B_glob:
        global x
        try: test(x, None, 1583)
        except NameError: test(None, None, 1584)
        def a_anno_B_glob_setfunc():
            global x; x = "x"
        a_anno_B_glob_setfunc()
        try: test(x, 'x', 1588)
        except NameError: test(None, 'x', 1589)
        def a_anno_B_glob_delfunc():
            global x; del x
        a_anno_B_glob_delfunc()
        try: test(x, None, 1593)
        except NameError: test(None, None, 1594)
        x = "x"
        try: test(x, 'x', 1596)
        except NameError: test(None, 'x', 1597)
        del x
        try: test(x, None, 1599)
        except NameError: test(None, None, 1600)
    class a_anno_B_loc:
        try: test(x, None, 1602)
        except NameError: test(None, None, 1603)
        def a_anno_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_anno_B_loc.x"
        a_anno_B_loc_setfunc()
        try: test(x, 'a_anno_B_loc.x', 1607)
        except NameError: test(None, 'a_anno_B_loc.x', 1608)
        def a_anno_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_anno_B_loc_delfunc()
        try: test(x, None, 1612)
        except NameError: test(None, None, 1613)
        x = "a_anno_B_loc.x"
        try: test(x, 'a_anno_B_loc.x', 1615)
        except NameError: test(None, 'a_anno_B_loc.x', 1616)
        del x
        try: test(x, None, 1618)
        except NameError: test(None, None, 1619)
    class a_anno_B_ncap:
        try: test(x, None, 1621)
        except NameError: test(None, None, 1622)
        def a_anno_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_anno_B_ncap.x"
        a_anno_B_ncap_setfunc()
        try: test(x, 'a_anno_B_ncap.x', 1626)
        except NameError: test(None, 'a_anno_B_ncap.x', 1627)
        def a_anno_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_anno_B_ncap_delfunc()
        try: test(x, None, 1631)
        except NameError: test(None, None, 1632)
        x = "a_anno_B_ncap.x"
        try: test(x, 'a_anno_B_ncap.x', 1634)
        except NameError: test(None, 'a_anno_B_ncap.x', 1635)
        del x
        try: test(x, None, 1637)
        except NameError: test(None, None, 1638)
    def a_anno_b():
        pass
    a_anno_b()
    def a_anno_b_use():
        try: test(x, None, 1643)
        except NameError: test(None, None, 1644)
    a_anno_b_use()
    def a_anno_b_anno():
        x: str
        try: test(x, None, 1648)
        except NameError: test(None, None, 1649)
    a_anno_b_anno()
    def a_anno_b_nloc():
        nonlocal x
        try: test(x, None, 1653)
        except NameError: test(None, None, 1654)
        [x := _ for _ in ["a_anno.x"]]
        try: test(x, 'a_anno.x', 1656)
        except NameError: test(None, 'a_anno.x', 1657)
        def a_anno_b_nloc_delfunc():
            nonlocal x; del x
        a_anno_b_nloc_delfunc()
        try: test(x, None, 1661)
        except NameError: test(None, None, 1662)
        x = "a_anno.x"
        try: test(x, 'a_anno.x', 1664)
        except NameError: test(None, 'a_anno.x', 1665)
        del x
        try: test(x, None, 1667)
        except NameError: test(None, None, 1668)
    a_anno_b_nloc()
    def a_anno_b_glob():
        global x
        try: test(x, None, 1672)
        except NameError: test(None, None, 1673)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1675)
        except NameError: test(None, 'x', 1676)
        def a_anno_b_glob_delfunc():
            global x; del x
        a_anno_b_glob_delfunc()
        try: test(x, None, 1680)
        except NameError: test(None, None, 1681)
        x = "x"
        try: test(x, 'x', 1683)
        except NameError: test(None, 'x', 1684)
        del x
        try: test(x, None, 1686)
        except NameError: test(None, None, 1687)
    a_anno_b_glob()
    def a_anno_b_loc():
        try: test(x, None, 1690)
        except NameError: test(None, None, 1691)
        [x := _ for _ in ["a_anno_b_loc.x"]]
        try: test(x, 'a_anno_b_loc.x', 1693)
        except NameError: test(None, 'a_anno_b_loc.x', 1694)
        def a_anno_b_loc_delfunc():
            nonlocal x; del x
        a_anno_b_loc_delfunc()
        try: test(x, None, 1698)
        except NameError: test(None, None, 1699)
        x = "a_anno_b_loc.x"
        try: test(x, 'a_anno_b_loc.x', 1701)
        except NameError: test(None, 'a_anno_b_loc.x', 1702)
        del x
        try: test(x, None, 1704)
        except NameError: test(None, None, 1705)
    a_anno_b_loc()
    def a_anno_b_ncap():
        try: test(x, None, 1708)
        except NameError: test(None, None, 1709)
        [x := _ for _ in ["a_anno_b_ncap.x"]]
        try: test(x, 'a_anno_b_ncap.x', 1711)
        except NameError: test(None, 'a_anno_b_ncap.x', 1712)
        def a_anno_b_ncap_delfunc():
            nonlocal x; del x
        a_anno_b_ncap_delfunc()
        try: test(x, None, 1716)
        except NameError: test(None, None, 1717)
        x = "a_anno_b_ncap.x"
        try: test(x, 'a_anno_b_ncap.x', 1719)
        except NameError: test(None, 'a_anno_b_ncap.x', 1720)
        del x
        try: test(x, None, 1722)
        except NameError: test(None, None, 1723)
    a_anno_b_ncap()
a_anno()
def a_nloc():
    # No enclosed binding exists.
    try: compile("nonlocal x", "<string>", "exec")
    except SyntaxError: test(None, None, 1729)
    else: error("Enclosed binding exists", 1730)
a_nloc()
def a_glob():
    global x
    try: test(x, None, 1734)
    except NameError: test(None, None, 1735)
    class a_glob_B:
        pass
    class a_glob_B_use:
        try: test(x, None, 1739)
        except NameError: test(None, None, 1740)
    class a_glob_B_anno:
        x: str
        try: test(x, None, 1743)
        except NameError: test(None, None, 1744)
    class a_glob_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1748)
        else: error("Enclosed binding exists", 1749)
    class a_glob_B_glob:
        global x
        try: test(x, None, 1752)
        except NameError: test(None, None, 1753)
        def a_glob_B_glob_setfunc():
            global x; x = "x"
        a_glob_B_glob_setfunc()
        try: test(x, 'x', 1757)
        except NameError: test(None, 'x', 1758)
        def a_glob_B_glob_delfunc():
            global x; del x
        a_glob_B_glob_delfunc()
        try: test(x, None, 1762)
        except NameError: test(None, None, 1763)
        x = "x"
        try: test(x, 'x', 1765)
        except NameError: test(None, 'x', 1766)
        del x
        try: test(x, None, 1768)
        except NameError: test(None, None, 1769)
    class a_glob_B_loc:
        try: test(x, None, 1771)
        except NameError: test(None, None, 1772)
        def a_glob_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_glob_B_loc.x"
        a_glob_B_loc_setfunc()
        try: test(x, 'a_glob_B_loc.x', 1776)
        except NameError: test(None, 'a_glob_B_loc.x', 1777)
        def a_glob_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_glob_B_loc_delfunc()
        try: test(x, None, 1781)
        except NameError: test(None, None, 1782)
        x = "a_glob_B_loc.x"
        try: test(x, 'a_glob_B_loc.x', 1784)
        except NameError: test(None, 'a_glob_B_loc.x', 1785)
        del x
        try: test(x, None, 1787)
        except NameError: test(None, None, 1788)
    class a_glob_B_ncap:
        try: test(x, None, 1790)
        except NameError: test(None, None, 1791)
        def a_glob_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_glob_B_ncap.x"
        a_glob_B_ncap_setfunc()
        try: test(x, 'a_glob_B_ncap.x', 1795)
        except NameError: test(None, 'a_glob_B_ncap.x', 1796)
        def a_glob_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_glob_B_ncap_delfunc()
        try: test(x, None, 1800)
        except NameError: test(None, None, 1801)
        x = "a_glob_B_ncap.x"
        try: test(x, 'a_glob_B_ncap.x', 1803)
        except NameError: test(None, 'a_glob_B_ncap.x', 1804)
        del x
        try: test(x, None, 1806)
        except NameError: test(None, None, 1807)
    def a_glob_b():
        pass
    a_glob_b()
    def a_glob_b_use():
        try: test(x, None, 1812)
        except NameError: test(None, None, 1813)
    a_glob_b_use()
    def a_glob_b_anno():
        x: str
        try: test(x, None, 1817)
        except NameError: test(None, None, 1818)
    a_glob_b_anno()
    def a_glob_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1823)
        else: error("Enclosed binding exists", 1824)
    a_glob_b_nloc()
    def a_glob_b_glob():
        global x
        try: test(x, None, 1828)
        except NameError: test(None, None, 1829)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1831)
        except NameError: test(None, 'x', 1832)
        def a_glob_b_glob_delfunc():
            global x; del x
        a_glob_b_glob_delfunc()
        try: test(x, None, 1836)
        except NameError: test(None, None, 1837)
        x = "x"
        try: test(x, 'x', 1839)
        except NameError: test(None, 'x', 1840)
        del x
        try: test(x, None, 1842)
        except NameError: test(None, None, 1843)
    a_glob_b_glob()
    def a_glob_b_loc():
        try: test(x, None, 1846)
        except NameError: test(None, None, 1847)
        [x := _ for _ in ["a_glob_b_loc.x"]]
        try: test(x, 'a_glob_b_loc.x', 1849)
        except NameError: test(None, 'a_glob_b_loc.x', 1850)
        def a_glob_b_loc_delfunc():
            nonlocal x; del x
        a_glob_b_loc_delfunc()
        try: test(x, None, 1854)
        except NameError: test(None, None, 1855)
        x = "a_glob_b_loc.x"
        try: test(x, 'a_glob_b_loc.x', 1857)
        except NameError: test(None, 'a_glob_b_loc.x', 1858)
        del x
        try: test(x, None, 1860)
        except NameError: test(None, None, 1861)
    a_glob_b_loc()
    def a_glob_b_ncap():
        try: test(x, None, 1864)
        except NameError: test(None, None, 1865)
        [x := _ for _ in ["a_glob_b_ncap.x"]]
        try: test(x, 'a_glob_b_ncap.x', 1867)
        except NameError: test(None, 'a_glob_b_ncap.x', 1868)
        def a_glob_b_ncap_delfunc():
            nonlocal x; del x
        a_glob_b_ncap_delfunc()
        try: test(x, None, 1872)
        except NameError: test(None, None, 1873)
        x = "a_glob_b_ncap.x"
        try: test(x, 'a_glob_b_ncap.x', 1875)
        except NameError: test(None, 'a_glob_b_ncap.x', 1876)
        del x
        try: test(x, None, 1878)
        except NameError: test(None, None, 1879)
    a_glob_b_ncap()
    [x := _ for _ in ["x"]]
    try: test(x, 'x', 1882)
    except NameError: test(None, 'x', 1883)
    def a_glob_delfunc():
        global x; del x
    a_glob_delfunc()
    try: test(x, None, 1887)
    except NameError: test(None, None, 1888)
    x = "x"
    try: test(x, 'x', 1890)
    except NameError: test(None, 'x', 1891)
    class a_glob_B2:
        pass
    class a_glob_B2_use:
        try: test(x, 'x', 1895)
        except NameError: test(None, 'x', 1896)
    class a_glob_B2_anno:
        x: str
        try: test(x, 'x', 1899)
        except NameError: test(None, 'x', 1900)
    class a_glob_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1904)
        else: error("Enclosed binding exists", 1905)
    class a_glob_B2_glob:
        global x
        try: test(x, 'x', 1908)
        except NameError: test(None, 'x', 1909)
        del x
        try: test(x, None, 1911)
        except NameError: test(None, None, 1912)
        def a_glob_B2_glob_setfunc():
            global x; x = "x"
        a_glob_B2_glob_setfunc()
        try: test(x, 'x', 1916)
        except NameError: test(None, 'x', 1917)
        def a_glob_B2_glob_delfunc():
            global x; del x
        a_glob_B2_glob_delfunc()
        try: test(x, None, 1921)
        except NameError: test(None, None, 1922)
        x = "x"
        try: test(x, 'x', 1924)
        except NameError: test(None, 'x', 1925)
    class a_glob_B2_loc:
        try: test(x, 'x', 1927)
        except NameError: test(None, 'x', 1928)
        def a_glob_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_glob_B2_loc.x"
        a_glob_B2_loc_setfunc()
        try: test(x, 'a_glob_B2_loc.x', 1932)
        except NameError: test(None, 'a_glob_B2_loc.x', 1933)
        def a_glob_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_glob_B2_loc_delfunc()
        try: test(x, 'x', 1937)
        except NameError: test(None, 'x', 1938)
        x = "a_glob_B2_loc.x"
        try: test(x, 'a_glob_B2_loc.x', 1940)
        except NameError: test(None, 'a_glob_B2_loc.x', 1941)
        del x
        try: test(x, 'x', 1943)
        except NameError: test(None, 'x', 1944)
    class a_glob_B2_ncap:
        try: test(x, 'x', 1946)
        except NameError: test(None, 'x', 1947)
        def a_glob_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_glob_B2_ncap.x"
        a_glob_B2_ncap_setfunc()
        try: test(x, 'a_glob_B2_ncap.x', 1951)
        except NameError: test(None, 'a_glob_B2_ncap.x', 1952)
        def a_glob_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_glob_B2_ncap_delfunc()
        try: test(x, 'x', 1956)
        except NameError: test(None, 'x', 1957)
        x = "a_glob_B2_ncap.x"
        try: test(x, 'a_glob_B2_ncap.x', 1959)
        except NameError: test(None, 'a_glob_B2_ncap.x', 1960)
        del x
        try: test(x, 'x', 1962)
        except NameError: test(None, 'x', 1963)
    def a_glob_b2():
        pass
    a_glob_b2()
    def a_glob_b2_use():
        try: test(x, 'x', 1968)
        except NameError: test(None, 'x', 1969)
    a_glob_b2_use()
    def a_glob_b2_anno():
        x: str
        try: test(x, None, 1973)
        except NameError: test(None, None, 1974)
    a_glob_b2_anno()
    def a_glob_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1979)
        else: error("Enclosed binding exists", 1980)
    a_glob_b2_nloc()
    def a_glob_b2_glob():
        global x
        try: test(x, 'x', 1984)
        except NameError: test(None, 'x', 1985)
        del x
        try: test(x, None, 1987)
        except NameError: test(None, None, 1988)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1990)
        except NameError: test(None, 'x', 1991)
        def a_glob_b2_glob_delfunc():
            global x; del x
        a_glob_b2_glob_delfunc()
        try: test(x, None, 1995)
        except NameError: test(None, None, 1996)
        x = "x"
        try: test(x, 'x', 1998)
        except NameError: test(None, 'x', 1999)
    a_glob_b2_glob()
    def a_glob_b2_loc():
        try: test(x, None, 2002)
        except NameError: test(None, None, 2003)
        [x := _ for _ in ["a_glob_b2_loc.x"]]
        try: test(x, 'a_glob_b2_loc.x', 2005)
        except NameError: test(None, 'a_glob_b2_loc.x', 2006)
        def a_glob_b2_loc_delfunc():
            nonlocal x; del x
        a_glob_b2_loc_delfunc()
        try: test(x, None, 2010)
        except NameError: test(None, None, 2011)
        x = "a_glob_b2_loc.x"
        try: test(x, 'a_glob_b2_loc.x', 2013)
        except NameError: test(None, 'a_glob_b2_loc.x', 2014)
        del x
        try: test(x, None, 2016)
        except NameError: test(None, None, 2017)
    a_glob_b2_loc()
    def a_glob_b2_ncap():
        try: test(x, None, 2020)
        except NameError: test(None, None, 2021)
        [x := _ for _ in ["a_glob_b2_ncap.x"]]
        try: test(x, 'a_glob_b2_ncap.x', 2023)
        except NameError: test(None, 'a_glob_b2_ncap.x', 2024)
        def a_glob_b2_ncap_delfunc():
            nonlocal x; del x
        a_glob_b2_ncap_delfunc()
        try: test(x, None, 2028)
        except NameError: test(None, None, 2029)
        x = "a_glob_b2_ncap.x"
        try: test(x, 'a_glob_b2_ncap.x', 2031)
        except NameError: test(None, 'a_glob_b2_ncap.x', 2032)
        del x
        try: test(x, None, 2034)
        except NameError: test(None, None, 2035)
    a_glob_b2_ncap()
    del x
    try: test(x, None, 2038)
    except NameError: test(None, None, 2039)
a_glob()
def a_loc():
    try: test(x, None, 2042)
    except NameError: test(None, None, 2043)
    class a_loc_B:
        pass
    class a_loc_B_use:
        try: test(x, None, 2047)
        except NameError: test(None, None, 2048)
    class a_loc_B_anno:
        x: str
        try: test(x, None, 2051)
        except NameError: test(None, None, 2052)
    class a_loc_B_nloc:
        nonlocal x
        try: test(x, None, 2055)
        except NameError: test(None, None, 2056)
        def a_loc_B_nloc_setfunc():
            nonlocal x; x = "a_loc.x"
        a_loc_B_nloc_setfunc()
        try: test(x, 'a_loc.x', 2060)
        except NameError: test(None, 'a_loc.x', 2061)
        def a_loc_B_nloc_delfunc():
            nonlocal x; del x
        a_loc_B_nloc_delfunc()
        try: test(x, None, 2065)
        except NameError: test(None, None, 2066)
        x = "a_loc.x"
        try: test(x, 'a_loc.x', 2068)
        except NameError: test(None, 'a_loc.x', 2069)
        del x
        try: test(x, None, 2071)
        except NameError: test(None, None, 2072)
    class a_loc_B_glob:
        global x
        try: test(x, None, 2075)
        except NameError: test(None, None, 2076)
        def a_loc_B_glob_setfunc():
            global x; x = "x"
        a_loc_B_glob_setfunc()
        try: test(x, 'x', 2080)
        except NameError: test(None, 'x', 2081)
        def a_loc_B_glob_delfunc():
            global x; del x
        a_loc_B_glob_delfunc()
        try: test(x, None, 2085)
        except NameError: test(None, None, 2086)
        x = "x"
        try: test(x, 'x', 2088)
        except NameError: test(None, 'x', 2089)
        del x
        try: test(x, None, 2091)
        except NameError: test(None, None, 2092)
    class a_loc_B_loc:
        try: test(x, None, 2094)
        except NameError: test(None, None, 2095)
        def a_loc_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_loc_B_loc.x"
        a_loc_B_loc_setfunc()
        try: test(x, 'a_loc_B_loc.x', 2099)
        except NameError: test(None, 'a_loc_B_loc.x', 2100)
        def a_loc_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_loc_B_loc_delfunc()
        try: test(x, None, 2104)
        except NameError: test(None, None, 2105)
        x = "a_loc_B_loc.x"
        try: test(x, 'a_loc_B_loc.x', 2107)
        except NameError: test(None, 'a_loc_B_loc.x', 2108)
        del x
        try: test(x, None, 2110)
        except NameError: test(None, None, 2111)
    class a_loc_B_ncap:
        try: test(x, None, 2113)
        except NameError: test(None, None, 2114)
        def a_loc_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_loc_B_ncap.x"
        a_loc_B_ncap_setfunc()
        try: test(x, 'a_loc_B_ncap.x', 2118)
        except NameError: test(None, 'a_loc_B_ncap.x', 2119)
        def a_loc_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_loc_B_ncap_delfunc()
        try: test(x, None, 2123)
        except NameError: test(None, None, 2124)
        x = "a_loc_B_ncap.x"
        try: test(x, 'a_loc_B_ncap.x', 2126)
        except NameError: test(None, 'a_loc_B_ncap.x', 2127)
        del x
        try: test(x, None, 2129)
        except NameError: test(None, None, 2130)
    def a_loc_b():
        pass
    a_loc_b()
    def a_loc_b_use():
        try: test(x, None, 2135)
        except NameError: test(None, None, 2136)
    a_loc_b_use()
    def a_loc_b_anno():
        x: str
        try: test(x, None, 2140)
        except NameError: test(None, None, 2141)
    a_loc_b_anno()
    def a_loc_b_nloc():
        nonlocal x
        try: test(x, None, 2145)
        except NameError: test(None, None, 2146)
        [x := _ for _ in ["a_loc.x"]]
        try: test(x, 'a_loc.x', 2148)
        except NameError: test(None, 'a_loc.x', 2149)
        def a_loc_b_nloc_delfunc():
            nonlocal x; del x
        a_loc_b_nloc_delfunc()
        try: test(x, None, 2153)
        except NameError: test(None, None, 2154)
        x = "a_loc.x"
        try: test(x, 'a_loc.x', 2156)
        except NameError: test(None, 'a_loc.x', 2157)
        del x
        try: test(x, None, 2159)
        except NameError: test(None, None, 2160)
    a_loc_b_nloc()
    def a_loc_b_glob():
        global x
        try: test(x, None, 2164)
        except NameError: test(None, None, 2165)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2167)
        except NameError: test(None, 'x', 2168)
        def a_loc_b_glob_delfunc():
            global x; del x
        a_loc_b_glob_delfunc()
        try: test(x, None, 2172)
        except NameError: test(None, None, 2173)
        x = "x"
        try: test(x, 'x', 2175)
        except NameError: test(None, 'x', 2176)
        del x
        try: test(x, None, 2178)
        except NameError: test(None, None, 2179)
    a_loc_b_glob()
    def a_loc_b_loc():
        try: test(x, None, 2182)
        except NameError: test(None, None, 2183)
        [x := _ for _ in ["a_loc_b_loc.x"]]
        try: test(x, 'a_loc_b_loc.x', 2185)
        except NameError: test(None, 'a_loc_b_loc.x', 2186)
        def a_loc_b_loc_delfunc():
            nonlocal x; del x
        a_loc_b_loc_delfunc()
        try: test(x, None, 2190)
        except NameError: test(None, None, 2191)
        x = "a_loc_b_loc.x"
        try: test(x, 'a_loc_b_loc.x', 2193)
        except NameError: test(None, 'a_loc_b_loc.x', 2194)
        del x
        try: test(x, None, 2196)
        except NameError: test(None, None, 2197)
    a_loc_b_loc()
    def a_loc_b_ncap():
        try: test(x, None, 2200)
        except NameError: test(None, None, 2201)
        [x := _ for _ in ["a_loc_b_ncap.x"]]
        try: test(x, 'a_loc_b_ncap.x', 2203)
        except NameError: test(None, 'a_loc_b_ncap.x', 2204)
        def a_loc_b_ncap_delfunc():
            nonlocal x; del x
        a_loc_b_ncap_delfunc()
        try: test(x, None, 2208)
        except NameError: test(None, None, 2209)
        x = "a_loc_b_ncap.x"
        try: test(x, 'a_loc_b_ncap.x', 2211)
        except NameError: test(None, 'a_loc_b_ncap.x', 2212)
        del x
        try: test(x, None, 2214)
        except NameError: test(None, None, 2215)
    a_loc_b_ncap()
    [x := _ for _ in ["a_loc.x"]]
    try: test(x, 'a_loc.x', 2218)
    except NameError: test(None, 'a_loc.x', 2219)
    def a_loc_delfunc():
        nonlocal x; del x
    a_loc_delfunc()
    try: test(x, None, 2223)
    except NameError: test(None, None, 2224)
    x = "a_loc.x"
    try: test(x, 'a_loc.x', 2226)
    except NameError: test(None, 'a_loc.x', 2227)
    class a_loc_B2:
        pass
    class a_loc_B2_use:
        try: test(x, 'a_loc.x', 2231)
        except NameError: test(None, 'a_loc.x', 2232)
    class a_loc_B2_anno:
        x: str
        try: test(x, None, 2235)
        except NameError: test(None, None, 2236)
    class a_loc_B2_nloc:
        nonlocal x
        try: test(x, 'a_loc.x', 2239)
        except NameError: test(None, 'a_loc.x', 2240)
        del x
        try: test(x, None, 2242)
        except NameError: test(None, None, 2243)
        def a_loc_B2_nloc_setfunc():
            nonlocal x; x = "a_loc.x"
        a_loc_B2_nloc_setfunc()
        try: test(x, 'a_loc.x', 2247)
        except NameError: test(None, 'a_loc.x', 2248)
        def a_loc_B2_nloc_delfunc():
            nonlocal x; del x
        a_loc_B2_nloc_delfunc()
        try: test(x, None, 2252)
        except NameError: test(None, None, 2253)
        x = "a_loc.x"
        try: test(x, 'a_loc.x', 2255)
        except NameError: test(None, 'a_loc.x', 2256)
    class a_loc_B2_glob:
        global x
        try: test(x, None, 2259)
        except NameError: test(None, None, 2260)
        def a_loc_B2_glob_setfunc():
            global x; x = "x"
        a_loc_B2_glob_setfunc()
        try: test(x, 'x', 2264)
        except NameError: test(None, 'x', 2265)
        def a_loc_B2_glob_delfunc():
            global x; del x
        a_loc_B2_glob_delfunc()
        try: test(x, None, 2269)
        except NameError: test(None, None, 2270)
        x = "x"
        try: test(x, 'x', 2272)
        except NameError: test(None, 'x', 2273)
        del x
        try: test(x, None, 2275)
        except NameError: test(None, None, 2276)
    class a_loc_B2_loc:
        try: test(x, None, 2278)
        except NameError: test(None, None, 2279)
        def a_loc_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_loc_B2_loc.x"
        a_loc_B2_loc_setfunc()
        try: test(x, 'a_loc_B2_loc.x', 2283)
        except NameError: test(None, 'a_loc_B2_loc.x', 2284)
        def a_loc_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_loc_B2_loc_delfunc()
        try: test(x, None, 2288)
        except NameError: test(None, None, 2289)
        x = "a_loc_B2_loc.x"
        try: test(x, 'a_loc_B2_loc.x', 2291)
        except NameError: test(None, 'a_loc_B2_loc.x', 2292)
        del x
        try: test(x, None, 2294)
        except NameError: test(None, None, 2295)
    class a_loc_B2_ncap:
        try: test(x, None, 2297)
        except NameError: test(None, None, 2298)
        def a_loc_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_loc_B2_ncap.x"
        a_loc_B2_ncap_setfunc()
        try: test(x, 'a_loc_B2_ncap.x', 2302)
        except NameError: test(None, 'a_loc_B2_ncap.x', 2303)
        def a_loc_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_loc_B2_ncap_delfunc()
        try: test(x, None, 2307)
        except NameError: test(None, None, 2308)
        x = "a_loc_B2_ncap.x"
        try: test(x, 'a_loc_B2_ncap.x', 2310)
        except NameError: test(None, 'a_loc_B2_ncap.x', 2311)
        del x
        try: test(x, None, 2313)
        except NameError: test(None, None, 2314)
    def a_loc_b2():
        pass
    a_loc_b2()
    def a_loc_b2_use():
        try: test(x, 'a_loc.x', 2319)
        except NameError: test(None, 'a_loc.x', 2320)
    a_loc_b2_use()
    def a_loc_b2_anno():
        x: str
        try: test(x, None, 2324)
        except NameError: test(None, None, 2325)
    a_loc_b2_anno()
    def a_loc_b2_nloc():
        nonlocal x
        try: test(x, 'a_loc.x', 2329)
        except NameError: test(None, 'a_loc.x', 2330)
        del x
        try: test(x, None, 2332)
        except NameError: test(None, None, 2333)
        [x := _ for _ in ["a_loc.x"]]
        try: test(x, 'a_loc.x', 2335)
        except NameError: test(None, 'a_loc.x', 2336)
        def a_loc_b2_nloc_delfunc():
            nonlocal x; del x
        a_loc_b2_nloc_delfunc()
        try: test(x, None, 2340)
        except NameError: test(None, None, 2341)
        x = "a_loc.x"
        try: test(x, 'a_loc.x', 2343)
        except NameError: test(None, 'a_loc.x', 2344)
    a_loc_b2_nloc()
    def a_loc_b2_glob():
        global x
        try: test(x, None, 2348)
        except NameError: test(None, None, 2349)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2351)
        except NameError: test(None, 'x', 2352)
        def a_loc_b2_glob_delfunc():
            global x; del x
        a_loc_b2_glob_delfunc()
        try: test(x, None, 2356)
        except NameError: test(None, None, 2357)
        x = "x"
        try: test(x, 'x', 2359)
        except NameError: test(None, 'x', 2360)
        del x
        try: test(x, None, 2362)
        except NameError: test(None, None, 2363)
    a_loc_b2_glob()
    def a_loc_b2_loc():
        try: test(x, None, 2366)
        except NameError: test(None, None, 2367)
        [x := _ for _ in ["a_loc_b2_loc.x"]]
        try: test(x, 'a_loc_b2_loc.x', 2369)
        except NameError: test(None, 'a_loc_b2_loc.x', 2370)
        def a_loc_b2_loc_delfunc():
            nonlocal x; del x
        a_loc_b2_loc_delfunc()
        try: test(x, None, 2374)
        except NameError: test(None, None, 2375)
        x = "a_loc_b2_loc.x"
        try: test(x, 'a_loc_b2_loc.x', 2377)
        except NameError: test(None, 'a_loc_b2_loc.x', 2378)
        del x
        try: test(x, None, 2380)
        except NameError: test(None, None, 2381)
    a_loc_b2_loc()
    def a_loc_b2_ncap():
        try: test(x, None, 2384)
        except NameError: test(None, None, 2385)
        [x := _ for _ in ["a_loc_b2_ncap.x"]]
        try: test(x, 'a_loc_b2_ncap.x', 2387)
        except NameError: test(None, 'a_loc_b2_ncap.x', 2388)
        def a_loc_b2_ncap_delfunc():
            nonlocal x; del x
        a_loc_b2_ncap_delfunc()
        try: test(x, None, 2392)
        except NameError: test(None, None, 2393)
        x = "a_loc_b2_ncap.x"
        try: test(x, 'a_loc_b2_ncap.x', 2395)
        except NameError: test(None, 'a_loc_b2_ncap.x', 2396)
        del x
        try: test(x, None, 2398)
        except NameError: test(None, None, 2399)
    a_loc_b2_ncap()
    del x
    try: test(x, None, 2402)
    except NameError: test(None, None, 2403)
a_loc()
def a_ncap():
    try: test(x, None, 2406)
    except NameError: test(None, None, 2407)
    class a_ncap_B:
        pass
    class a_ncap_B_glob:
        global x
        try: test(x, None, 2412)
        except NameError: test(None, None, 2413)
        def a_ncap_B_glob_setfunc():
            global x; x = "x"
        a_ncap_B_glob_setfunc()
        try: test(x, 'x', 2417)
        except NameError: test(None, 'x', 2418)
        def a_ncap_B_glob_delfunc():
            global x; del x
        a_ncap_B_glob_delfunc()
        try: test(x, None, 2422)
        except NameError: test(None, None, 2423)
        x = "x"
        try: test(x, 'x', 2425)
        except NameError: test(None, 'x', 2426)
        del x
        try: test(x, None, 2428)
        except NameError: test(None, None, 2429)
    class a_ncap_B_loc:
        try: test(x, None, 2431)
        except NameError: test(None, None, 2432)
        def a_ncap_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_ncap_B_loc.x"
        a_ncap_B_loc_setfunc()
        try: test(x, 'a_ncap_B_loc.x', 2436)
        except NameError: test(None, 'a_ncap_B_loc.x', 2437)
        def a_ncap_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_ncap_B_loc_delfunc()
        try: test(x, None, 2441)
        except NameError: test(None, None, 2442)
        x = "a_ncap_B_loc.x"
        try: test(x, 'a_ncap_B_loc.x', 2444)
        except NameError: test(None, 'a_ncap_B_loc.x', 2445)
        del x
        try: test(x, None, 2447)
        except NameError: test(None, None, 2448)
    def a_ncap_b():
        pass
    a_ncap_b()
    def a_ncap_b_glob():
        global x
        try: test(x, None, 2454)
        except NameError: test(None, None, 2455)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2457)
        except NameError: test(None, 'x', 2458)
        def a_ncap_b_glob_delfunc():
            global x; del x
        a_ncap_b_glob_delfunc()
        try: test(x, None, 2462)
        except NameError: test(None, None, 2463)
        x = "x"
        try: test(x, 'x', 2465)
        except NameError: test(None, 'x', 2466)
        del x
        try: test(x, None, 2468)
        except NameError: test(None, None, 2469)
    a_ncap_b_glob()
    def a_ncap_b_loc():
        try: test(x, None, 2472)
        except NameError: test(None, None, 2473)
        [x := _ for _ in ["a_ncap_b_loc.x"]]
        try: test(x, 'a_ncap_b_loc.x', 2475)
        except NameError: test(None, 'a_ncap_b_loc.x', 2476)
        def a_ncap_b_loc_delfunc():
            nonlocal x; del x
        a_ncap_b_loc_delfunc()
        try: test(x, None, 2480)
        except NameError: test(None, None, 2481)
        x = "a_ncap_b_loc.x"
        try: test(x, 'a_ncap_b_loc.x', 2483)
        except NameError: test(None, 'a_ncap_b_loc.x', 2484)
        del x
        try: test(x, None, 2486)
        except NameError: test(None, None, 2487)
    a_ncap_b_loc()
    [x := _ for _ in ["a_ncap.x"]]
    try: test(x, 'a_ncap.x', 2490)
    except NameError: test(None, 'a_ncap.x', 2491)
    def a_ncap_delfunc():
        nonlocal x; del x
    a_ncap_delfunc()
    try: test(x, None, 2495)
    except NameError: test(None, None, 2496)
    x = "a_ncap.x"
    try: test(x, 'a_ncap.x', 2498)
    except NameError: test(None, 'a_ncap.x', 2499)
    class a_ncap_B2:
        pass
    class a_ncap_B2_glob:
        global x
        try: test(x, None, 2504)
        except NameError: test(None, None, 2505)
        def a_ncap_B2_glob_setfunc():
            global x; x = "x"
        a_ncap_B2_glob_setfunc()
        try: test(x, 'x', 2509)
        except NameError: test(None, 'x', 2510)
        def a_ncap_B2_glob_delfunc():
            global x; del x
        a_ncap_B2_glob_delfunc()
        try: test(x, None, 2514)
        except NameError: test(None, None, 2515)
        x = "x"
        try: test(x, 'x', 2517)
        except NameError: test(None, 'x', 2518)
        del x
        try: test(x, None, 2520)
        except NameError: test(None, None, 2521)
    class a_ncap_B2_loc:
        try: test(x, None, 2523)
        except NameError: test(None, None, 2524)
        def a_ncap_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_ncap_B2_loc.x"
        a_ncap_B2_loc_setfunc()
        try: test(x, 'a_ncap_B2_loc.x', 2528)
        except NameError: test(None, 'a_ncap_B2_loc.x', 2529)
        def a_ncap_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_ncap_B2_loc_delfunc()
        try: test(x, None, 2533)
        except NameError: test(None, None, 2534)
        x = "a_ncap_B2_loc.x"
        try: test(x, 'a_ncap_B2_loc.x', 2536)
        except NameError: test(None, 'a_ncap_B2_loc.x', 2537)
        del x
        try: test(x, None, 2539)
        except NameError: test(None, None, 2540)
    def a_ncap_b2():
        pass
    a_ncap_b2()
    def a_ncap_b2_glob():
        global x
        try: test(x, None, 2546)
        except NameError: test(None, None, 2547)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2549)
        except NameError: test(None, 'x', 2550)
        def a_ncap_b2_glob_delfunc():
            global x; del x
        a_ncap_b2_glob_delfunc()
        try: test(x, None, 2554)
        except NameError: test(None, None, 2555)
        x = "x"
        try: test(x, 'x', 2557)
        except NameError: test(None, 'x', 2558)
        del x
        try: test(x, None, 2560)
        except NameError: test(None, None, 2561)
    a_ncap_b2_glob()
    def a_ncap_b2_loc():
        try: test(x, None, 2564)
        except NameError: test(None, None, 2565)
        [x := _ for _ in ["a_ncap_b2_loc.x"]]
        try: test(x, 'a_ncap_b2_loc.x', 2567)
        except NameError: test(None, 'a_ncap_b2_loc.x', 2568)
        def a_ncap_b2_loc_delfunc():
            nonlocal x; del x
        a_ncap_b2_loc_delfunc()
        try: test(x, None, 2572)
        except NameError: test(None, None, 2573)
        x = "a_ncap_b2_loc.x"
        try: test(x, 'a_ncap_b2_loc.x', 2575)
        except NameError: test(None, 'a_ncap_b2_loc.x', 2576)
        del x
        try: test(x, None, 2578)
        except NameError: test(None, None, 2579)
    a_ncap_b2_loc()
    del x
    try: test(x, None, 2582)
    except NameError: test(None, None, 2583)
a_ncap()
[x := _ for _ in ["x"]]
try: test(x, 'x', 2586)
except NameError: test(None, 'x', 2587)
def _delfunc():
    global x; del x
_delfunc()
try: test(x, None, 2591)
except NameError: test(None, None, 2592)
x = "x"
try: test(x, 'x', 2594)
except NameError: test(None, 'x', 2595)
class A2:
    class A2_B:
        pass
    class A2_B_use:
        try: test(x, 'x', 2600)
        except NameError: test(None, 'x', 2601)
    class A2_B_anno:
        x: str
        try: test(x, 'x', 2604)
        except NameError: test(None, 'x', 2605)
    class A2_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2609)
        else: error("Enclosed binding exists", 2610)
    class A2_B_glob:
        global x
        try: test(x, 'x', 2613)
        except NameError: test(None, 'x', 2614)
        del x
        try: test(x, None, 2616)
        except NameError: test(None, None, 2617)
        def A2_B_glob_setfunc():
            global x; x = "x"
        A2_B_glob_setfunc()
        try: test(x, 'x', 2621)
        except NameError: test(None, 'x', 2622)
        def A2_B_glob_delfunc():
            global x; del x
        A2_B_glob_delfunc()
        try: test(x, None, 2626)
        except NameError: test(None, None, 2627)
        x = "x"
        try: test(x, 'x', 2629)
        except NameError: test(None, 'x', 2630)
    class A2_B_loc:
        try: test(x, 'x', 2632)
        except NameError: test(None, 'x', 2633)
        def A2_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_B_loc.x"
        A2_B_loc_setfunc()
        try: test(x, 'A2_B_loc.x', 2637)
        except NameError: test(None, 'A2_B_loc.x', 2638)
        def A2_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_B_loc_delfunc()
        try: test(x, 'x', 2642)
        except NameError: test(None, 'x', 2643)
        x = "A2_B_loc.x"
        try: test(x, 'A2_B_loc.x', 2645)
        except NameError: test(None, 'A2_B_loc.x', 2646)
        del x
        try: test(x, 'x', 2648)
        except NameError: test(None, 'x', 2649)
    class A2_B_ncap:
        try: test(x, 'x', 2651)
        except NameError: test(None, 'x', 2652)
        def A2_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_B_ncap.x"
        A2_B_ncap_setfunc()
        try: test(x, 'A2_B_ncap.x', 2656)
        except NameError: test(None, 'A2_B_ncap.x', 2657)
        def A2_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_B_ncap_delfunc()
        try: test(x, 'x', 2661)
        except NameError: test(None, 'x', 2662)
        x = "A2_B_ncap.x"
        try: test(x, 'A2_B_ncap.x', 2664)
        except NameError: test(None, 'A2_B_ncap.x', 2665)
        del x
        try: test(x, 'x', 2667)
        except NameError: test(None, 'x', 2668)
    def A2_b():
        pass
    A2_b()
    def A2_b_use():
        try: test(x, 'x', 2673)
        except NameError: test(None, 'x', 2674)
    A2_b_use()
    def A2_b_anno():
        x: str
        try: test(x, None, 2678)
        except NameError: test(None, None, 2679)
    A2_b_anno()
    def A2_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2684)
        else: error("Enclosed binding exists", 2685)
    A2_b_nloc()
    def A2_b_glob():
        global x
        try: test(x, 'x', 2689)
        except NameError: test(None, 'x', 2690)
        del x
        try: test(x, None, 2692)
        except NameError: test(None, None, 2693)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2695)
        except NameError: test(None, 'x', 2696)
        def A2_b_glob_delfunc():
            global x; del x
        A2_b_glob_delfunc()
        try: test(x, None, 2700)
        except NameError: test(None, None, 2701)
        x = "x"
        try: test(x, 'x', 2703)
        except NameError: test(None, 'x', 2704)
    A2_b_glob()
    def A2_b_loc():
        try: test(x, None, 2707)
        except NameError: test(None, None, 2708)
        [x := _ for _ in ["A2_b_loc.x"]]
        try: test(x, 'A2_b_loc.x', 2710)
        except NameError: test(None, 'A2_b_loc.x', 2711)
        def A2_b_loc_delfunc():
            nonlocal x; del x
        A2_b_loc_delfunc()
        try: test(x, None, 2715)
        except NameError: test(None, None, 2716)
        x = "A2_b_loc.x"
        try: test(x, 'A2_b_loc.x', 2718)
        except NameError: test(None, 'A2_b_loc.x', 2719)
        del x
        try: test(x, None, 2721)
        except NameError: test(None, None, 2722)
    A2_b_loc()
    def A2_b_ncap():
        try: test(x, None, 2725)
        except NameError: test(None, None, 2726)
        [x := _ for _ in ["A2_b_ncap.x"]]
        try: test(x, 'A2_b_ncap.x', 2728)
        except NameError: test(None, 'A2_b_ncap.x', 2729)
        def A2_b_ncap_delfunc():
            nonlocal x; del x
        A2_b_ncap_delfunc()
        try: test(x, None, 2733)
        except NameError: test(None, None, 2734)
        x = "A2_b_ncap.x"
        try: test(x, 'A2_b_ncap.x', 2736)
        except NameError: test(None, 'A2_b_ncap.x', 2737)
        del x
        try: test(x, None, 2739)
        except NameError: test(None, None, 2740)
    A2_b_ncap()
class A2_use:
    try: test(x, 'x', 2743)
    except NameError: test(None, 'x', 2744)
    class A2_use_B:
        pass
    class A2_use_B_use:
        try: test(x, 'x', 2748)
        except NameError: test(None, 'x', 2749)
    class A2_use_B_anno:
        x: str
        try: test(x, 'x', 2752)
        except NameError: test(None, 'x', 2753)
    class A2_use_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2757)
        else: error("Enclosed binding exists", 2758)
    class A2_use_B_glob:
        global x
        try: test(x, 'x', 2761)
        except NameError: test(None, 'x', 2762)
        del x
        try: test(x, None, 2764)
        except NameError: test(None, None, 2765)
        def A2_use_B_glob_setfunc():
            global x; x = "x"
        A2_use_B_glob_setfunc()
        try: test(x, 'x', 2769)
        except NameError: test(None, 'x', 2770)
        def A2_use_B_glob_delfunc():
            global x; del x
        A2_use_B_glob_delfunc()
        try: test(x, None, 2774)
        except NameError: test(None, None, 2775)
        x = "x"
        try: test(x, 'x', 2777)
        except NameError: test(None, 'x', 2778)
    class A2_use_B_loc:
        try: test(x, 'x', 2780)
        except NameError: test(None, 'x', 2781)
        def A2_use_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_use_B_loc.x"
        A2_use_B_loc_setfunc()
        try: test(x, 'A2_use_B_loc.x', 2785)
        except NameError: test(None, 'A2_use_B_loc.x', 2786)
        def A2_use_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_use_B_loc_delfunc()
        try: test(x, 'x', 2790)
        except NameError: test(None, 'x', 2791)
        x = "A2_use_B_loc.x"
        try: test(x, 'A2_use_B_loc.x', 2793)
        except NameError: test(None, 'A2_use_B_loc.x', 2794)
        del x
        try: test(x, 'x', 2796)
        except NameError: test(None, 'x', 2797)
    class A2_use_B_ncap:
        try: test(x, 'x', 2799)
        except NameError: test(None, 'x', 2800)
        def A2_use_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_use_B_ncap.x"
        A2_use_B_ncap_setfunc()
        try: test(x, 'A2_use_B_ncap.x', 2804)
        except NameError: test(None, 'A2_use_B_ncap.x', 2805)
        def A2_use_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_use_B_ncap_delfunc()
        try: test(x, 'x', 2809)
        except NameError: test(None, 'x', 2810)
        x = "A2_use_B_ncap.x"
        try: test(x, 'A2_use_B_ncap.x', 2812)
        except NameError: test(None, 'A2_use_B_ncap.x', 2813)
        del x
        try: test(x, 'x', 2815)
        except NameError: test(None, 'x', 2816)
    def A2_use_b():
        pass
    A2_use_b()
    def A2_use_b_use():
        try: test(x, 'x', 2821)
        except NameError: test(None, 'x', 2822)
    A2_use_b_use()
    def A2_use_b_anno():
        x: str
        try: test(x, None, 2826)
        except NameError: test(None, None, 2827)
    A2_use_b_anno()
    def A2_use_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2832)
        else: error("Enclosed binding exists", 2833)
    A2_use_b_nloc()
    def A2_use_b_glob():
        global x
        try: test(x, 'x', 2837)
        except NameError: test(None, 'x', 2838)
        del x
        try: test(x, None, 2840)
        except NameError: test(None, None, 2841)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2843)
        except NameError: test(None, 'x', 2844)
        def A2_use_b_glob_delfunc():
            global x; del x
        A2_use_b_glob_delfunc()
        try: test(x, None, 2848)
        except NameError: test(None, None, 2849)
        x = "x"
        try: test(x, 'x', 2851)
        except NameError: test(None, 'x', 2852)
    A2_use_b_glob()
    def A2_use_b_loc():
        try: test(x, None, 2855)
        except NameError: test(None, None, 2856)
        [x := _ for _ in ["A2_use_b_loc.x"]]
        try: test(x, 'A2_use_b_loc.x', 2858)
        except NameError: test(None, 'A2_use_b_loc.x', 2859)
        def A2_use_b_loc_delfunc():
            nonlocal x; del x
        A2_use_b_loc_delfunc()
        try: test(x, None, 2863)
        except NameError: test(None, None, 2864)
        x = "A2_use_b_loc.x"
        try: test(x, 'A2_use_b_loc.x', 2866)
        except NameError: test(None, 'A2_use_b_loc.x', 2867)
        del x
        try: test(x, None, 2869)
        except NameError: test(None, None, 2870)
    A2_use_b_loc()
    def A2_use_b_ncap():
        try: test(x, None, 2873)
        except NameError: test(None, None, 2874)
        [x := _ for _ in ["A2_use_b_ncap.x"]]
        try: test(x, 'A2_use_b_ncap.x', 2876)
        except NameError: test(None, 'A2_use_b_ncap.x', 2877)
        def A2_use_b_ncap_delfunc():
            nonlocal x; del x
        A2_use_b_ncap_delfunc()
        try: test(x, None, 2881)
        except NameError: test(None, None, 2882)
        x = "A2_use_b_ncap.x"
        try: test(x, 'A2_use_b_ncap.x', 2884)
        except NameError: test(None, 'A2_use_b_ncap.x', 2885)
        del x
        try: test(x, None, 2887)
        except NameError: test(None, None, 2888)
    A2_use_b_ncap()
class A2_anno:
    x: str
    try: test(x, 'x', 2892)
    except NameError: test(None, 'x', 2893)
    class A2_anno_B:
        pass
    class A2_anno_B_use:
        try: test(x, 'x', 2897)
        except NameError: test(None, 'x', 2898)
    class A2_anno_B_anno:
        x: str
        try: test(x, 'x', 2901)
        except NameError: test(None, 'x', 2902)
    class A2_anno_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2906)
        else: error("Enclosed binding exists", 2907)
    class A2_anno_B_glob:
        global x
        try: test(x, 'x', 2910)
        except NameError: test(None, 'x', 2911)
        del x
        try: test(x, None, 2913)
        except NameError: test(None, None, 2914)
        def A2_anno_B_glob_setfunc():
            global x; x = "x"
        A2_anno_B_glob_setfunc()
        try: test(x, 'x', 2918)
        except NameError: test(None, 'x', 2919)
        def A2_anno_B_glob_delfunc():
            global x; del x
        A2_anno_B_glob_delfunc()
        try: test(x, None, 2923)
        except NameError: test(None, None, 2924)
        x = "x"
        try: test(x, 'x', 2926)
        except NameError: test(None, 'x', 2927)
    class A2_anno_B_loc:
        try: test(x, 'x', 2929)
        except NameError: test(None, 'x', 2930)
        def A2_anno_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_anno_B_loc.x"
        A2_anno_B_loc_setfunc()
        try: test(x, 'A2_anno_B_loc.x', 2934)
        except NameError: test(None, 'A2_anno_B_loc.x', 2935)
        def A2_anno_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_anno_B_loc_delfunc()
        try: test(x, 'x', 2939)
        except NameError: test(None, 'x', 2940)
        x = "A2_anno_B_loc.x"
        try: test(x, 'A2_anno_B_loc.x', 2942)
        except NameError: test(None, 'A2_anno_B_loc.x', 2943)
        del x
        try: test(x, 'x', 2945)
        except NameError: test(None, 'x', 2946)
    class A2_anno_B_ncap:
        try: test(x, 'x', 2948)
        except NameError: test(None, 'x', 2949)
        def A2_anno_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_anno_B_ncap.x"
        A2_anno_B_ncap_setfunc()
        try: test(x, 'A2_anno_B_ncap.x', 2953)
        except NameError: test(None, 'A2_anno_B_ncap.x', 2954)
        def A2_anno_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_anno_B_ncap_delfunc()
        try: test(x, 'x', 2958)
        except NameError: test(None, 'x', 2959)
        x = "A2_anno_B_ncap.x"
        try: test(x, 'A2_anno_B_ncap.x', 2961)
        except NameError: test(None, 'A2_anno_B_ncap.x', 2962)
        del x
        try: test(x, 'x', 2964)
        except NameError: test(None, 'x', 2965)
    def A2_anno_b():
        pass
    A2_anno_b()
    def A2_anno_b_use():
        try: test(x, 'x', 2970)
        except NameError: test(None, 'x', 2971)
    A2_anno_b_use()
    def A2_anno_b_anno():
        x: str
        try: test(x, None, 2975)
        except NameError: test(None, None, 2976)
    A2_anno_b_anno()
    def A2_anno_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2981)
        else: error("Enclosed binding exists", 2982)
    A2_anno_b_nloc()
    def A2_anno_b_glob():
        global x
        try: test(x, 'x', 2986)
        except NameError: test(None, 'x', 2987)
        del x
        try: test(x, None, 2989)
        except NameError: test(None, None, 2990)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2992)
        except NameError: test(None, 'x', 2993)
        def A2_anno_b_glob_delfunc():
            global x; del x
        A2_anno_b_glob_delfunc()
        try: test(x, None, 2997)
        except NameError: test(None, None, 2998)
        x = "x"
        try: test(x, 'x', 3000)
        except NameError: test(None, 'x', 3001)
    A2_anno_b_glob()
    def A2_anno_b_loc():
        try: test(x, None, 3004)
        except NameError: test(None, None, 3005)
        [x := _ for _ in ["A2_anno_b_loc.x"]]
        try: test(x, 'A2_anno_b_loc.x', 3007)
        except NameError: test(None, 'A2_anno_b_loc.x', 3008)
        def A2_anno_b_loc_delfunc():
            nonlocal x; del x
        A2_anno_b_loc_delfunc()
        try: test(x, None, 3012)
        except NameError: test(None, None, 3013)
        x = "A2_anno_b_loc.x"
        try: test(x, 'A2_anno_b_loc.x', 3015)
        except NameError: test(None, 'A2_anno_b_loc.x', 3016)
        del x
        try: test(x, None, 3018)
        except NameError: test(None, None, 3019)
    A2_anno_b_loc()
    def A2_anno_b_ncap():
        try: test(x, None, 3022)
        except NameError: test(None, None, 3023)
        [x := _ for _ in ["A2_anno_b_ncap.x"]]
        try: test(x, 'A2_anno_b_ncap.x', 3025)
        except NameError: test(None, 'A2_anno_b_ncap.x', 3026)
        def A2_anno_b_ncap_delfunc():
            nonlocal x; del x
        A2_anno_b_ncap_delfunc()
        try: test(x, None, 3030)
        except NameError: test(None, None, 3031)
        x = "A2_anno_b_ncap.x"
        try: test(x, 'A2_anno_b_ncap.x', 3033)
        except NameError: test(None, 'A2_anno_b_ncap.x', 3034)
        del x
        try: test(x, None, 3036)
        except NameError: test(None, None, 3037)
    A2_anno_b_ncap()
class A2_nloc:
    # No enclosed binding exists.
    try: compile("nonlocal x", "<string>", "exec")
    except SyntaxError: test(None, None, 3042)
    else: error("Enclosed binding exists", 3043)
class A2_glob:
    global x
    try: test(x, 'x', 3046)
    except NameError: test(None, 'x', 3047)
    class A2_glob_B:
        pass
    class A2_glob_B_use:
        try: test(x, 'x', 3051)
        except NameError: test(None, 'x', 3052)
    class A2_glob_B_anno:
        x: str
        try: test(x, 'x', 3055)
        except NameError: test(None, 'x', 3056)
    class A2_glob_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3060)
        else: error("Enclosed binding exists", 3061)
    class A2_glob_B_glob:
        global x
        try: test(x, 'x', 3064)
        except NameError: test(None, 'x', 3065)
        del x
        try: test(x, None, 3067)
        except NameError: test(None, None, 3068)
        def A2_glob_B_glob_setfunc():
            global x; x = "x"
        A2_glob_B_glob_setfunc()
        try: test(x, 'x', 3072)
        except NameError: test(None, 'x', 3073)
        def A2_glob_B_glob_delfunc():
            global x; del x
        A2_glob_B_glob_delfunc()
        try: test(x, None, 3077)
        except NameError: test(None, None, 3078)
        x = "x"
        try: test(x, 'x', 3080)
        except NameError: test(None, 'x', 3081)
    class A2_glob_B_loc:
        try: test(x, 'x', 3083)
        except NameError: test(None, 'x', 3084)
        def A2_glob_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_glob_B_loc.x"
        A2_glob_B_loc_setfunc()
        try: test(x, 'A2_glob_B_loc.x', 3088)
        except NameError: test(None, 'A2_glob_B_loc.x', 3089)
        def A2_glob_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_glob_B_loc_delfunc()
        try: test(x, 'x', 3093)
        except NameError: test(None, 'x', 3094)
        x = "A2_glob_B_loc.x"
        try: test(x, 'A2_glob_B_loc.x', 3096)
        except NameError: test(None, 'A2_glob_B_loc.x', 3097)
        del x
        try: test(x, 'x', 3099)
        except NameError: test(None, 'x', 3100)
    class A2_glob_B_ncap:
        try: test(x, 'x', 3102)
        except NameError: test(None, 'x', 3103)
        def A2_glob_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_glob_B_ncap.x"
        A2_glob_B_ncap_setfunc()
        try: test(x, 'A2_glob_B_ncap.x', 3107)
        except NameError: test(None, 'A2_glob_B_ncap.x', 3108)
        def A2_glob_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_glob_B_ncap_delfunc()
        try: test(x, 'x', 3112)
        except NameError: test(None, 'x', 3113)
        x = "A2_glob_B_ncap.x"
        try: test(x, 'A2_glob_B_ncap.x', 3115)
        except NameError: test(None, 'A2_glob_B_ncap.x', 3116)
        del x
        try: test(x, 'x', 3118)
        except NameError: test(None, 'x', 3119)
    def A2_glob_b():
        pass
    A2_glob_b()
    def A2_glob_b_use():
        try: test(x, 'x', 3124)
        except NameError: test(None, 'x', 3125)
    A2_glob_b_use()
    def A2_glob_b_anno():
        x: str
        try: test(x, None, 3129)
        except NameError: test(None, None, 3130)
    A2_glob_b_anno()
    def A2_glob_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3135)
        else: error("Enclosed binding exists", 3136)
    A2_glob_b_nloc()
    def A2_glob_b_glob():
        global x
        try: test(x, 'x', 3140)
        except NameError: test(None, 'x', 3141)
        del x
        try: test(x, None, 3143)
        except NameError: test(None, None, 3144)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3146)
        except NameError: test(None, 'x', 3147)
        def A2_glob_b_glob_delfunc():
            global x; del x
        A2_glob_b_glob_delfunc()
        try: test(x, None, 3151)
        except NameError: test(None, None, 3152)
        x = "x"
        try: test(x, 'x', 3154)
        except NameError: test(None, 'x', 3155)
    A2_glob_b_glob()
    def A2_glob_b_loc():
        try: test(x, None, 3158)
        except NameError: test(None, None, 3159)
        [x := _ for _ in ["A2_glob_b_loc.x"]]
        try: test(x, 'A2_glob_b_loc.x', 3161)
        except NameError: test(None, 'A2_glob_b_loc.x', 3162)
        def A2_glob_b_loc_delfunc():
            nonlocal x; del x
        A2_glob_b_loc_delfunc()
        try: test(x, None, 3166)
        except NameError: test(None, None, 3167)
        x = "A2_glob_b_loc.x"
        try: test(x, 'A2_glob_b_loc.x', 3169)
        except NameError: test(None, 'A2_glob_b_loc.x', 3170)
        del x
        try: test(x, None, 3172)
        except NameError: test(None, None, 3173)
    A2_glob_b_loc()
    def A2_glob_b_ncap():
        try: test(x, None, 3176)
        except NameError: test(None, None, 3177)
        [x := _ for _ in ["A2_glob_b_ncap.x"]]
        try: test(x, 'A2_glob_b_ncap.x', 3179)
        except NameError: test(None, 'A2_glob_b_ncap.x', 3180)
        def A2_glob_b_ncap_delfunc():
            nonlocal x; del x
        A2_glob_b_ncap_delfunc()
        try: test(x, None, 3184)
        except NameError: test(None, None, 3185)
        x = "A2_glob_b_ncap.x"
        try: test(x, 'A2_glob_b_ncap.x', 3187)
        except NameError: test(None, 'A2_glob_b_ncap.x', 3188)
        del x
        try: test(x, None, 3190)
        except NameError: test(None, None, 3191)
    A2_glob_b_ncap()
    del x
    try: test(x, None, 3194)
    except NameError: test(None, None, 3195)
    def A2_glob_setfunc():
        global x; x = "x"
    A2_glob_setfunc()
    try: test(x, 'x', 3199)
    except NameError: test(None, 'x', 3200)
    def A2_glob_delfunc():
        global x; del x
    A2_glob_delfunc()
    try: test(x, None, 3204)
    except NameError: test(None, None, 3205)
    class A2_glob_B2:
        pass
    class A2_glob_B2_use:
        try: test(x, None, 3209)
        except NameError: test(None, None, 3210)
    class A2_glob_B2_anno:
        x: str
        try: test(x, None, 3213)
        except NameError: test(None, None, 3214)
    class A2_glob_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3218)
        else: error("Enclosed binding exists", 3219)
    class A2_glob_B2_glob:
        global x
        try: test(x, None, 3222)
        except NameError: test(None, None, 3223)
        def A2_glob_B2_glob_setfunc():
            global x; x = "x"
        A2_glob_B2_glob_setfunc()
        try: test(x, 'x', 3227)
        except NameError: test(None, 'x', 3228)
        def A2_glob_B2_glob_delfunc():
            global x; del x
        A2_glob_B2_glob_delfunc()
        try: test(x, None, 3232)
        except NameError: test(None, None, 3233)
        x = "x"
        try: test(x, 'x', 3235)
        except NameError: test(None, 'x', 3236)
        del x
        try: test(x, None, 3238)
        except NameError: test(None, None, 3239)
    class A2_glob_B2_loc:
        try: test(x, None, 3241)
        except NameError: test(None, None, 3242)
        def A2_glob_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_glob_B2_loc.x"
        A2_glob_B2_loc_setfunc()
        try: test(x, 'A2_glob_B2_loc.x', 3246)
        except NameError: test(None, 'A2_glob_B2_loc.x', 3247)
        def A2_glob_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_glob_B2_loc_delfunc()
        try: test(x, None, 3251)
        except NameError: test(None, None, 3252)
        x = "A2_glob_B2_loc.x"
        try: test(x, 'A2_glob_B2_loc.x', 3254)
        except NameError: test(None, 'A2_glob_B2_loc.x', 3255)
        del x
        try: test(x, None, 3257)
        except NameError: test(None, None, 3258)
    class A2_glob_B2_ncap:
        try: test(x, None, 3260)
        except NameError: test(None, None, 3261)
        def A2_glob_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_glob_B2_ncap.x"
        A2_glob_B2_ncap_setfunc()
        try: test(x, 'A2_glob_B2_ncap.x', 3265)
        except NameError: test(None, 'A2_glob_B2_ncap.x', 3266)
        def A2_glob_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_glob_B2_ncap_delfunc()
        try: test(x, None, 3270)
        except NameError: test(None, None, 3271)
        x = "A2_glob_B2_ncap.x"
        try: test(x, 'A2_glob_B2_ncap.x', 3273)
        except NameError: test(None, 'A2_glob_B2_ncap.x', 3274)
        del x
        try: test(x, None, 3276)
        except NameError: test(None, None, 3277)
    def A2_glob_b2():
        pass
    A2_glob_b2()
    def A2_glob_b2_use():
        try: test(x, None, 3282)
        except NameError: test(None, None, 3283)
    A2_glob_b2_use()
    def A2_glob_b2_anno():
        x: str
        try: test(x, None, 3287)
        except NameError: test(None, None, 3288)
    A2_glob_b2_anno()
    def A2_glob_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3293)
        else: error("Enclosed binding exists", 3294)
    A2_glob_b2_nloc()
    def A2_glob_b2_glob():
        global x
        try: test(x, None, 3298)
        except NameError: test(None, None, 3299)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3301)
        except NameError: test(None, 'x', 3302)
        def A2_glob_b2_glob_delfunc():
            global x; del x
        A2_glob_b2_glob_delfunc()
        try: test(x, None, 3306)
        except NameError: test(None, None, 3307)
        x = "x"
        try: test(x, 'x', 3309)
        except NameError: test(None, 'x', 3310)
        del x
        try: test(x, None, 3312)
        except NameError: test(None, None, 3313)
    A2_glob_b2_glob()
    def A2_glob_b2_loc():
        try: test(x, None, 3316)
        except NameError: test(None, None, 3317)
        [x := _ for _ in ["A2_glob_b2_loc.x"]]
        try: test(x, 'A2_glob_b2_loc.x', 3319)
        except NameError: test(None, 'A2_glob_b2_loc.x', 3320)
        def A2_glob_b2_loc_delfunc():
            nonlocal x; del x
        A2_glob_b2_loc_delfunc()
        try: test(x, None, 3324)
        except NameError: test(None, None, 3325)
        x = "A2_glob_b2_loc.x"
        try: test(x, 'A2_glob_b2_loc.x', 3327)
        except NameError: test(None, 'A2_glob_b2_loc.x', 3328)
        del x
        try: test(x, None, 3330)
        except NameError: test(None, None, 3331)
    A2_glob_b2_loc()
    def A2_glob_b2_ncap():
        try: test(x, None, 3334)
        except NameError: test(None, None, 3335)
        [x := _ for _ in ["A2_glob_b2_ncap.x"]]
        try: test(x, 'A2_glob_b2_ncap.x', 3337)
        except NameError: test(None, 'A2_glob_b2_ncap.x', 3338)
        def A2_glob_b2_ncap_delfunc():
            nonlocal x; del x
        A2_glob_b2_ncap_delfunc()
        try: test(x, None, 3342)
        except NameError: test(None, None, 3343)
        x = "A2_glob_b2_ncap.x"
        try: test(x, 'A2_glob_b2_ncap.x', 3345)
        except NameError: test(None, 'A2_glob_b2_ncap.x', 3346)
        del x
        try: test(x, None, 3348)
        except NameError: test(None, None, 3349)
    A2_glob_b2_ncap()
    x = "x"
    try: test(x, 'x', 3352)
    except NameError: test(None, 'x', 3353)
class A2_loc:
    try: test(x, 'x', 3355)
    except NameError: test(None, 'x', 3356)
    class A2_loc_B:
        pass
    class A2_loc_B_use:
        try: test(x, 'x', 3360)
        except NameError: test(None, 'x', 3361)
    class A2_loc_B_anno:
        x: str
        try: test(x, 'x', 3364)
        except NameError: test(None, 'x', 3365)
    class A2_loc_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3369)
        else: error("Enclosed binding exists", 3370)
    class A2_loc_B_glob:
        global x
        try: test(x, 'x', 3373)
        except NameError: test(None, 'x', 3374)
        del x
        try: test(x, None, 3376)
        except NameError: test(None, None, 3377)
        def A2_loc_B_glob_setfunc():
            global x; x = "x"
        A2_loc_B_glob_setfunc()
        try: test(x, 'x', 3381)
        except NameError: test(None, 'x', 3382)
        def A2_loc_B_glob_delfunc():
            global x; del x
        A2_loc_B_glob_delfunc()
        try: test(x, None, 3386)
        except NameError: test(None, None, 3387)
        x = "x"
        try: test(x, 'x', 3389)
        except NameError: test(None, 'x', 3390)
    class A2_loc_B_loc:
        try: test(x, 'x', 3392)
        except NameError: test(None, 'x', 3393)
        def A2_loc_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_loc_B_loc.x"
        A2_loc_B_loc_setfunc()
        try: test(x, 'A2_loc_B_loc.x', 3397)
        except NameError: test(None, 'A2_loc_B_loc.x', 3398)
        def A2_loc_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_loc_B_loc_delfunc()
        try: test(x, 'x', 3402)
        except NameError: test(None, 'x', 3403)
        x = "A2_loc_B_loc.x"
        try: test(x, 'A2_loc_B_loc.x', 3405)
        except NameError: test(None, 'A2_loc_B_loc.x', 3406)
        del x
        try: test(x, 'x', 3408)
        except NameError: test(None, 'x', 3409)
    class A2_loc_B_ncap:
        try: test(x, 'x', 3411)
        except NameError: test(None, 'x', 3412)
        def A2_loc_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_loc_B_ncap.x"
        A2_loc_B_ncap_setfunc()
        try: test(x, 'A2_loc_B_ncap.x', 3416)
        except NameError: test(None, 'A2_loc_B_ncap.x', 3417)
        def A2_loc_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_loc_B_ncap_delfunc()
        try: test(x, 'x', 3421)
        except NameError: test(None, 'x', 3422)
        x = "A2_loc_B_ncap.x"
        try: test(x, 'A2_loc_B_ncap.x', 3424)
        except NameError: test(None, 'A2_loc_B_ncap.x', 3425)
        del x
        try: test(x, 'x', 3427)
        except NameError: test(None, 'x', 3428)
    def A2_loc_b():
        pass
    A2_loc_b()
    def A2_loc_b_use():
        try: test(x, 'x', 3433)
        except NameError: test(None, 'x', 3434)
    A2_loc_b_use()
    def A2_loc_b_anno():
        x: str
        try: test(x, None, 3438)
        except NameError: test(None, None, 3439)
    A2_loc_b_anno()
    def A2_loc_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3444)
        else: error("Enclosed binding exists", 3445)
    A2_loc_b_nloc()
    def A2_loc_b_glob():
        global x
        try: test(x, 'x', 3449)
        except NameError: test(None, 'x', 3450)
        del x
        try: test(x, None, 3452)
        except NameError: test(None, None, 3453)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3455)
        except NameError: test(None, 'x', 3456)
        def A2_loc_b_glob_delfunc():
            global x; del x
        A2_loc_b_glob_delfunc()
        try: test(x, None, 3460)
        except NameError: test(None, None, 3461)
        x = "x"
        try: test(x, 'x', 3463)
        except NameError: test(None, 'x', 3464)
    A2_loc_b_glob()
    def A2_loc_b_loc():
        try: test(x, None, 3467)
        except NameError: test(None, None, 3468)
        [x := _ for _ in ["A2_loc_b_loc.x"]]
        try: test(x, 'A2_loc_b_loc.x', 3470)
        except NameError: test(None, 'A2_loc_b_loc.x', 3471)
        def A2_loc_b_loc_delfunc():
            nonlocal x; del x
        A2_loc_b_loc_delfunc()
        try: test(x, None, 3475)
        except NameError: test(None, None, 3476)
        x = "A2_loc_b_loc.x"
        try: test(x, 'A2_loc_b_loc.x', 3478)
        except NameError: test(None, 'A2_loc_b_loc.x', 3479)
        del x
        try: test(x, None, 3481)
        except NameError: test(None, None, 3482)
    A2_loc_b_loc()
    def A2_loc_b_ncap():
        try: test(x, None, 3485)
        except NameError: test(None, None, 3486)
        [x := _ for _ in ["A2_loc_b_ncap.x"]]
        try: test(x, 'A2_loc_b_ncap.x', 3488)
        except NameError: test(None, 'A2_loc_b_ncap.x', 3489)
        def A2_loc_b_ncap_delfunc():
            nonlocal x; del x
        A2_loc_b_ncap_delfunc()
        try: test(x, None, 3493)
        except NameError: test(None, None, 3494)
        x = "A2_loc_b_ncap.x"
        try: test(x, 'A2_loc_b_ncap.x', 3496)
        except NameError: test(None, 'A2_loc_b_ncap.x', 3497)
        del x
        try: test(x, None, 3499)
        except NameError: test(None, None, 3500)
    A2_loc_b_ncap()
    def A2_loc_setfunc():
        inspect.stack()[1].frame.f_locals["x"] = "A2_loc.x"
    A2_loc_setfunc()
    try: test(x, 'A2_loc.x', 3505)
    except NameError: test(None, 'A2_loc.x', 3506)
    def A2_loc_delfunc():
        del inspect.stack()[1].frame.f_locals["x"]
    A2_loc_delfunc()
    try: test(x, 'x', 3510)
    except NameError: test(None, 'x', 3511)
    x = "A2_loc.x"
    try: test(x, 'A2_loc.x', 3513)
    except NameError: test(None, 'A2_loc.x', 3514)
    class A2_loc_B2:
        pass
    class A2_loc_B2_use:
        try: test(x, 'x', 3518)
        except NameError: test(None, 'x', 3519)
    class A2_loc_B2_anno:
        x: str
        try: test(x, 'x', 3522)
        except NameError: test(None, 'x', 3523)
    class A2_loc_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3527)
        else: error("Enclosed binding exists", 3528)
    class A2_loc_B2_glob:
        global x
        try: test(x, 'x', 3531)
        except NameError: test(None, 'x', 3532)
        del x
        try: test(x, None, 3534)
        except NameError: test(None, None, 3535)
        def A2_loc_B2_glob_setfunc():
            global x; x = "x"
        A2_loc_B2_glob_setfunc()
        try: test(x, 'x', 3539)
        except NameError: test(None, 'x', 3540)
        def A2_loc_B2_glob_delfunc():
            global x; del x
        A2_loc_B2_glob_delfunc()
        try: test(x, None, 3544)
        except NameError: test(None, None, 3545)
        x = "x"
        try: test(x, 'x', 3547)
        except NameError: test(None, 'x', 3548)
    class A2_loc_B2_loc:
        try: test(x, 'x', 3550)
        except NameError: test(None, 'x', 3551)
        def A2_loc_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_loc_B2_loc.x"
        A2_loc_B2_loc_setfunc()
        try: test(x, 'A2_loc_B2_loc.x', 3555)
        except NameError: test(None, 'A2_loc_B2_loc.x', 3556)
        def A2_loc_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_loc_B2_loc_delfunc()
        try: test(x, 'x', 3560)
        except NameError: test(None, 'x', 3561)
        x = "A2_loc_B2_loc.x"
        try: test(x, 'A2_loc_B2_loc.x', 3563)
        except NameError: test(None, 'A2_loc_B2_loc.x', 3564)
        del x
        try: test(x, 'x', 3566)
        except NameError: test(None, 'x', 3567)
    class A2_loc_B2_ncap:
        try: test(x, 'x', 3569)
        except NameError: test(None, 'x', 3570)
        def A2_loc_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_loc_B2_ncap.x"
        A2_loc_B2_ncap_setfunc()
        try: test(x, 'A2_loc_B2_ncap.x', 3574)
        except NameError: test(None, 'A2_loc_B2_ncap.x', 3575)
        def A2_loc_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_loc_B2_ncap_delfunc()
        try: test(x, 'x', 3579)
        except NameError: test(None, 'x', 3580)
        x = "A2_loc_B2_ncap.x"
        try: test(x, 'A2_loc_B2_ncap.x', 3582)
        except NameError: test(None, 'A2_loc_B2_ncap.x', 3583)
        del x
        try: test(x, 'x', 3585)
        except NameError: test(None, 'x', 3586)
    def A2_loc_b2():
        pass
    A2_loc_b2()
    def A2_loc_b2_use():
        try: test(x, 'x', 3591)
        except NameError: test(None, 'x', 3592)
    A2_loc_b2_use()
    def A2_loc_b2_anno():
        x: str
        try: test(x, None, 3596)
        except NameError: test(None, None, 3597)
    A2_loc_b2_anno()
    def A2_loc_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3602)
        else: error("Enclosed binding exists", 3603)
    A2_loc_b2_nloc()
    def A2_loc_b2_glob():
        global x
        try: test(x, 'x', 3607)
        except NameError: test(None, 'x', 3608)
        del x
        try: test(x, None, 3610)
        except NameError: test(None, None, 3611)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3613)
        except NameError: test(None, 'x', 3614)
        def A2_loc_b2_glob_delfunc():
            global x; del x
        A2_loc_b2_glob_delfunc()
        try: test(x, None, 3618)
        except NameError: test(None, None, 3619)
        x = "x"
        try: test(x, 'x', 3621)
        except NameError: test(None, 'x', 3622)
    A2_loc_b2_glob()
    def A2_loc_b2_loc():
        try: test(x, None, 3625)
        except NameError: test(None, None, 3626)
        [x := _ for _ in ["A2_loc_b2_loc.x"]]
        try: test(x, 'A2_loc_b2_loc.x', 3628)
        except NameError: test(None, 'A2_loc_b2_loc.x', 3629)
        def A2_loc_b2_loc_delfunc():
            nonlocal x; del x
        A2_loc_b2_loc_delfunc()
        try: test(x, None, 3633)
        except NameError: test(None, None, 3634)
        x = "A2_loc_b2_loc.x"
        try: test(x, 'A2_loc_b2_loc.x', 3636)
        except NameError: test(None, 'A2_loc_b2_loc.x', 3637)
        del x
        try: test(x, None, 3639)
        except NameError: test(None, None, 3640)
    A2_loc_b2_loc()
    def A2_loc_b2_ncap():
        try: test(x, None, 3643)
        except NameError: test(None, None, 3644)
        [x := _ for _ in ["A2_loc_b2_ncap.x"]]
        try: test(x, 'A2_loc_b2_ncap.x', 3646)
        except NameError: test(None, 'A2_loc_b2_ncap.x', 3647)
        def A2_loc_b2_ncap_delfunc():
            nonlocal x; del x
        A2_loc_b2_ncap_delfunc()
        try: test(x, None, 3651)
        except NameError: test(None, None, 3652)
        x = "A2_loc_b2_ncap.x"
        try: test(x, 'A2_loc_b2_ncap.x', 3654)
        except NameError: test(None, 'A2_loc_b2_ncap.x', 3655)
        del x
        try: test(x, None, 3657)
        except NameError: test(None, None, 3658)
    A2_loc_b2_ncap()
    del x
    try: test(x, 'x', 3661)
    except NameError: test(None, 'x', 3662)
class A2_ncap:
    try: test(x, 'x', 3664)
    except NameError: test(None, 'x', 3665)
    class A2_ncap_B:
        pass
    class A2_ncap_B_glob:
        global x
        try: test(x, 'x', 3670)
        except NameError: test(None, 'x', 3671)
        del x
        try: test(x, None, 3673)
        except NameError: test(None, None, 3674)
        def A2_ncap_B_glob_setfunc():
            global x; x = "x"
        A2_ncap_B_glob_setfunc()
        try: test(x, 'x', 3678)
        except NameError: test(None, 'x', 3679)
        def A2_ncap_B_glob_delfunc():
            global x; del x
        A2_ncap_B_glob_delfunc()
        try: test(x, None, 3683)
        except NameError: test(None, None, 3684)
        x = "x"
        try: test(x, 'x', 3686)
        except NameError: test(None, 'x', 3687)
    class A2_ncap_B_loc:
        try: test(x, 'x', 3689)
        except NameError: test(None, 'x', 3690)
        def A2_ncap_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_ncap_B_loc.x"
        A2_ncap_B_loc_setfunc()
        try: test(x, 'A2_ncap_B_loc.x', 3694)
        except NameError: test(None, 'A2_ncap_B_loc.x', 3695)
        def A2_ncap_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_ncap_B_loc_delfunc()
        try: test(x, 'x', 3699)
        except NameError: test(None, 'x', 3700)
        x = "A2_ncap_B_loc.x"
        try: test(x, 'A2_ncap_B_loc.x', 3702)
        except NameError: test(None, 'A2_ncap_B_loc.x', 3703)
        del x
        try: test(x, 'x', 3705)
        except NameError: test(None, 'x', 3706)
    def A2_ncap_b():
        pass
    A2_ncap_b()
    def A2_ncap_b_glob():
        global x
        try: test(x, 'x', 3712)
        except NameError: test(None, 'x', 3713)
        del x
        try: test(x, None, 3715)
        except NameError: test(None, None, 3716)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3718)
        except NameError: test(None, 'x', 3719)
        def A2_ncap_b_glob_delfunc():
            global x; del x
        A2_ncap_b_glob_delfunc()
        try: test(x, None, 3723)
        except NameError: test(None, None, 3724)
        x = "x"
        try: test(x, 'x', 3726)
        except NameError: test(None, 'x', 3727)
    A2_ncap_b_glob()
    def A2_ncap_b_loc():
        try: test(x, None, 3730)
        except NameError: test(None, None, 3731)
        [x := _ for _ in ["A2_ncap_b_loc.x"]]
        try: test(x, 'A2_ncap_b_loc.x', 3733)
        except NameError: test(None, 'A2_ncap_b_loc.x', 3734)
        def A2_ncap_b_loc_delfunc():
            nonlocal x; del x
        A2_ncap_b_loc_delfunc()
        try: test(x, None, 3738)
        except NameError: test(None, None, 3739)
        x = "A2_ncap_b_loc.x"
        try: test(x, 'A2_ncap_b_loc.x', 3741)
        except NameError: test(None, 'A2_ncap_b_loc.x', 3742)
        del x
        try: test(x, None, 3744)
        except NameError: test(None, None, 3745)
    A2_ncap_b_loc()
    def A2_ncap_setfunc():
        inspect.stack()[1].frame.f_locals["x"] = "A2_ncap.x"
    A2_ncap_setfunc()
    try: test(x, 'A2_ncap.x', 3750)
    except NameError: test(None, 'A2_ncap.x', 3751)
    def A2_ncap_delfunc():
        del inspect.stack()[1].frame.f_locals["x"]
    A2_ncap_delfunc()
    try: test(x, 'x', 3755)
    except NameError: test(None, 'x', 3756)
    x = "A2_ncap.x"
    try: test(x, 'A2_ncap.x', 3758)
    except NameError: test(None, 'A2_ncap.x', 3759)
    class A2_ncap_B2:
        pass
    class A2_ncap_B2_glob:
        global x
        try: test(x, 'x', 3764)
        except NameError: test(None, 'x', 3765)
        del x
        try: test(x, None, 3767)
        except NameError: test(None, None, 3768)
        def A2_ncap_B2_glob_setfunc():
            global x; x = "x"
        A2_ncap_B2_glob_setfunc()
        try: test(x, 'x', 3772)
        except NameError: test(None, 'x', 3773)
        def A2_ncap_B2_glob_delfunc():
            global x; del x
        A2_ncap_B2_glob_delfunc()
        try: test(x, None, 3777)
        except NameError: test(None, None, 3778)
        x = "x"
        try: test(x, 'x', 3780)
        except NameError: test(None, 'x', 3781)
    class A2_ncap_B2_loc:
        try: test(x, 'x', 3783)
        except NameError: test(None, 'x', 3784)
        def A2_ncap_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_ncap_B2_loc.x"
        A2_ncap_B2_loc_setfunc()
        try: test(x, 'A2_ncap_B2_loc.x', 3788)
        except NameError: test(None, 'A2_ncap_B2_loc.x', 3789)
        def A2_ncap_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_ncap_B2_loc_delfunc()
        try: test(x, 'x', 3793)
        except NameError: test(None, 'x', 3794)
        x = "A2_ncap_B2_loc.x"
        try: test(x, 'A2_ncap_B2_loc.x', 3796)
        except NameError: test(None, 'A2_ncap_B2_loc.x', 3797)
        del x
        try: test(x, 'x', 3799)
        except NameError: test(None, 'x', 3800)
    def A2_ncap_b2():
        pass
    A2_ncap_b2()
    def A2_ncap_b2_glob():
        global x
        try: test(x, 'x', 3806)
        except NameError: test(None, 'x', 3807)
        del x
        try: test(x, None, 3809)
        except NameError: test(None, None, 3810)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3812)
        except NameError: test(None, 'x', 3813)
        def A2_ncap_b2_glob_delfunc():
            global x; del x
        A2_ncap_b2_glob_delfunc()
        try: test(x, None, 3817)
        except NameError: test(None, None, 3818)
        x = "x"
        try: test(x, 'x', 3820)
        except NameError: test(None, 'x', 3821)
    A2_ncap_b2_glob()
    def A2_ncap_b2_loc():
        try: test(x, None, 3824)
        except NameError: test(None, None, 3825)
        [x := _ for _ in ["A2_ncap_b2_loc.x"]]
        try: test(x, 'A2_ncap_b2_loc.x', 3827)
        except NameError: test(None, 'A2_ncap_b2_loc.x', 3828)
        def A2_ncap_b2_loc_delfunc():
            nonlocal x; del x
        A2_ncap_b2_loc_delfunc()
        try: test(x, None, 3832)
        except NameError: test(None, None, 3833)
        x = "A2_ncap_b2_loc.x"
        try: test(x, 'A2_ncap_b2_loc.x', 3835)
        except NameError: test(None, 'A2_ncap_b2_loc.x', 3836)
        del x
        try: test(x, None, 3838)
        except NameError: test(None, None, 3839)
    A2_ncap_b2_loc()
    del x
    try: test(x, 'x', 3842)
    except NameError: test(None, 'x', 3843)
def a2():
    class a2_B:
        pass
    class a2_B_use:
        try: test(x, 'x', 3848)
        except NameError: test(None, 'x', 3849)
    class a2_B_anno:
        x: str
        try: test(x, 'x', 3852)
        except NameError: test(None, 'x', 3853)
    class a2_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3857)
        else: error("Enclosed binding exists", 3858)
    class a2_B_glob:
        global x
        try: test(x, 'x', 3861)
        except NameError: test(None, 'x', 3862)
        del x
        try: test(x, None, 3864)
        except NameError: test(None, None, 3865)
        def a2_B_glob_setfunc():
            global x; x = "x"
        a2_B_glob_setfunc()
        try: test(x, 'x', 3869)
        except NameError: test(None, 'x', 3870)
        def a2_B_glob_delfunc():
            global x; del x
        a2_B_glob_delfunc()
        try: test(x, None, 3874)
        except NameError: test(None, None, 3875)
        x = "x"
        try: test(x, 'x', 3877)
        except NameError: test(None, 'x', 3878)
    class a2_B_loc:
        try: test(x, 'x', 3880)
        except NameError: test(None, 'x', 3881)
        def a2_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_B_loc.x"
        a2_B_loc_setfunc()
        try: test(x, 'a2_B_loc.x', 3885)
        except NameError: test(None, 'a2_B_loc.x', 3886)
        def a2_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_B_loc_delfunc()
        try: test(x, 'x', 3890)
        except NameError: test(None, 'x', 3891)
        x = "a2_B_loc.x"
        try: test(x, 'a2_B_loc.x', 3893)
        except NameError: test(None, 'a2_B_loc.x', 3894)
        del x
        try: test(x, 'x', 3896)
        except NameError: test(None, 'x', 3897)
    class a2_B_ncap:
        try: test(x, 'x', 3899)
        except NameError: test(None, 'x', 3900)
        def a2_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_B_ncap.x"
        a2_B_ncap_setfunc()
        try: test(x, 'a2_B_ncap.x', 3904)
        except NameError: test(None, 'a2_B_ncap.x', 3905)
        def a2_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_B_ncap_delfunc()
        try: test(x, 'x', 3909)
        except NameError: test(None, 'x', 3910)
        x = "a2_B_ncap.x"
        try: test(x, 'a2_B_ncap.x', 3912)
        except NameError: test(None, 'a2_B_ncap.x', 3913)
        del x
        try: test(x, 'x', 3915)
        except NameError: test(None, 'x', 3916)
    def a2_b():
        pass
    a2_b()
    def a2_b_use():
        try: test(x, 'x', 3921)
        except NameError: test(None, 'x', 3922)
    a2_b_use()
    def a2_b_anno():
        x: str
        try: test(x, None, 3926)
        except NameError: test(None, None, 3927)
    a2_b_anno()
    def a2_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3932)
        else: error("Enclosed binding exists", 3933)
    a2_b_nloc()
    def a2_b_glob():
        global x
        try: test(x, 'x', 3937)
        except NameError: test(None, 'x', 3938)
        del x
        try: test(x, None, 3940)
        except NameError: test(None, None, 3941)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3943)
        except NameError: test(None, 'x', 3944)
        def a2_b_glob_delfunc():
            global x; del x
        a2_b_glob_delfunc()
        try: test(x, None, 3948)
        except NameError: test(None, None, 3949)
        x = "x"
        try: test(x, 'x', 3951)
        except NameError: test(None, 'x', 3952)
    a2_b_glob()
    def a2_b_loc():
        try: test(x, None, 3955)
        except NameError: test(None, None, 3956)
        [x := _ for _ in ["a2_b_loc.x"]]
        try: test(x, 'a2_b_loc.x', 3958)
        except NameError: test(None, 'a2_b_loc.x', 3959)
        def a2_b_loc_delfunc():
            nonlocal x; del x
        a2_b_loc_delfunc()
        try: test(x, None, 3963)
        except NameError: test(None, None, 3964)
        x = "a2_b_loc.x"
        try: test(x, 'a2_b_loc.x', 3966)
        except NameError: test(None, 'a2_b_loc.x', 3967)
        del x
        try: test(x, None, 3969)
        except NameError: test(None, None, 3970)
    a2_b_loc()
    def a2_b_ncap():
        try: test(x, None, 3973)
        except NameError: test(None, None, 3974)
        [x := _ for _ in ["a2_b_ncap.x"]]
        try: test(x, 'a2_b_ncap.x', 3976)
        except NameError: test(None, 'a2_b_ncap.x', 3977)
        def a2_b_ncap_delfunc():
            nonlocal x; del x
        a2_b_ncap_delfunc()
        try: test(x, None, 3981)
        except NameError: test(None, None, 3982)
        x = "a2_b_ncap.x"
        try: test(x, 'a2_b_ncap.x', 3984)
        except NameError: test(None, 'a2_b_ncap.x', 3985)
        del x
        try: test(x, None, 3987)
        except NameError: test(None, None, 3988)
    a2_b_ncap()
a2()
def a2_use():
    try: test(x, 'x', 3992)
    except NameError: test(None, 'x', 3993)
    class a2_use_B:
        pass
    class a2_use_B_use:
        try: test(x, 'x', 3997)
        except NameError: test(None, 'x', 3998)
    class a2_use_B_anno:
        x: str
        try: test(x, 'x', 4001)
        except NameError: test(None, 'x', 4002)
    class a2_use_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4006)
        else: error("Enclosed binding exists", 4007)
    class a2_use_B_glob:
        global x
        try: test(x, 'x', 4010)
        except NameError: test(None, 'x', 4011)
        del x
        try: test(x, None, 4013)
        except NameError: test(None, None, 4014)
        def a2_use_B_glob_setfunc():
            global x; x = "x"
        a2_use_B_glob_setfunc()
        try: test(x, 'x', 4018)
        except NameError: test(None, 'x', 4019)
        def a2_use_B_glob_delfunc():
            global x; del x
        a2_use_B_glob_delfunc()
        try: test(x, None, 4023)
        except NameError: test(None, None, 4024)
        x = "x"
        try: test(x, 'x', 4026)
        except NameError: test(None, 'x', 4027)
    class a2_use_B_loc:
        try: test(x, 'x', 4029)
        except NameError: test(None, 'x', 4030)
        def a2_use_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_use_B_loc.x"
        a2_use_B_loc_setfunc()
        try: test(x, 'a2_use_B_loc.x', 4034)
        except NameError: test(None, 'a2_use_B_loc.x', 4035)
        def a2_use_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_use_B_loc_delfunc()
        try: test(x, 'x', 4039)
        except NameError: test(None, 'x', 4040)
        x = "a2_use_B_loc.x"
        try: test(x, 'a2_use_B_loc.x', 4042)
        except NameError: test(None, 'a2_use_B_loc.x', 4043)
        del x
        try: test(x, 'x', 4045)
        except NameError: test(None, 'x', 4046)
    class a2_use_B_ncap:
        try: test(x, 'x', 4048)
        except NameError: test(None, 'x', 4049)
        def a2_use_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_use_B_ncap.x"
        a2_use_B_ncap_setfunc()
        try: test(x, 'a2_use_B_ncap.x', 4053)
        except NameError: test(None, 'a2_use_B_ncap.x', 4054)
        def a2_use_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_use_B_ncap_delfunc()
        try: test(x, 'x', 4058)
        except NameError: test(None, 'x', 4059)
        x = "a2_use_B_ncap.x"
        try: test(x, 'a2_use_B_ncap.x', 4061)
        except NameError: test(None, 'a2_use_B_ncap.x', 4062)
        del x
        try: test(x, 'x', 4064)
        except NameError: test(None, 'x', 4065)
    def a2_use_b():
        pass
    a2_use_b()
    def a2_use_b_use():
        try: test(x, 'x', 4070)
        except NameError: test(None, 'x', 4071)
    a2_use_b_use()
    def a2_use_b_anno():
        x: str
        try: test(x, None, 4075)
        except NameError: test(None, None, 4076)
    a2_use_b_anno()
    def a2_use_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4081)
        else: error("Enclosed binding exists", 4082)
    a2_use_b_nloc()
    def a2_use_b_glob():
        global x
        try: test(x, 'x', 4086)
        except NameError: test(None, 'x', 4087)
        del x
        try: test(x, None, 4089)
        except NameError: test(None, None, 4090)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4092)
        except NameError: test(None, 'x', 4093)
        def a2_use_b_glob_delfunc():
            global x; del x
        a2_use_b_glob_delfunc()
        try: test(x, None, 4097)
        except NameError: test(None, None, 4098)
        x = "x"
        try: test(x, 'x', 4100)
        except NameError: test(None, 'x', 4101)
    a2_use_b_glob()
    def a2_use_b_loc():
        try: test(x, None, 4104)
        except NameError: test(None, None, 4105)
        [x := _ for _ in ["a2_use_b_loc.x"]]
        try: test(x, 'a2_use_b_loc.x', 4107)
        except NameError: test(None, 'a2_use_b_loc.x', 4108)
        def a2_use_b_loc_delfunc():
            nonlocal x; del x
        a2_use_b_loc_delfunc()
        try: test(x, None, 4112)
        except NameError: test(None, None, 4113)
        x = "a2_use_b_loc.x"
        try: test(x, 'a2_use_b_loc.x', 4115)
        except NameError: test(None, 'a2_use_b_loc.x', 4116)
        del x
        try: test(x, None, 4118)
        except NameError: test(None, None, 4119)
    a2_use_b_loc()
    def a2_use_b_ncap():
        try: test(x, None, 4122)
        except NameError: test(None, None, 4123)
        [x := _ for _ in ["a2_use_b_ncap.x"]]
        try: test(x, 'a2_use_b_ncap.x', 4125)
        except NameError: test(None, 'a2_use_b_ncap.x', 4126)
        def a2_use_b_ncap_delfunc():
            nonlocal x; del x
        a2_use_b_ncap_delfunc()
        try: test(x, None, 4130)
        except NameError: test(None, None, 4131)
        x = "a2_use_b_ncap.x"
        try: test(x, 'a2_use_b_ncap.x', 4133)
        except NameError: test(None, 'a2_use_b_ncap.x', 4134)
        del x
        try: test(x, None, 4136)
        except NameError: test(None, None, 4137)
    a2_use_b_ncap()
a2_use()
def a2_anno():
    x: str
    try: test(x, None, 4142)
    except NameError: test(None, None, 4143)
    class a2_anno_B:
        pass
    class a2_anno_B_use:
        try: test(x, None, 4147)
        except NameError: test(None, None, 4148)
    class a2_anno_B_anno:
        x: str
        try: test(x, 'x', 4151)
        except NameError: test(None, 'x', 4152)
    class a2_anno_B_nloc:
        nonlocal x
        try: test(x, None, 4155)
        except NameError: test(None, None, 4156)
        def a2_anno_B_nloc_setfunc():
            nonlocal x; x = "a2_anno.x"
        a2_anno_B_nloc_setfunc()
        try: test(x, 'a2_anno.x', 4160)
        except NameError: test(None, 'a2_anno.x', 4161)
        def a2_anno_B_nloc_delfunc():
            nonlocal x; del x
        a2_anno_B_nloc_delfunc()
        try: test(x, None, 4165)
        except NameError: test(None, None, 4166)
        x = "a2_anno.x"
        try: test(x, 'a2_anno.x', 4168)
        except NameError: test(None, 'a2_anno.x', 4169)
        del x
        try: test(x, None, 4171)
        except NameError: test(None, None, 4172)
    class a2_anno_B_glob:
        global x
        try: test(x, 'x', 4175)
        except NameError: test(None, 'x', 4176)
        del x
        try: test(x, None, 4178)
        except NameError: test(None, None, 4179)
        def a2_anno_B_glob_setfunc():
            global x; x = "x"
        a2_anno_B_glob_setfunc()
        try: test(x, 'x', 4183)
        except NameError: test(None, 'x', 4184)
        def a2_anno_B_glob_delfunc():
            global x; del x
        a2_anno_B_glob_delfunc()
        try: test(x, None, 4188)
        except NameError: test(None, None, 4189)
        x = "x"
        try: test(x, 'x', 4191)
        except NameError: test(None, 'x', 4192)
    class a2_anno_B_loc:
        try: test(x, 'x', 4194)
        except NameError: test(None, 'x', 4195)
        def a2_anno_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_anno_B_loc.x"
        a2_anno_B_loc_setfunc()
        try: test(x, 'a2_anno_B_loc.x', 4199)
        except NameError: test(None, 'a2_anno_B_loc.x', 4200)
        def a2_anno_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_anno_B_loc_delfunc()
        try: test(x, 'x', 4204)
        except NameError: test(None, 'x', 4205)
        x = "a2_anno_B_loc.x"
        try: test(x, 'a2_anno_B_loc.x', 4207)
        except NameError: test(None, 'a2_anno_B_loc.x', 4208)
        del x
        try: test(x, 'x', 4210)
        except NameError: test(None, 'x', 4211)
    class a2_anno_B_ncap:
        try: test(x, 'x', 4213)
        except NameError: test(None, 'x', 4214)
        def a2_anno_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_anno_B_ncap.x"
        a2_anno_B_ncap_setfunc()
        try: test(x, 'a2_anno_B_ncap.x', 4218)
        except NameError: test(None, 'a2_anno_B_ncap.x', 4219)
        def a2_anno_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_anno_B_ncap_delfunc()
        try: test(x, 'x', 4223)
        except NameError: test(None, 'x', 4224)
        x = "a2_anno_B_ncap.x"
        try: test(x, 'a2_anno_B_ncap.x', 4226)
        except NameError: test(None, 'a2_anno_B_ncap.x', 4227)
        del x
        try: test(x, 'x', 4229)
        except NameError: test(None, 'x', 4230)
    def a2_anno_b():
        pass
    a2_anno_b()
    def a2_anno_b_use():
        try: test(x, None, 4235)
        except NameError: test(None, None, 4236)
    a2_anno_b_use()
    def a2_anno_b_anno():
        x: str
        try: test(x, None, 4240)
        except NameError: test(None, None, 4241)
    a2_anno_b_anno()
    def a2_anno_b_nloc():
        nonlocal x
        try: test(x, None, 4245)
        except NameError: test(None, None, 4246)
        [x := _ for _ in ["a2_anno.x"]]
        try: test(x, 'a2_anno.x', 4248)
        except NameError: test(None, 'a2_anno.x', 4249)
        def a2_anno_b_nloc_delfunc():
            nonlocal x; del x
        a2_anno_b_nloc_delfunc()
        try: test(x, None, 4253)
        except NameError: test(None, None, 4254)
        x = "a2_anno.x"
        try: test(x, 'a2_anno.x', 4256)
        except NameError: test(None, 'a2_anno.x', 4257)
        del x
        try: test(x, None, 4259)
        except NameError: test(None, None, 4260)
    a2_anno_b_nloc()
    def a2_anno_b_glob():
        global x
        try: test(x, 'x', 4264)
        except NameError: test(None, 'x', 4265)
        del x
        try: test(x, None, 4267)
        except NameError: test(None, None, 4268)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4270)
        except NameError: test(None, 'x', 4271)
        def a2_anno_b_glob_delfunc():
            global x; del x
        a2_anno_b_glob_delfunc()
        try: test(x, None, 4275)
        except NameError: test(None, None, 4276)
        x = "x"
        try: test(x, 'x', 4278)
        except NameError: test(None, 'x', 4279)
    a2_anno_b_glob()
    def a2_anno_b_loc():
        try: test(x, None, 4282)
        except NameError: test(None, None, 4283)
        [x := _ for _ in ["a2_anno_b_loc.x"]]
        try: test(x, 'a2_anno_b_loc.x', 4285)
        except NameError: test(None, 'a2_anno_b_loc.x', 4286)
        def a2_anno_b_loc_delfunc():
            nonlocal x; del x
        a2_anno_b_loc_delfunc()
        try: test(x, None, 4290)
        except NameError: test(None, None, 4291)
        x = "a2_anno_b_loc.x"
        try: test(x, 'a2_anno_b_loc.x', 4293)
        except NameError: test(None, 'a2_anno_b_loc.x', 4294)
        del x
        try: test(x, None, 4296)
        except NameError: test(None, None, 4297)
    a2_anno_b_loc()
    def a2_anno_b_ncap():
        try: test(x, None, 4300)
        except NameError: test(None, None, 4301)
        [x := _ for _ in ["a2_anno_b_ncap.x"]]
        try: test(x, 'a2_anno_b_ncap.x', 4303)
        except NameError: test(None, 'a2_anno_b_ncap.x', 4304)
        def a2_anno_b_ncap_delfunc():
            nonlocal x; del x
        a2_anno_b_ncap_delfunc()
        try: test(x, None, 4308)
        except NameError: test(None, None, 4309)
        x = "a2_anno_b_ncap.x"
        try: test(x, 'a2_anno_b_ncap.x', 4311)
        except NameError: test(None, 'a2_anno_b_ncap.x', 4312)
        del x
        try: test(x, None, 4314)
        except NameError: test(None, None, 4315)
    a2_anno_b_ncap()
a2_anno()
def a2_nloc():
    # No enclosed binding exists.
    try: compile("nonlocal x", "<string>", "exec")
    except SyntaxError: test(None, None, 4321)
    else: error("Enclosed binding exists", 4322)
a2_nloc()
def a2_glob():
    global x
    try: test(x, 'x', 4326)
    except NameError: test(None, 'x', 4327)
    class a2_glob_B:
        pass
    class a2_glob_B_use:
        try: test(x, 'x', 4331)
        except NameError: test(None, 'x', 4332)
    class a2_glob_B_anno:
        x: str
        try: test(x, 'x', 4335)
        except NameError: test(None, 'x', 4336)
    class a2_glob_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4340)
        else: error("Enclosed binding exists", 4341)
    class a2_glob_B_glob:
        global x
        try: test(x, 'x', 4344)
        except NameError: test(None, 'x', 4345)
        del x
        try: test(x, None, 4347)
        except NameError: test(None, None, 4348)
        def a2_glob_B_glob_setfunc():
            global x; x = "x"
        a2_glob_B_glob_setfunc()
        try: test(x, 'x', 4352)
        except NameError: test(None, 'x', 4353)
        def a2_glob_B_glob_delfunc():
            global x; del x
        a2_glob_B_glob_delfunc()
        try: test(x, None, 4357)
        except NameError: test(None, None, 4358)
        x = "x"
        try: test(x, 'x', 4360)
        except NameError: test(None, 'x', 4361)
    class a2_glob_B_loc:
        try: test(x, 'x', 4363)
        except NameError: test(None, 'x', 4364)
        def a2_glob_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_glob_B_loc.x"
        a2_glob_B_loc_setfunc()
        try: test(x, 'a2_glob_B_loc.x', 4368)
        except NameError: test(None, 'a2_glob_B_loc.x', 4369)
        def a2_glob_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_glob_B_loc_delfunc()
        try: test(x, 'x', 4373)
        except NameError: test(None, 'x', 4374)
        x = "a2_glob_B_loc.x"
        try: test(x, 'a2_glob_B_loc.x', 4376)
        except NameError: test(None, 'a2_glob_B_loc.x', 4377)
        del x
        try: test(x, 'x', 4379)
        except NameError: test(None, 'x', 4380)
    class a2_glob_B_ncap:
        try: test(x, 'x', 4382)
        except NameError: test(None, 'x', 4383)
        def a2_glob_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_glob_B_ncap.x"
        a2_glob_B_ncap_setfunc()
        try: test(x, 'a2_glob_B_ncap.x', 4387)
        except NameError: test(None, 'a2_glob_B_ncap.x', 4388)
        def a2_glob_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_glob_B_ncap_delfunc()
        try: test(x, 'x', 4392)
        except NameError: test(None, 'x', 4393)
        x = "a2_glob_B_ncap.x"
        try: test(x, 'a2_glob_B_ncap.x', 4395)
        except NameError: test(None, 'a2_glob_B_ncap.x', 4396)
        del x
        try: test(x, 'x', 4398)
        except NameError: test(None, 'x', 4399)
    def a2_glob_b():
        pass
    a2_glob_b()
    def a2_glob_b_use():
        try: test(x, 'x', 4404)
        except NameError: test(None, 'x', 4405)
    a2_glob_b_use()
    def a2_glob_b_anno():
        x: str
        try: test(x, None, 4409)
        except NameError: test(None, None, 4410)
    a2_glob_b_anno()
    def a2_glob_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4415)
        else: error("Enclosed binding exists", 4416)
    a2_glob_b_nloc()
    def a2_glob_b_glob():
        global x
        try: test(x, 'x', 4420)
        except NameError: test(None, 'x', 4421)
        del x
        try: test(x, None, 4423)
        except NameError: test(None, None, 4424)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4426)
        except NameError: test(None, 'x', 4427)
        def a2_glob_b_glob_delfunc():
            global x; del x
        a2_glob_b_glob_delfunc()
        try: test(x, None, 4431)
        except NameError: test(None, None, 4432)
        x = "x"
        try: test(x, 'x', 4434)
        except NameError: test(None, 'x', 4435)
    a2_glob_b_glob()
    def a2_glob_b_loc():
        try: test(x, None, 4438)
        except NameError: test(None, None, 4439)
        [x := _ for _ in ["a2_glob_b_loc.x"]]
        try: test(x, 'a2_glob_b_loc.x', 4441)
        except NameError: test(None, 'a2_glob_b_loc.x', 4442)
        def a2_glob_b_loc_delfunc():
            nonlocal x; del x
        a2_glob_b_loc_delfunc()
        try: test(x, None, 4446)
        except NameError: test(None, None, 4447)
        x = "a2_glob_b_loc.x"
        try: test(x, 'a2_glob_b_loc.x', 4449)
        except NameError: test(None, 'a2_glob_b_loc.x', 4450)
        del x
        try: test(x, None, 4452)
        except NameError: test(None, None, 4453)
    a2_glob_b_loc()
    def a2_glob_b_ncap():
        try: test(x, None, 4456)
        except NameError: test(None, None, 4457)
        [x := _ for _ in ["a2_glob_b_ncap.x"]]
        try: test(x, 'a2_glob_b_ncap.x', 4459)
        except NameError: test(None, 'a2_glob_b_ncap.x', 4460)
        def a2_glob_b_ncap_delfunc():
            nonlocal x; del x
        a2_glob_b_ncap_delfunc()
        try: test(x, None, 4464)
        except NameError: test(None, None, 4465)
        x = "a2_glob_b_ncap.x"
        try: test(x, 'a2_glob_b_ncap.x', 4467)
        except NameError: test(None, 'a2_glob_b_ncap.x', 4468)
        del x
        try: test(x, None, 4470)
        except NameError: test(None, None, 4471)
    a2_glob_b_ncap()
    del x
    try: test(x, None, 4474)
    except NameError: test(None, None, 4475)
    [x := _ for _ in ["x"]]
    try: test(x, 'x', 4477)
    except NameError: test(None, 'x', 4478)
    def a2_glob_delfunc():
        global x; del x
    a2_glob_delfunc()
    try: test(x, None, 4482)
    except NameError: test(None, None, 4483)
    class a2_glob_B2:
        pass
    class a2_glob_B2_use:
        try: test(x, None, 4487)
        except NameError: test(None, None, 4488)
    class a2_glob_B2_anno:
        x: str
        try: test(x, None, 4491)
        except NameError: test(None, None, 4492)
    class a2_glob_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4496)
        else: error("Enclosed binding exists", 4497)
    class a2_glob_B2_glob:
        global x
        try: test(x, None, 4500)
        except NameError: test(None, None, 4501)
        def a2_glob_B2_glob_setfunc():
            global x; x = "x"
        a2_glob_B2_glob_setfunc()
        try: test(x, 'x', 4505)
        except NameError: test(None, 'x', 4506)
        def a2_glob_B2_glob_delfunc():
            global x; del x
        a2_glob_B2_glob_delfunc()
        try: test(x, None, 4510)
        except NameError: test(None, None, 4511)
        x = "x"
        try: test(x, 'x', 4513)
        except NameError: test(None, 'x', 4514)
        del x
        try: test(x, None, 4516)
        except NameError: test(None, None, 4517)
    class a2_glob_B2_loc:
        try: test(x, None, 4519)
        except NameError: test(None, None, 4520)
        def a2_glob_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_glob_B2_loc.x"
        a2_glob_B2_loc_setfunc()
        try: test(x, 'a2_glob_B2_loc.x', 4524)
        except NameError: test(None, 'a2_glob_B2_loc.x', 4525)
        def a2_glob_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_glob_B2_loc_delfunc()
        try: test(x, None, 4529)
        except NameError: test(None, None, 4530)
        x = "a2_glob_B2_loc.x"
        try: test(x, 'a2_glob_B2_loc.x', 4532)
        except NameError: test(None, 'a2_glob_B2_loc.x', 4533)
        del x
        try: test(x, None, 4535)
        except NameError: test(None, None, 4536)
    class a2_glob_B2_ncap:
        try: test(x, None, 4538)
        except NameError: test(None, None, 4539)
        def a2_glob_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_glob_B2_ncap.x"
        a2_glob_B2_ncap_setfunc()
        try: test(x, 'a2_glob_B2_ncap.x', 4543)
        except NameError: test(None, 'a2_glob_B2_ncap.x', 4544)
        def a2_glob_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_glob_B2_ncap_delfunc()
        try: test(x, None, 4548)
        except NameError: test(None, None, 4549)
        x = "a2_glob_B2_ncap.x"
        try: test(x, 'a2_glob_B2_ncap.x', 4551)
        except NameError: test(None, 'a2_glob_B2_ncap.x', 4552)
        del x
        try: test(x, None, 4554)
        except NameError: test(None, None, 4555)
    def a2_glob_b2():
        pass
    a2_glob_b2()
    def a2_glob_b2_use():
        try: test(x, None, 4560)
        except NameError: test(None, None, 4561)
    a2_glob_b2_use()
    def a2_glob_b2_anno():
        x: str
        try: test(x, None, 4565)
        except NameError: test(None, None, 4566)
    a2_glob_b2_anno()
    def a2_glob_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4571)
        else: error("Enclosed binding exists", 4572)
    a2_glob_b2_nloc()
    def a2_glob_b2_glob():
        global x
        try: test(x, None, 4576)
        except NameError: test(None, None, 4577)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4579)
        except NameError: test(None, 'x', 4580)
        def a2_glob_b2_glob_delfunc():
            global x; del x
        a2_glob_b2_glob_delfunc()
        try: test(x, None, 4584)
        except NameError: test(None, None, 4585)
        x = "x"
        try: test(x, 'x', 4587)
        except NameError: test(None, 'x', 4588)
        del x
        try: test(x, None, 4590)
        except NameError: test(None, None, 4591)
    a2_glob_b2_glob()
    def a2_glob_b2_loc():
        try: test(x, None, 4594)
        except NameError: test(None, None, 4595)
        [x := _ for _ in ["a2_glob_b2_loc.x"]]
        try: test(x, 'a2_glob_b2_loc.x', 4597)
        except NameError: test(None, 'a2_glob_b2_loc.x', 4598)
        def a2_glob_b2_loc_delfunc():
            nonlocal x; del x
        a2_glob_b2_loc_delfunc()
        try: test(x, None, 4602)
        except NameError: test(None, None, 4603)
        x = "a2_glob_b2_loc.x"
        try: test(x, 'a2_glob_b2_loc.x', 4605)
        except NameError: test(None, 'a2_glob_b2_loc.x', 4606)
        del x
        try: test(x, None, 4608)
        except NameError: test(None, None, 4609)
    a2_glob_b2_loc()
    def a2_glob_b2_ncap():
        try: test(x, None, 4612)
        except NameError: test(None, None, 4613)
        [x := _ for _ in ["a2_glob_b2_ncap.x"]]
        try: test(x, 'a2_glob_b2_ncap.x', 4615)
        except NameError: test(None, 'a2_glob_b2_ncap.x', 4616)
        def a2_glob_b2_ncap_delfunc():
            nonlocal x; del x
        a2_glob_b2_ncap_delfunc()
        try: test(x, None, 4620)
        except NameError: test(None, None, 4621)
        x = "a2_glob_b2_ncap.x"
        try: test(x, 'a2_glob_b2_ncap.x', 4623)
        except NameError: test(None, 'a2_glob_b2_ncap.x', 4624)
        del x
        try: test(x, None, 4626)
        except NameError: test(None, None, 4627)
    a2_glob_b2_ncap()
    x = "x"
    try: test(x, 'x', 4630)
    except NameError: test(None, 'x', 4631)
a2_glob()
def a2_loc():
    try: test(x, None, 4634)
    except NameError: test(None, None, 4635)
    class a2_loc_B:
        pass
    class a2_loc_B_use:
        try: test(x, None, 4639)
        except NameError: test(None, None, 4640)
    class a2_loc_B_anno:
        x: str
        try: test(x, 'x', 4643)
        except NameError: test(None, 'x', 4644)
    class a2_loc_B_nloc:
        nonlocal x
        try: test(x, None, 4647)
        except NameError: test(None, None, 4648)
        def a2_loc_B_nloc_setfunc():
            nonlocal x; x = "a2_loc.x"
        a2_loc_B_nloc_setfunc()
        try: test(x, 'a2_loc.x', 4652)
        except NameError: test(None, 'a2_loc.x', 4653)
        def a2_loc_B_nloc_delfunc():
            nonlocal x; del x
        a2_loc_B_nloc_delfunc()
        try: test(x, None, 4657)
        except NameError: test(None, None, 4658)
        x = "a2_loc.x"
        try: test(x, 'a2_loc.x', 4660)
        except NameError: test(None, 'a2_loc.x', 4661)
        del x
        try: test(x, None, 4663)
        except NameError: test(None, None, 4664)
    class a2_loc_B_glob:
        global x
        try: test(x, 'x', 4667)
        except NameError: test(None, 'x', 4668)
        del x
        try: test(x, None, 4670)
        except NameError: test(None, None, 4671)
        def a2_loc_B_glob_setfunc():
            global x; x = "x"
        a2_loc_B_glob_setfunc()
        try: test(x, 'x', 4675)
        except NameError: test(None, 'x', 4676)
        def a2_loc_B_glob_delfunc():
            global x; del x
        a2_loc_B_glob_delfunc()
        try: test(x, None, 4680)
        except NameError: test(None, None, 4681)
        x = "x"
        try: test(x, 'x', 4683)
        except NameError: test(None, 'x', 4684)
    class a2_loc_B_loc:
        try: test(x, 'x', 4686)
        except NameError: test(None, 'x', 4687)
        def a2_loc_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_loc_B_loc.x"
        a2_loc_B_loc_setfunc()
        try: test(x, 'a2_loc_B_loc.x', 4691)
        except NameError: test(None, 'a2_loc_B_loc.x', 4692)
        def a2_loc_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_loc_B_loc_delfunc()
        try: test(x, 'x', 4696)
        except NameError: test(None, 'x', 4697)
        x = "a2_loc_B_loc.x"
        try: test(x, 'a2_loc_B_loc.x', 4699)
        except NameError: test(None, 'a2_loc_B_loc.x', 4700)
        del x
        try: test(x, 'x', 4702)
        except NameError: test(None, 'x', 4703)
    class a2_loc_B_ncap:
        try: test(x, 'x', 4705)
        except NameError: test(None, 'x', 4706)
        def a2_loc_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_loc_B_ncap.x"
        a2_loc_B_ncap_setfunc()
        try: test(x, 'a2_loc_B_ncap.x', 4710)
        except NameError: test(None, 'a2_loc_B_ncap.x', 4711)
        def a2_loc_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_loc_B_ncap_delfunc()
        try: test(x, 'x', 4715)
        except NameError: test(None, 'x', 4716)
        x = "a2_loc_B_ncap.x"
        try: test(x, 'a2_loc_B_ncap.x', 4718)
        except NameError: test(None, 'a2_loc_B_ncap.x', 4719)
        del x
        try: test(x, 'x', 4721)
        except NameError: test(None, 'x', 4722)
    def a2_loc_b():
        pass
    a2_loc_b()
    def a2_loc_b_use():
        try: test(x, None, 4727)
        except NameError: test(None, None, 4728)
    a2_loc_b_use()
    def a2_loc_b_anno():
        x: str
        try: test(x, None, 4732)
        except NameError: test(None, None, 4733)
    a2_loc_b_anno()
    def a2_loc_b_nloc():
        nonlocal x
        try: test(x, None, 4737)
        except NameError: test(None, None, 4738)
        [x := _ for _ in ["a2_loc.x"]]
        try: test(x, 'a2_loc.x', 4740)
        except NameError: test(None, 'a2_loc.x', 4741)
        def a2_loc_b_nloc_delfunc():
            nonlocal x; del x
        a2_loc_b_nloc_delfunc()
        try: test(x, None, 4745)
        except NameError: test(None, None, 4746)
        x = "a2_loc.x"
        try: test(x, 'a2_loc.x', 4748)
        except NameError: test(None, 'a2_loc.x', 4749)
        del x
        try: test(x, None, 4751)
        except NameError: test(None, None, 4752)
    a2_loc_b_nloc()
    def a2_loc_b_glob():
        global x
        try: test(x, 'x', 4756)
        except NameError: test(None, 'x', 4757)
        del x
        try: test(x, None, 4759)
        except NameError: test(None, None, 4760)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4762)
        except NameError: test(None, 'x', 4763)
        def a2_loc_b_glob_delfunc():
            global x; del x
        a2_loc_b_glob_delfunc()
        try: test(x, None, 4767)
        except NameError: test(None, None, 4768)
        x = "x"
        try: test(x, 'x', 4770)
        except NameError: test(None, 'x', 4771)
    a2_loc_b_glob()
    def a2_loc_b_loc():
        try: test(x, None, 4774)
        except NameError: test(None, None, 4775)
        [x := _ for _ in ["a2_loc_b_loc.x"]]
        try: test(x, 'a2_loc_b_loc.x', 4777)
        except NameError: test(None, 'a2_loc_b_loc.x', 4778)
        def a2_loc_b_loc_delfunc():
            nonlocal x; del x
        a2_loc_b_loc_delfunc()
        try: test(x, None, 4782)
        except NameError: test(None, None, 4783)
        x = "a2_loc_b_loc.x"
        try: test(x, 'a2_loc_b_loc.x', 4785)
        except NameError: test(None, 'a2_loc_b_loc.x', 4786)
        del x
        try: test(x, None, 4788)
        except NameError: test(None, None, 4789)
    a2_loc_b_loc()
    def a2_loc_b_ncap():
        try: test(x, None, 4792)
        except NameError: test(None, None, 4793)
        [x := _ for _ in ["a2_loc_b_ncap.x"]]
        try: test(x, 'a2_loc_b_ncap.x', 4795)
        except NameError: test(None, 'a2_loc_b_ncap.x', 4796)
        def a2_loc_b_ncap_delfunc():
            nonlocal x; del x
        a2_loc_b_ncap_delfunc()
        try: test(x, None, 4800)
        except NameError: test(None, None, 4801)
        x = "a2_loc_b_ncap.x"
        try: test(x, 'a2_loc_b_ncap.x', 4803)
        except NameError: test(None, 'a2_loc_b_ncap.x', 4804)
        del x
        try: test(x, None, 4806)
        except NameError: test(None, None, 4807)
    a2_loc_b_ncap()
    [x := _ for _ in ["a2_loc.x"]]
    try: test(x, 'a2_loc.x', 4810)
    except NameError: test(None, 'a2_loc.x', 4811)
    def a2_loc_delfunc():
        nonlocal x; del x
    a2_loc_delfunc()
    try: test(x, None, 4815)
    except NameError: test(None, None, 4816)
    x = "a2_loc.x"
    try: test(x, 'a2_loc.x', 4818)
    except NameError: test(None, 'a2_loc.x', 4819)
    class a2_loc_B2:
        pass
    class a2_loc_B2_use:
        try: test(x, 'a2_loc.x', 4823)
        except NameError: test(None, 'a2_loc.x', 4824)
    class a2_loc_B2_anno:
        x: str
        try: test(x, 'x', 4827)
        except NameError: test(None, 'x', 4828)
    class a2_loc_B2_nloc:
        nonlocal x
        try: test(x, 'a2_loc.x', 4831)
        except NameError: test(None, 'a2_loc.x', 4832)
        del x
        try: test(x, None, 4834)
        except NameError: test(None, None, 4835)
        def a2_loc_B2_nloc_setfunc():
            nonlocal x; x = "a2_loc.x"
        a2_loc_B2_nloc_setfunc()
        try: test(x, 'a2_loc.x', 4839)
        except NameError: test(None, 'a2_loc.x', 4840)
        def a2_loc_B2_nloc_delfunc():
            nonlocal x; del x
        a2_loc_B2_nloc_delfunc()
        try: test(x, None, 4844)
        except NameError: test(None, None, 4845)
        x = "a2_loc.x"
        try: test(x, 'a2_loc.x', 4847)
        except NameError: test(None, 'a2_loc.x', 4848)
    class a2_loc_B2_glob:
        global x
        try: test(x, 'x', 4851)
        except NameError: test(None, 'x', 4852)
        del x
        try: test(x, None, 4854)
        except NameError: test(None, None, 4855)
        def a2_loc_B2_glob_setfunc():
            global x; x = "x"
        a2_loc_B2_glob_setfunc()
        try: test(x, 'x', 4859)
        except NameError: test(None, 'x', 4860)
        def a2_loc_B2_glob_delfunc():
            global x; del x
        a2_loc_B2_glob_delfunc()
        try: test(x, None, 4864)
        except NameError: test(None, None, 4865)
        x = "x"
        try: test(x, 'x', 4867)
        except NameError: test(None, 'x', 4868)
    class a2_loc_B2_loc:
        try: test(x, 'x', 4870)
        except NameError: test(None, 'x', 4871)
        def a2_loc_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_loc_B2_loc.x"
        a2_loc_B2_loc_setfunc()
        try: test(x, 'a2_loc_B2_loc.x', 4875)
        except NameError: test(None, 'a2_loc_B2_loc.x', 4876)
        def a2_loc_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_loc_B2_loc_delfunc()
        try: test(x, 'x', 4880)
        except NameError: test(None, 'x', 4881)
        x = "a2_loc_B2_loc.x"
        try: test(x, 'a2_loc_B2_loc.x', 4883)
        except NameError: test(None, 'a2_loc_B2_loc.x', 4884)
        del x
        try: test(x, 'x', 4886)
        except NameError: test(None, 'x', 4887)
    class a2_loc_B2_ncap:
        try: test(x, 'x', 4889)
        except NameError: test(None, 'x', 4890)
        def a2_loc_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_loc_B2_ncap.x"
        a2_loc_B2_ncap_setfunc()
        try: test(x, 'a2_loc_B2_ncap.x', 4894)
        except NameError: test(None, 'a2_loc_B2_ncap.x', 4895)
        def a2_loc_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_loc_B2_ncap_delfunc()
        try: test(x, 'x', 4899)
        except NameError: test(None, 'x', 4900)
        x = "a2_loc_B2_ncap.x"
        try: test(x, 'a2_loc_B2_ncap.x', 4902)
        except NameError: test(None, 'a2_loc_B2_ncap.x', 4903)
        del x
        try: test(x, 'x', 4905)
        except NameError: test(None, 'x', 4906)
    def a2_loc_b2():
        pass
    a2_loc_b2()
    def a2_loc_b2_use():
        try: test(x, 'a2_loc.x', 4911)
        except NameError: test(None, 'a2_loc.x', 4912)
    a2_loc_b2_use()
    def a2_loc_b2_anno():
        x: str
        try: test(x, None, 4916)
        except NameError: test(None, None, 4917)
    a2_loc_b2_anno()
    def a2_loc_b2_nloc():
        nonlocal x
        try: test(x, 'a2_loc.x', 4921)
        except NameError: test(None, 'a2_loc.x', 4922)
        del x
        try: test(x, None, 4924)
        except NameError: test(None, None, 4925)
        [x := _ for _ in ["a2_loc.x"]]
        try: test(x, 'a2_loc.x', 4927)
        except NameError: test(None, 'a2_loc.x', 4928)
        def a2_loc_b2_nloc_delfunc():
            nonlocal x; del x
        a2_loc_b2_nloc_delfunc()
        try: test(x, None, 4932)
        except NameError: test(None, None, 4933)
        x = "a2_loc.x"
        try: test(x, 'a2_loc.x', 4935)
        except NameError: test(None, 'a2_loc.x', 4936)
    a2_loc_b2_nloc()
    def a2_loc_b2_glob():
        global x
        try: test(x, 'x', 4940)
        except NameError: test(None, 'x', 4941)
        del x
        try: test(x, None, 4943)
        except NameError: test(None, None, 4944)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4946)
        except NameError: test(None, 'x', 4947)
        def a2_loc_b2_glob_delfunc():
            global x; del x
        a2_loc_b2_glob_delfunc()
        try: test(x, None, 4951)
        except NameError: test(None, None, 4952)
        x = "x"
        try: test(x, 'x', 4954)
        except NameError: test(None, 'x', 4955)
    a2_loc_b2_glob()
    def a2_loc_b2_loc():
        try: test(x, None, 4958)
        except NameError: test(None, None, 4959)
        [x := _ for _ in ["a2_loc_b2_loc.x"]]
        try: test(x, 'a2_loc_b2_loc.x', 4961)
        except NameError: test(None, 'a2_loc_b2_loc.x', 4962)
        def a2_loc_b2_loc_delfunc():
            nonlocal x; del x
        a2_loc_b2_loc_delfunc()
        try: test(x, None, 4966)
        except NameError: test(None, None, 4967)
        x = "a2_loc_b2_loc.x"
        try: test(x, 'a2_loc_b2_loc.x', 4969)
        except NameError: test(None, 'a2_loc_b2_loc.x', 4970)
        del x
        try: test(x, None, 4972)
        except NameError: test(None, None, 4973)
    a2_loc_b2_loc()
    def a2_loc_b2_ncap():
        try: test(x, None, 4976)
        except NameError: test(None, None, 4977)
        [x := _ for _ in ["a2_loc_b2_ncap.x"]]
        try: test(x, 'a2_loc_b2_ncap.x', 4979)
        except NameError: test(None, 'a2_loc_b2_ncap.x', 4980)
        def a2_loc_b2_ncap_delfunc():
            nonlocal x; del x
        a2_loc_b2_ncap_delfunc()
        try: test(x, None, 4984)
        except NameError: test(None, None, 4985)
        x = "a2_loc_b2_ncap.x"
        try: test(x, 'a2_loc_b2_ncap.x', 4987)
        except NameError: test(None, 'a2_loc_b2_ncap.x', 4988)
        del x
        try: test(x, None, 4990)
        except NameError: test(None, None, 4991)
    a2_loc_b2_ncap()
    del x
    try: test(x, None, 4994)
    except NameError: test(None, None, 4995)
a2_loc()
def a2_ncap():
    try: test(x, None, 4998)
    except NameError: test(None, None, 4999)
    class a2_ncap_B:
        pass
    class a2_ncap_B_glob:
        global x
        try: test(x, 'x', 5004)
        except NameError: test(None, 'x', 5005)
        del x
        try: test(x, None, 5007)
        except NameError: test(None, None, 5008)
        def a2_ncap_B_glob_setfunc():
            global x; x = "x"
        a2_ncap_B_glob_setfunc()
        try: test(x, 'x', 5012)
        except NameError: test(None, 'x', 5013)
        def a2_ncap_B_glob_delfunc():
            global x; del x
        a2_ncap_B_glob_delfunc()
        try: test(x, None, 5017)
        except NameError: test(None, None, 5018)
        x = "x"
        try: test(x, 'x', 5020)
        except NameError: test(None, 'x', 5021)
    class a2_ncap_B_loc:
        try: test(x, 'x', 5023)
        except NameError: test(None, 'x', 5024)
        def a2_ncap_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_ncap_B_loc.x"
        a2_ncap_B_loc_setfunc()
        try: test(x, 'a2_ncap_B_loc.x', 5028)
        except NameError: test(None, 'a2_ncap_B_loc.x', 5029)
        def a2_ncap_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_ncap_B_loc_delfunc()
        try: test(x, 'x', 5033)
        except NameError: test(None, 'x', 5034)
        x = "a2_ncap_B_loc.x"
        try: test(x, 'a2_ncap_B_loc.x', 5036)
        except NameError: test(None, 'a2_ncap_B_loc.x', 5037)
        del x
        try: test(x, 'x', 5039)
        except NameError: test(None, 'x', 5040)
    def a2_ncap_b():
        pass
    a2_ncap_b()
    def a2_ncap_b_glob():
        global x
        try: test(x, 'x', 5046)
        except NameError: test(None, 'x', 5047)
        del x
        try: test(x, None, 5049)
        except NameError: test(None, None, 5050)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 5052)
        except NameError: test(None, 'x', 5053)
        def a2_ncap_b_glob_delfunc():
            global x; del x
        a2_ncap_b_glob_delfunc()
        try: test(x, None, 5057)
        except NameError: test(None, None, 5058)
        x = "x"
        try: test(x, 'x', 5060)
        except NameError: test(None, 'x', 5061)
    a2_ncap_b_glob()
    def a2_ncap_b_loc():
        try: test(x, None, 5064)
        except NameError: test(None, None, 5065)
        [x := _ for _ in ["a2_ncap_b_loc.x"]]
        try: test(x, 'a2_ncap_b_loc.x', 5067)
        except NameError: test(None, 'a2_ncap_b_loc.x', 5068)
        def a2_ncap_b_loc_delfunc():
            nonlocal x; del x
        a2_ncap_b_loc_delfunc()
        try: test(x, None, 5072)
        except NameError: test(None, None, 5073)
        x = "a2_ncap_b_loc.x"
        try: test(x, 'a2_ncap_b_loc.x', 5075)
        except NameError: test(None, 'a2_ncap_b_loc.x', 5076)
        del x
        try: test(x, None, 5078)
        except NameError: test(None, None, 5079)
    a2_ncap_b_loc()
    [x := _ for _ in ["a2_ncap.x"]]
    try: test(x, 'a2_ncap.x', 5082)
    except NameError: test(None, 'a2_ncap.x', 5083)
    def a2_ncap_delfunc():
        nonlocal x; del x
    a2_ncap_delfunc()
    try: test(x, None, 5087)
    except NameError: test(None, None, 5088)
    x = "a2_ncap.x"
    try: test(x, 'a2_ncap.x', 5090)
    except NameError: test(None, 'a2_ncap.x', 5091)
    class a2_ncap_B2:
        pass
    class a2_ncap_B2_glob:
        global x
        try: test(x, 'x', 5096)
        except NameError: test(None, 'x', 5097)
        del x
        try: test(x, None, 5099)
        except NameError: test(None, None, 5100)
        def a2_ncap_B2_glob_setfunc():
            global x; x = "x"
        a2_ncap_B2_glob_setfunc()
        try: test(x, 'x', 5104)
        except NameError: test(None, 'x', 5105)
        def a2_ncap_B2_glob_delfunc():
            global x; del x
        a2_ncap_B2_glob_delfunc()
        try: test(x, None, 5109)
        except NameError: test(None, None, 5110)
        x = "x"
        try: test(x, 'x', 5112)
        except NameError: test(None, 'x', 5113)
    class a2_ncap_B2_loc:
        try: test(x, 'x', 5115)
        except NameError: test(None, 'x', 5116)
        def a2_ncap_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_ncap_B2_loc.x"
        a2_ncap_B2_loc_setfunc()
        try: test(x, 'a2_ncap_B2_loc.x', 5120)
        except NameError: test(None, 'a2_ncap_B2_loc.x', 5121)
        def a2_ncap_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_ncap_B2_loc_delfunc()
        try: test(x, 'x', 5125)
        except NameError: test(None, 'x', 5126)
        x = "a2_ncap_B2_loc.x"
        try: test(x, 'a2_ncap_B2_loc.x', 5128)
        except NameError: test(None, 'a2_ncap_B2_loc.x', 5129)
        del x
        try: test(x, 'x', 5131)
        except NameError: test(None, 'x', 5132)
    def a2_ncap_b2():
        pass
    a2_ncap_b2()
    def a2_ncap_b2_glob():
        global x
        try: test(x, 'x', 5138)
        except NameError: test(None, 'x', 5139)
        del x
        try: test(x, None, 5141)
        except NameError: test(None, None, 5142)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 5144)
        except NameError: test(None, 'x', 5145)
        def a2_ncap_b2_glob_delfunc():
            global x; del x
        a2_ncap_b2_glob_delfunc()
        try: test(x, None, 5149)
        except NameError: test(None, None, 5150)
        x = "x"
        try: test(x, 'x', 5152)
        except NameError: test(None, 'x', 5153)
    a2_ncap_b2_glob()
    def a2_ncap_b2_loc():
        try: test(x, None, 5156)
        except NameError: test(None, None, 5157)
        [x := _ for _ in ["a2_ncap_b2_loc.x"]]
        try: test(x, 'a2_ncap_b2_loc.x', 5159)
        except NameError: test(None, 'a2_ncap_b2_loc.x', 5160)
        def a2_ncap_b2_loc_delfunc():
            nonlocal x; del x
        a2_ncap_b2_loc_delfunc()
        try: test(x, None, 5164)
        except NameError: test(None, None, 5165)
        x = "a2_ncap_b2_loc.x"
        try: test(x, 'a2_ncap_b2_loc.x', 5167)
        except NameError: test(None, 'a2_ncap_b2_loc.x', 5168)
        del x
        try: test(x, None, 5170)
        except NameError: test(None, None, 5171)
    a2_ncap_b2_loc()
    del x
    try: test(x, None, 5174)
    except NameError: test(None, None, 5175)
a2_ncap()
del x
try: test(x, None, 5178)
except NameError: test(None, None, 5179)
