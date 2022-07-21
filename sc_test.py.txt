
try: test(x, None, 17)
except NameError: test(None, None, 18)
class A:
    class A_B:
        pass
    class A_B_use:
        try: test(x, None, 23)
        except NameError: test(None, None, 24)
    class A_B_anno:
        x: str
        try: test(x, None, 27)
        except NameError: test(None, None, 28)
    class A_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 32)
        else: error("Enclosed binding exists", 33)
    class A_B_glob:
        global x
        try: test(x, None, 36)
        except NameError: test(None, None, 37)
        def A_B_glob_setfunc():
            global x; x = "x"
        A_B_glob_setfunc()
        try: test(x, 'x', 41)
        except NameError: test(None, 'x', 42)
        def A_B_glob_delfunc():
            global x; del x
        A_B_glob_delfunc()
        try: test(x, None, 46)
        except NameError: test(None, None, 47)
        x = "x"
        try: test(x, 'x', 49)
        except NameError: test(None, 'x', 50)
        del x
        try: test(x, None, 52)
        except NameError: test(None, None, 53)
    class A_B_loc:
        try: test(x, None, 55)
        except NameError: test(None, None, 56)
        def A_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_B_loc.x"
        A_B_loc_setfunc()
        try: test(x, 'A_B_loc.x', 60)
        except NameError: test(None, 'A_B_loc.x', 61)
        def A_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_B_loc_delfunc()
        try: test(x, None, 65)
        except NameError: test(None, None, 66)
        x = "A_B_loc.x"
        try: test(x, 'A_B_loc.x', 68)
        except NameError: test(None, 'A_B_loc.x', 69)
        del x
        try: test(x, None, 71)
        except NameError: test(None, None, 72)
    class A_B_ncap:
        try: test(x, None, 74)
        except NameError: test(None, None, 75)
        def A_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_B_ncap.x"
        A_B_ncap_setfunc()
        try: test(x, 'A_B_ncap.x', 79)
        except NameError: test(None, 'A_B_ncap.x', 80)
        def A_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_B_ncap_delfunc()
        try: test(x, None, 84)
        except NameError: test(None, None, 85)
        x = "A_B_ncap.x"
        try: test(x, 'A_B_ncap.x', 87)
        except NameError: test(None, 'A_B_ncap.x', 88)
        del x
        try: test(x, None, 90)
        except NameError: test(None, None, 91)
    def A_b():
        pass
    A_b()
    def A_b_use():
        try: test(x, None, 96)
        except NameError: test(None, None, 97)
    A_b_use()
    def A_b_anno():
        x: str
        try: test(x, None, 101)
        except NameError: test(None, None, 102)
    A_b_anno()
    def A_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 107)
        else: error("Enclosed binding exists", 108)
    A_b_nloc()
    def A_b_glob():
        global x
        try: test(x, None, 112)
        except NameError: test(None, None, 113)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 115)
        except NameError: test(None, 'x', 116)
        def A_b_glob_delfunc():
            global x; del x
        A_b_glob_delfunc()
        try: test(x, None, 120)
        except NameError: test(None, None, 121)
        x = "x"
        try: test(x, 'x', 123)
        except NameError: test(None, 'x', 124)
        del x
        try: test(x, None, 126)
        except NameError: test(None, None, 127)
    A_b_glob()
    def A_b_loc():
        try: test(x, None, 130)
        except NameError: test(None, None, 131)
        [x := _ for _ in ["A_b_loc.x"]]
        try: test(x, 'A_b_loc.x', 133)
        except NameError: test(None, 'A_b_loc.x', 134)
        def A_b_loc_delfunc():
            nonlocal x; del x
        A_b_loc_delfunc()
        try: test(x, None, 138)
        except NameError: test(None, None, 139)
        x = "A_b_loc.x"
        try: test(x, 'A_b_loc.x', 141)
        except NameError: test(None, 'A_b_loc.x', 142)
        del x
        try: test(x, None, 144)
        except NameError: test(None, None, 145)
    A_b_loc()
    def A_b_ncap():
        try: test(x, None, 148)
        except NameError: test(None, None, 149)
        [x := _ for _ in ["A_b_ncap.x"]]
        try: test(x, 'A_b_ncap.x', 151)
        except NameError: test(None, 'A_b_ncap.x', 152)
        def A_b_ncap_delfunc():
            nonlocal x; del x
        A_b_ncap_delfunc()
        try: test(x, None, 156)
        except NameError: test(None, None, 157)
        x = "A_b_ncap.x"
        try: test(x, 'A_b_ncap.x', 159)
        except NameError: test(None, 'A_b_ncap.x', 160)
        del x
        try: test(x, None, 162)
        except NameError: test(None, None, 163)
    A_b_ncap()
class A_use:
    try: test(x, None, 166)
    except NameError: test(None, None, 167)
    class A_use_B:
        pass
    class A_use_B_use:
        try: test(x, None, 171)
        except NameError: test(None, None, 172)
    class A_use_B_anno:
        x: str
        try: test(x, None, 175)
        except NameError: test(None, None, 176)
    class A_use_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 180)
        else: error("Enclosed binding exists", 181)
    class A_use_B_glob:
        global x
        try: test(x, None, 184)
        except NameError: test(None, None, 185)
        def A_use_B_glob_setfunc():
            global x; x = "x"
        A_use_B_glob_setfunc()
        try: test(x, 'x', 189)
        except NameError: test(None, 'x', 190)
        def A_use_B_glob_delfunc():
            global x; del x
        A_use_B_glob_delfunc()
        try: test(x, None, 194)
        except NameError: test(None, None, 195)
        x = "x"
        try: test(x, 'x', 197)
        except NameError: test(None, 'x', 198)
        del x
        try: test(x, None, 200)
        except NameError: test(None, None, 201)
    class A_use_B_loc:
        try: test(x, None, 203)
        except NameError: test(None, None, 204)
        def A_use_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_use_B_loc.x"
        A_use_B_loc_setfunc()
        try: test(x, 'A_use_B_loc.x', 208)
        except NameError: test(None, 'A_use_B_loc.x', 209)
        def A_use_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_use_B_loc_delfunc()
        try: test(x, None, 213)
        except NameError: test(None, None, 214)
        x = "A_use_B_loc.x"
        try: test(x, 'A_use_B_loc.x', 216)
        except NameError: test(None, 'A_use_B_loc.x', 217)
        del x
        try: test(x, None, 219)
        except NameError: test(None, None, 220)
    class A_use_B_ncap:
        try: test(x, None, 222)
        except NameError: test(None, None, 223)
        def A_use_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_use_B_ncap.x"
        A_use_B_ncap_setfunc()
        try: test(x, 'A_use_B_ncap.x', 227)
        except NameError: test(None, 'A_use_B_ncap.x', 228)
        def A_use_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_use_B_ncap_delfunc()
        try: test(x, None, 232)
        except NameError: test(None, None, 233)
        x = "A_use_B_ncap.x"
        try: test(x, 'A_use_B_ncap.x', 235)
        except NameError: test(None, 'A_use_B_ncap.x', 236)
        del x
        try: test(x, None, 238)
        except NameError: test(None, None, 239)
    def A_use_b():
        pass
    A_use_b()
    def A_use_b_use():
        try: test(x, None, 244)
        except NameError: test(None, None, 245)
    A_use_b_use()
    def A_use_b_anno():
        x: str
        try: test(x, None, 249)
        except NameError: test(None, None, 250)
    A_use_b_anno()
    def A_use_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 255)
        else: error("Enclosed binding exists", 256)
    A_use_b_nloc()
    def A_use_b_glob():
        global x
        try: test(x, None, 260)
        except NameError: test(None, None, 261)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 263)
        except NameError: test(None, 'x', 264)
        def A_use_b_glob_delfunc():
            global x; del x
        A_use_b_glob_delfunc()
        try: test(x, None, 268)
        except NameError: test(None, None, 269)
        x = "x"
        try: test(x, 'x', 271)
        except NameError: test(None, 'x', 272)
        del x
        try: test(x, None, 274)
        except NameError: test(None, None, 275)
    A_use_b_glob()
    def A_use_b_loc():
        try: test(x, None, 278)
        except NameError: test(None, None, 279)
        [x := _ for _ in ["A_use_b_loc.x"]]
        try: test(x, 'A_use_b_loc.x', 281)
        except NameError: test(None, 'A_use_b_loc.x', 282)
        def A_use_b_loc_delfunc():
            nonlocal x; del x
        A_use_b_loc_delfunc()
        try: test(x, None, 286)
        except NameError: test(None, None, 287)
        x = "A_use_b_loc.x"
        try: test(x, 'A_use_b_loc.x', 289)
        except NameError: test(None, 'A_use_b_loc.x', 290)
        del x
        try: test(x, None, 292)
        except NameError: test(None, None, 293)
    A_use_b_loc()
    def A_use_b_ncap():
        try: test(x, None, 296)
        except NameError: test(None, None, 297)
        [x := _ for _ in ["A_use_b_ncap.x"]]
        try: test(x, 'A_use_b_ncap.x', 299)
        except NameError: test(None, 'A_use_b_ncap.x', 300)
        def A_use_b_ncap_delfunc():
            nonlocal x; del x
        A_use_b_ncap_delfunc()
        try: test(x, None, 304)
        except NameError: test(None, None, 305)
        x = "A_use_b_ncap.x"
        try: test(x, 'A_use_b_ncap.x', 307)
        except NameError: test(None, 'A_use_b_ncap.x', 308)
        del x
        try: test(x, None, 310)
        except NameError: test(None, None, 311)
    A_use_b_ncap()
class A_anno:
    x: str
    try: test(x, None, 315)
    except NameError: test(None, None, 316)
    class A_anno_B:
        pass
    class A_anno_B_use:
        try: test(x, None, 320)
        except NameError: test(None, None, 321)
    class A_anno_B_anno:
        x: str
        try: test(x, None, 324)
        except NameError: test(None, None, 325)
    class A_anno_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 329)
        else: error("Enclosed binding exists", 330)
    class A_anno_B_glob:
        global x
        try: test(x, None, 333)
        except NameError: test(None, None, 334)
        def A_anno_B_glob_setfunc():
            global x; x = "x"
        A_anno_B_glob_setfunc()
        try: test(x, 'x', 338)
        except NameError: test(None, 'x', 339)
        def A_anno_B_glob_delfunc():
            global x; del x
        A_anno_B_glob_delfunc()
        try: test(x, None, 343)
        except NameError: test(None, None, 344)
        x = "x"
        try: test(x, 'x', 346)
        except NameError: test(None, 'x', 347)
        del x
        try: test(x, None, 349)
        except NameError: test(None, None, 350)
    class A_anno_B_loc:
        try: test(x, None, 352)
        except NameError: test(None, None, 353)
        def A_anno_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_anno_B_loc.x"
        A_anno_B_loc_setfunc()
        try: test(x, 'A_anno_B_loc.x', 357)
        except NameError: test(None, 'A_anno_B_loc.x', 358)
        def A_anno_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_anno_B_loc_delfunc()
        try: test(x, None, 362)
        except NameError: test(None, None, 363)
        x = "A_anno_B_loc.x"
        try: test(x, 'A_anno_B_loc.x', 365)
        except NameError: test(None, 'A_anno_B_loc.x', 366)
        del x
        try: test(x, None, 368)
        except NameError: test(None, None, 369)
    class A_anno_B_ncap:
        try: test(x, None, 371)
        except NameError: test(None, None, 372)
        def A_anno_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_anno_B_ncap.x"
        A_anno_B_ncap_setfunc()
        try: test(x, 'A_anno_B_ncap.x', 376)
        except NameError: test(None, 'A_anno_B_ncap.x', 377)
        def A_anno_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_anno_B_ncap_delfunc()
        try: test(x, None, 381)
        except NameError: test(None, None, 382)
        x = "A_anno_B_ncap.x"
        try: test(x, 'A_anno_B_ncap.x', 384)
        except NameError: test(None, 'A_anno_B_ncap.x', 385)
        del x
        try: test(x, None, 387)
        except NameError: test(None, None, 388)
    def A_anno_b():
        pass
    A_anno_b()
    def A_anno_b_use():
        try: test(x, None, 393)
        except NameError: test(None, None, 394)
    A_anno_b_use()
    def A_anno_b_anno():
        x: str
        try: test(x, None, 398)
        except NameError: test(None, None, 399)
    A_anno_b_anno()
    def A_anno_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 404)
        else: error("Enclosed binding exists", 405)
    A_anno_b_nloc()
    def A_anno_b_glob():
        global x
        try: test(x, None, 409)
        except NameError: test(None, None, 410)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 412)
        except NameError: test(None, 'x', 413)
        def A_anno_b_glob_delfunc():
            global x; del x
        A_anno_b_glob_delfunc()
        try: test(x, None, 417)
        except NameError: test(None, None, 418)
        x = "x"
        try: test(x, 'x', 420)
        except NameError: test(None, 'x', 421)
        del x
        try: test(x, None, 423)
        except NameError: test(None, None, 424)
    A_anno_b_glob()
    def A_anno_b_loc():
        try: test(x, None, 427)
        except NameError: test(None, None, 428)
        [x := _ for _ in ["A_anno_b_loc.x"]]
        try: test(x, 'A_anno_b_loc.x', 430)
        except NameError: test(None, 'A_anno_b_loc.x', 431)
        def A_anno_b_loc_delfunc():
            nonlocal x; del x
        A_anno_b_loc_delfunc()
        try: test(x, None, 435)
        except NameError: test(None, None, 436)
        x = "A_anno_b_loc.x"
        try: test(x, 'A_anno_b_loc.x', 438)
        except NameError: test(None, 'A_anno_b_loc.x', 439)
        del x
        try: test(x, None, 441)
        except NameError: test(None, None, 442)
    A_anno_b_loc()
    def A_anno_b_ncap():
        try: test(x, None, 445)
        except NameError: test(None, None, 446)
        [x := _ for _ in ["A_anno_b_ncap.x"]]
        try: test(x, 'A_anno_b_ncap.x', 448)
        except NameError: test(None, 'A_anno_b_ncap.x', 449)
        def A_anno_b_ncap_delfunc():
            nonlocal x; del x
        A_anno_b_ncap_delfunc()
        try: test(x, None, 453)
        except NameError: test(None, None, 454)
        x = "A_anno_b_ncap.x"
        try: test(x, 'A_anno_b_ncap.x', 456)
        except NameError: test(None, 'A_anno_b_ncap.x', 457)
        del x
        try: test(x, None, 459)
        except NameError: test(None, None, 460)
    A_anno_b_ncap()
class A_nloc:
    # No enclosed binding exists.
    try: compile("nonlocal x", "<string>", "exec")
    except SyntaxError: test(None, None, 465)
    else: error("Enclosed binding exists", 466)
class A_glob:
    global x
    try: test(x, None, 469)
    except NameError: test(None, None, 470)
    class A_glob_B:
        pass
    class A_glob_B_use:
        try: test(x, None, 474)
        except NameError: test(None, None, 475)
    class A_glob_B_anno:
        x: str
        try: test(x, None, 478)
        except NameError: test(None, None, 479)
    class A_glob_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 483)
        else: error("Enclosed binding exists", 484)
    class A_glob_B_glob:
        global x
        try: test(x, None, 487)
        except NameError: test(None, None, 488)
        def A_glob_B_glob_setfunc():
            global x; x = "x"
        A_glob_B_glob_setfunc()
        try: test(x, 'x', 492)
        except NameError: test(None, 'x', 493)
        def A_glob_B_glob_delfunc():
            global x; del x
        A_glob_B_glob_delfunc()
        try: test(x, None, 497)
        except NameError: test(None, None, 498)
        x = "x"
        try: test(x, 'x', 500)
        except NameError: test(None, 'x', 501)
        del x
        try: test(x, None, 503)
        except NameError: test(None, None, 504)
    class A_glob_B_loc:
        try: test(x, None, 506)
        except NameError: test(None, None, 507)
        def A_glob_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_glob_B_loc.x"
        A_glob_B_loc_setfunc()
        try: test(x, 'A_glob_B_loc.x', 511)
        except NameError: test(None, 'A_glob_B_loc.x', 512)
        def A_glob_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_glob_B_loc_delfunc()
        try: test(x, None, 516)
        except NameError: test(None, None, 517)
        x = "A_glob_B_loc.x"
        try: test(x, 'A_glob_B_loc.x', 519)
        except NameError: test(None, 'A_glob_B_loc.x', 520)
        del x
        try: test(x, None, 522)
        except NameError: test(None, None, 523)
    class A_glob_B_ncap:
        try: test(x, None, 525)
        except NameError: test(None, None, 526)
        def A_glob_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_glob_B_ncap.x"
        A_glob_B_ncap_setfunc()
        try: test(x, 'A_glob_B_ncap.x', 530)
        except NameError: test(None, 'A_glob_B_ncap.x', 531)
        def A_glob_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_glob_B_ncap_delfunc()
        try: test(x, None, 535)
        except NameError: test(None, None, 536)
        x = "A_glob_B_ncap.x"
        try: test(x, 'A_glob_B_ncap.x', 538)
        except NameError: test(None, 'A_glob_B_ncap.x', 539)
        del x
        try: test(x, None, 541)
        except NameError: test(None, None, 542)
    def A_glob_b():
        pass
    A_glob_b()
    def A_glob_b_use():
        try: test(x, None, 547)
        except NameError: test(None, None, 548)
    A_glob_b_use()
    def A_glob_b_anno():
        x: str
        try: test(x, None, 552)
        except NameError: test(None, None, 553)
    A_glob_b_anno()
    def A_glob_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 558)
        else: error("Enclosed binding exists", 559)
    A_glob_b_nloc()
    def A_glob_b_glob():
        global x
        try: test(x, None, 563)
        except NameError: test(None, None, 564)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 566)
        except NameError: test(None, 'x', 567)
        def A_glob_b_glob_delfunc():
            global x; del x
        A_glob_b_glob_delfunc()
        try: test(x, None, 571)
        except NameError: test(None, None, 572)
        x = "x"
        try: test(x, 'x', 574)
        except NameError: test(None, 'x', 575)
        del x
        try: test(x, None, 577)
        except NameError: test(None, None, 578)
    A_glob_b_glob()
    def A_glob_b_loc():
        try: test(x, None, 581)
        except NameError: test(None, None, 582)
        [x := _ for _ in ["A_glob_b_loc.x"]]
        try: test(x, 'A_glob_b_loc.x', 584)
        except NameError: test(None, 'A_glob_b_loc.x', 585)
        def A_glob_b_loc_delfunc():
            nonlocal x; del x
        A_glob_b_loc_delfunc()
        try: test(x, None, 589)
        except NameError: test(None, None, 590)
        x = "A_glob_b_loc.x"
        try: test(x, 'A_glob_b_loc.x', 592)
        except NameError: test(None, 'A_glob_b_loc.x', 593)
        del x
        try: test(x, None, 595)
        except NameError: test(None, None, 596)
    A_glob_b_loc()
    def A_glob_b_ncap():
        try: test(x, None, 599)
        except NameError: test(None, None, 600)
        [x := _ for _ in ["A_glob_b_ncap.x"]]
        try: test(x, 'A_glob_b_ncap.x', 602)
        except NameError: test(None, 'A_glob_b_ncap.x', 603)
        def A_glob_b_ncap_delfunc():
            nonlocal x; del x
        A_glob_b_ncap_delfunc()
        try: test(x, None, 607)
        except NameError: test(None, None, 608)
        x = "A_glob_b_ncap.x"
        try: test(x, 'A_glob_b_ncap.x', 610)
        except NameError: test(None, 'A_glob_b_ncap.x', 611)
        del x
        try: test(x, None, 613)
        except NameError: test(None, None, 614)
    A_glob_b_ncap()
    def A_glob_setfunc():
        global x; x = "x"
    A_glob_setfunc()
    try: test(x, 'x', 619)
    except NameError: test(None, 'x', 620)
    def A_glob_delfunc():
        global x; del x
    A_glob_delfunc()
    try: test(x, None, 624)
    except NameError: test(None, None, 625)
    x = "x"
    try: test(x, 'x', 627)
    except NameError: test(None, 'x', 628)
    class A_glob_B2:
        pass
    class A_glob_B2_use:
        try: test(x, 'x', 632)
        except NameError: test(None, 'x', 633)
    class A_glob_B2_anno:
        x: str
        try: test(x, 'x', 636)
        except NameError: test(None, 'x', 637)
    class A_glob_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 641)
        else: error("Enclosed binding exists", 642)
    class A_glob_B2_glob:
        global x
        try: test(x, 'x', 645)
        except NameError: test(None, 'x', 646)
        del x
        try: test(x, None, 648)
        except NameError: test(None, None, 649)
        def A_glob_B2_glob_setfunc():
            global x; x = "x"
        A_glob_B2_glob_setfunc()
        try: test(x, 'x', 653)
        except NameError: test(None, 'x', 654)
        def A_glob_B2_glob_delfunc():
            global x; del x
        A_glob_B2_glob_delfunc()
        try: test(x, None, 658)
        except NameError: test(None, None, 659)
        x = "x"
        try: test(x, 'x', 661)
        except NameError: test(None, 'x', 662)
    class A_glob_B2_loc:
        try: test(x, 'x', 664)
        except NameError: test(None, 'x', 665)
        def A_glob_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_glob_B2_loc.x"
        A_glob_B2_loc_setfunc()
        try: test(x, 'A_glob_B2_loc.x', 669)
        except NameError: test(None, 'A_glob_B2_loc.x', 670)
        def A_glob_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_glob_B2_loc_delfunc()
        try: test(x, 'x', 674)
        except NameError: test(None, 'x', 675)
        x = "A_glob_B2_loc.x"
        try: test(x, 'A_glob_B2_loc.x', 677)
        except NameError: test(None, 'A_glob_B2_loc.x', 678)
        del x
        try: test(x, 'x', 680)
        except NameError: test(None, 'x', 681)
    class A_glob_B2_ncap:
        try: test(x, 'x', 683)
        except NameError: test(None, 'x', 684)
        def A_glob_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_glob_B2_ncap.x"
        A_glob_B2_ncap_setfunc()
        try: test(x, 'A_glob_B2_ncap.x', 688)
        except NameError: test(None, 'A_glob_B2_ncap.x', 689)
        def A_glob_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_glob_B2_ncap_delfunc()
        try: test(x, 'x', 693)
        except NameError: test(None, 'x', 694)
        x = "A_glob_B2_ncap.x"
        try: test(x, 'A_glob_B2_ncap.x', 696)
        except NameError: test(None, 'A_glob_B2_ncap.x', 697)
        del x
        try: test(x, 'x', 699)
        except NameError: test(None, 'x', 700)
    def A_glob_b2():
        pass
    A_glob_b2()
    def A_glob_b2_use():
        try: test(x, 'x', 705)
        except NameError: test(None, 'x', 706)
    A_glob_b2_use()
    def A_glob_b2_anno():
        x: str
        try: test(x, None, 710)
        except NameError: test(None, None, 711)
    A_glob_b2_anno()
    def A_glob_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 716)
        else: error("Enclosed binding exists", 717)
    A_glob_b2_nloc()
    def A_glob_b2_glob():
        global x
        try: test(x, 'x', 721)
        except NameError: test(None, 'x', 722)
        del x
        try: test(x, None, 724)
        except NameError: test(None, None, 725)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 727)
        except NameError: test(None, 'x', 728)
        def A_glob_b2_glob_delfunc():
            global x; del x
        A_glob_b2_glob_delfunc()
        try: test(x, None, 732)
        except NameError: test(None, None, 733)
        x = "x"
        try: test(x, 'x', 735)
        except NameError: test(None, 'x', 736)
    A_glob_b2_glob()
    def A_glob_b2_loc():
        try: test(x, None, 739)
        except NameError: test(None, None, 740)
        [x := _ for _ in ["A_glob_b2_loc.x"]]
        try: test(x, 'A_glob_b2_loc.x', 742)
        except NameError: test(None, 'A_glob_b2_loc.x', 743)
        def A_glob_b2_loc_delfunc():
            nonlocal x; del x
        A_glob_b2_loc_delfunc()
        try: test(x, None, 747)
        except NameError: test(None, None, 748)
        x = "A_glob_b2_loc.x"
        try: test(x, 'A_glob_b2_loc.x', 750)
        except NameError: test(None, 'A_glob_b2_loc.x', 751)
        del x
        try: test(x, None, 753)
        except NameError: test(None, None, 754)
    A_glob_b2_loc()
    def A_glob_b2_ncap():
        try: test(x, None, 757)
        except NameError: test(None, None, 758)
        [x := _ for _ in ["A_glob_b2_ncap.x"]]
        try: test(x, 'A_glob_b2_ncap.x', 760)
        except NameError: test(None, 'A_glob_b2_ncap.x', 761)
        def A_glob_b2_ncap_delfunc():
            nonlocal x; del x
        A_glob_b2_ncap_delfunc()
        try: test(x, None, 765)
        except NameError: test(None, None, 766)
        x = "A_glob_b2_ncap.x"
        try: test(x, 'A_glob_b2_ncap.x', 768)
        except NameError: test(None, 'A_glob_b2_ncap.x', 769)
        del x
        try: test(x, None, 771)
        except NameError: test(None, None, 772)
    A_glob_b2_ncap()
    del x
    try: test(x, None, 775)
    except NameError: test(None, None, 776)
class A_loc:
    try: test(x, None, 778)
    except NameError: test(None, None, 779)
    class A_loc_B:
        pass
    class A_loc_B_use:
        try: test(x, None, 783)
        except NameError: test(None, None, 784)
    class A_loc_B_anno:
        x: str
        try: test(x, None, 787)
        except NameError: test(None, None, 788)
    class A_loc_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 792)
        else: error("Enclosed binding exists", 793)
    class A_loc_B_glob:
        global x
        try: test(x, None, 796)
        except NameError: test(None, None, 797)
        def A_loc_B_glob_setfunc():
            global x; x = "x"
        A_loc_B_glob_setfunc()
        try: test(x, 'x', 801)
        except NameError: test(None, 'x', 802)
        def A_loc_B_glob_delfunc():
            global x; del x
        A_loc_B_glob_delfunc()
        try: test(x, None, 806)
        except NameError: test(None, None, 807)
        x = "x"
        try: test(x, 'x', 809)
        except NameError: test(None, 'x', 810)
        del x
        try: test(x, None, 812)
        except NameError: test(None, None, 813)
    class A_loc_B_loc:
        try: test(x, None, 815)
        except NameError: test(None, None, 816)
        def A_loc_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_loc_B_loc.x"
        A_loc_B_loc_setfunc()
        try: test(x, 'A_loc_B_loc.x', 820)
        except NameError: test(None, 'A_loc_B_loc.x', 821)
        def A_loc_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_loc_B_loc_delfunc()
        try: test(x, None, 825)
        except NameError: test(None, None, 826)
        x = "A_loc_B_loc.x"
        try: test(x, 'A_loc_B_loc.x', 828)
        except NameError: test(None, 'A_loc_B_loc.x', 829)
        del x
        try: test(x, None, 831)
        except NameError: test(None, None, 832)
    class A_loc_B_ncap:
        try: test(x, None, 834)
        except NameError: test(None, None, 835)
        def A_loc_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_loc_B_ncap.x"
        A_loc_B_ncap_setfunc()
        try: test(x, 'A_loc_B_ncap.x', 839)
        except NameError: test(None, 'A_loc_B_ncap.x', 840)
        def A_loc_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_loc_B_ncap_delfunc()
        try: test(x, None, 844)
        except NameError: test(None, None, 845)
        x = "A_loc_B_ncap.x"
        try: test(x, 'A_loc_B_ncap.x', 847)
        except NameError: test(None, 'A_loc_B_ncap.x', 848)
        del x
        try: test(x, None, 850)
        except NameError: test(None, None, 851)
    def A_loc_b():
        pass
    A_loc_b()
    def A_loc_b_use():
        try: test(x, None, 856)
        except NameError: test(None, None, 857)
    A_loc_b_use()
    def A_loc_b_anno():
        x: str
        try: test(x, None, 861)
        except NameError: test(None, None, 862)
    A_loc_b_anno()
    def A_loc_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 867)
        else: error("Enclosed binding exists", 868)
    A_loc_b_nloc()
    def A_loc_b_glob():
        global x
        try: test(x, None, 872)
        except NameError: test(None, None, 873)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 875)
        except NameError: test(None, 'x', 876)
        def A_loc_b_glob_delfunc():
            global x; del x
        A_loc_b_glob_delfunc()
        try: test(x, None, 880)
        except NameError: test(None, None, 881)
        x = "x"
        try: test(x, 'x', 883)
        except NameError: test(None, 'x', 884)
        del x
        try: test(x, None, 886)
        except NameError: test(None, None, 887)
    A_loc_b_glob()
    def A_loc_b_loc():
        try: test(x, None, 890)
        except NameError: test(None, None, 891)
        [x := _ for _ in ["A_loc_b_loc.x"]]
        try: test(x, 'A_loc_b_loc.x', 893)
        except NameError: test(None, 'A_loc_b_loc.x', 894)
        def A_loc_b_loc_delfunc():
            nonlocal x; del x
        A_loc_b_loc_delfunc()
        try: test(x, None, 898)
        except NameError: test(None, None, 899)
        x = "A_loc_b_loc.x"
        try: test(x, 'A_loc_b_loc.x', 901)
        except NameError: test(None, 'A_loc_b_loc.x', 902)
        del x
        try: test(x, None, 904)
        except NameError: test(None, None, 905)
    A_loc_b_loc()
    def A_loc_b_ncap():
        try: test(x, None, 908)
        except NameError: test(None, None, 909)
        [x := _ for _ in ["A_loc_b_ncap.x"]]
        try: test(x, 'A_loc_b_ncap.x', 911)
        except NameError: test(None, 'A_loc_b_ncap.x', 912)
        def A_loc_b_ncap_delfunc():
            nonlocal x; del x
        A_loc_b_ncap_delfunc()
        try: test(x, None, 916)
        except NameError: test(None, None, 917)
        x = "A_loc_b_ncap.x"
        try: test(x, 'A_loc_b_ncap.x', 919)
        except NameError: test(None, 'A_loc_b_ncap.x', 920)
        del x
        try: test(x, None, 922)
        except NameError: test(None, None, 923)
    A_loc_b_ncap()
    def A_loc_setfunc():
        inspect.stack()[1].frame.f_locals["x"] = "A_loc.x"
    A_loc_setfunc()
    try: test(x, 'A_loc.x', 928)
    except NameError: test(None, 'A_loc.x', 929)
    def A_loc_delfunc():
        del inspect.stack()[1].frame.f_locals["x"]
    A_loc_delfunc()
    try: test(x, None, 933)
    except NameError: test(None, None, 934)
    x = "A_loc.x"
    try: test(x, 'A_loc.x', 936)
    except NameError: test(None, 'A_loc.x', 937)
    class A_loc_B2:
        pass
    class A_loc_B2_use:
        try: test(x, None, 941)
        except NameError: test(None, None, 942)
    class A_loc_B2_anno:
        x: str
        try: test(x, None, 945)
        except NameError: test(None, None, 946)
    class A_loc_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 950)
        else: error("Enclosed binding exists", 951)
    class A_loc_B2_glob:
        global x
        try: test(x, None, 954)
        except NameError: test(None, None, 955)
        def A_loc_B2_glob_setfunc():
            global x; x = "x"
        A_loc_B2_glob_setfunc()
        try: test(x, 'x', 959)
        except NameError: test(None, 'x', 960)
        def A_loc_B2_glob_delfunc():
            global x; del x
        A_loc_B2_glob_delfunc()
        try: test(x, None, 964)
        except NameError: test(None, None, 965)
        x = "x"
        try: test(x, 'x', 967)
        except NameError: test(None, 'x', 968)
        del x
        try: test(x, None, 970)
        except NameError: test(None, None, 971)
    class A_loc_B2_loc:
        try: test(x, None, 973)
        except NameError: test(None, None, 974)
        def A_loc_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_loc_B2_loc.x"
        A_loc_B2_loc_setfunc()
        try: test(x, 'A_loc_B2_loc.x', 978)
        except NameError: test(None, 'A_loc_B2_loc.x', 979)
        def A_loc_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_loc_B2_loc_delfunc()
        try: test(x, None, 983)
        except NameError: test(None, None, 984)
        x = "A_loc_B2_loc.x"
        try: test(x, 'A_loc_B2_loc.x', 986)
        except NameError: test(None, 'A_loc_B2_loc.x', 987)
        del x
        try: test(x, None, 989)
        except NameError: test(None, None, 990)
    class A_loc_B2_ncap:
        try: test(x, None, 992)
        except NameError: test(None, None, 993)
        def A_loc_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_loc_B2_ncap.x"
        A_loc_B2_ncap_setfunc()
        try: test(x, 'A_loc_B2_ncap.x', 997)
        except NameError: test(None, 'A_loc_B2_ncap.x', 998)
        def A_loc_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_loc_B2_ncap_delfunc()
        try: test(x, None, 1002)
        except NameError: test(None, None, 1003)
        x = "A_loc_B2_ncap.x"
        try: test(x, 'A_loc_B2_ncap.x', 1005)
        except NameError: test(None, 'A_loc_B2_ncap.x', 1006)
        del x
        try: test(x, None, 1008)
        except NameError: test(None, None, 1009)
    def A_loc_b2():
        pass
    A_loc_b2()
    def A_loc_b2_use():
        try: test(x, None, 1014)
        except NameError: test(None, None, 1015)
    A_loc_b2_use()
    def A_loc_b2_anno():
        x: str
        try: test(x, None, 1019)
        except NameError: test(None, None, 1020)
    A_loc_b2_anno()
    def A_loc_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1025)
        else: error("Enclosed binding exists", 1026)
    A_loc_b2_nloc()
    def A_loc_b2_glob():
        global x
        try: test(x, None, 1030)
        except NameError: test(None, None, 1031)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1033)
        except NameError: test(None, 'x', 1034)
        def A_loc_b2_glob_delfunc():
            global x; del x
        A_loc_b2_glob_delfunc()
        try: test(x, None, 1038)
        except NameError: test(None, None, 1039)
        x = "x"
        try: test(x, 'x', 1041)
        except NameError: test(None, 'x', 1042)
        del x
        try: test(x, None, 1044)
        except NameError: test(None, None, 1045)
    A_loc_b2_glob()
    def A_loc_b2_loc():
        try: test(x, None, 1048)
        except NameError: test(None, None, 1049)
        [x := _ for _ in ["A_loc_b2_loc.x"]]
        try: test(x, 'A_loc_b2_loc.x', 1051)
        except NameError: test(None, 'A_loc_b2_loc.x', 1052)
        def A_loc_b2_loc_delfunc():
            nonlocal x; del x
        A_loc_b2_loc_delfunc()
        try: test(x, None, 1056)
        except NameError: test(None, None, 1057)
        x = "A_loc_b2_loc.x"
        try: test(x, 'A_loc_b2_loc.x', 1059)
        except NameError: test(None, 'A_loc_b2_loc.x', 1060)
        del x
        try: test(x, None, 1062)
        except NameError: test(None, None, 1063)
    A_loc_b2_loc()
    def A_loc_b2_ncap():
        try: test(x, None, 1066)
        except NameError: test(None, None, 1067)
        [x := _ for _ in ["A_loc_b2_ncap.x"]]
        try: test(x, 'A_loc_b2_ncap.x', 1069)
        except NameError: test(None, 'A_loc_b2_ncap.x', 1070)
        def A_loc_b2_ncap_delfunc():
            nonlocal x; del x
        A_loc_b2_ncap_delfunc()
        try: test(x, None, 1074)
        except NameError: test(None, None, 1075)
        x = "A_loc_b2_ncap.x"
        try: test(x, 'A_loc_b2_ncap.x', 1077)
        except NameError: test(None, 'A_loc_b2_ncap.x', 1078)
        del x
        try: test(x, None, 1080)
        except NameError: test(None, None, 1081)
    A_loc_b2_ncap()
    del x
    try: test(x, None, 1084)
    except NameError: test(None, None, 1085)
class A_ncap:
    try: test(x, None, 1087)
    except NameError: test(None, None, 1088)
    class A_ncap_B:
        pass
    class A_ncap_B_glob:
        global x
        try: test(x, None, 1093)
        except NameError: test(None, None, 1094)
        def A_ncap_B_glob_setfunc():
            global x; x = "x"
        A_ncap_B_glob_setfunc()
        try: test(x, 'x', 1098)
        except NameError: test(None, 'x', 1099)
        def A_ncap_B_glob_delfunc():
            global x; del x
        A_ncap_B_glob_delfunc()
        try: test(x, None, 1103)
        except NameError: test(None, None, 1104)
        x = "x"
        try: test(x, 'x', 1106)
        except NameError: test(None, 'x', 1107)
        del x
        try: test(x, None, 1109)
        except NameError: test(None, None, 1110)
    class A_ncap_B_loc:
        try: test(x, None, 1112)
        except NameError: test(None, None, 1113)
        def A_ncap_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_ncap_B_loc.x"
        A_ncap_B_loc_setfunc()
        try: test(x, 'A_ncap_B_loc.x', 1117)
        except NameError: test(None, 'A_ncap_B_loc.x', 1118)
        def A_ncap_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_ncap_B_loc_delfunc()
        try: test(x, None, 1122)
        except NameError: test(None, None, 1123)
        x = "A_ncap_B_loc.x"
        try: test(x, 'A_ncap_B_loc.x', 1125)
        except NameError: test(None, 'A_ncap_B_loc.x', 1126)
        del x
        try: test(x, None, 1128)
        except NameError: test(None, None, 1129)
    def A_ncap_b():
        pass
    A_ncap_b()
    def A_ncap_b_glob():
        global x
        try: test(x, None, 1135)
        except NameError: test(None, None, 1136)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1138)
        except NameError: test(None, 'x', 1139)
        def A_ncap_b_glob_delfunc():
            global x; del x
        A_ncap_b_glob_delfunc()
        try: test(x, None, 1143)
        except NameError: test(None, None, 1144)
        x = "x"
        try: test(x, 'x', 1146)
        except NameError: test(None, 'x', 1147)
        del x
        try: test(x, None, 1149)
        except NameError: test(None, None, 1150)
    A_ncap_b_glob()
    def A_ncap_b_loc():
        try: test(x, None, 1153)
        except NameError: test(None, None, 1154)
        [x := _ for _ in ["A_ncap_b_loc.x"]]
        try: test(x, 'A_ncap_b_loc.x', 1156)
        except NameError: test(None, 'A_ncap_b_loc.x', 1157)
        def A_ncap_b_loc_delfunc():
            nonlocal x; del x
        A_ncap_b_loc_delfunc()
        try: test(x, None, 1161)
        except NameError: test(None, None, 1162)
        x = "A_ncap_b_loc.x"
        try: test(x, 'A_ncap_b_loc.x', 1164)
        except NameError: test(None, 'A_ncap_b_loc.x', 1165)
        del x
        try: test(x, None, 1167)
        except NameError: test(None, None, 1168)
    A_ncap_b_loc()
    def A_ncap_setfunc():
        inspect.stack()[1].frame.f_locals["x"] = "A_ncap.x"
    A_ncap_setfunc()
    try: test(x, 'A_ncap.x', 1173)
    except NameError: test(None, 'A_ncap.x', 1174)
    def A_ncap_delfunc():
        del inspect.stack()[1].frame.f_locals["x"]
    A_ncap_delfunc()
    try: test(x, None, 1178)
    except NameError: test(None, None, 1179)
    x = "A_ncap.x"
    try: test(x, 'A_ncap.x', 1181)
    except NameError: test(None, 'A_ncap.x', 1182)
    class A_ncap_B2:
        pass
    class A_ncap_B2_glob:
        global x
        try: test(x, None, 1187)
        except NameError: test(None, None, 1188)
        def A_ncap_B2_glob_setfunc():
            global x; x = "x"
        A_ncap_B2_glob_setfunc()
        try: test(x, 'x', 1192)
        except NameError: test(None, 'x', 1193)
        def A_ncap_B2_glob_delfunc():
            global x; del x
        A_ncap_B2_glob_delfunc()
        try: test(x, None, 1197)
        except NameError: test(None, None, 1198)
        x = "x"
        try: test(x, 'x', 1200)
        except NameError: test(None, 'x', 1201)
        del x
        try: test(x, None, 1203)
        except NameError: test(None, None, 1204)
    class A_ncap_B2_loc:
        try: test(x, None, 1206)
        except NameError: test(None, None, 1207)
        def A_ncap_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A_ncap_B2_loc.x"
        A_ncap_B2_loc_setfunc()
        try: test(x, 'A_ncap_B2_loc.x', 1211)
        except NameError: test(None, 'A_ncap_B2_loc.x', 1212)
        def A_ncap_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A_ncap_B2_loc_delfunc()
        try: test(x, None, 1216)
        except NameError: test(None, None, 1217)
        x = "A_ncap_B2_loc.x"
        try: test(x, 'A_ncap_B2_loc.x', 1219)
        except NameError: test(None, 'A_ncap_B2_loc.x', 1220)
        del x
        try: test(x, None, 1222)
        except NameError: test(None, None, 1223)
    def A_ncap_b2():
        pass
    A_ncap_b2()
    def A_ncap_b2_glob():
        global x
        try: test(x, None, 1229)
        except NameError: test(None, None, 1230)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1232)
        except NameError: test(None, 'x', 1233)
        def A_ncap_b2_glob_delfunc():
            global x; del x
        A_ncap_b2_glob_delfunc()
        try: test(x, None, 1237)
        except NameError: test(None, None, 1238)
        x = "x"
        try: test(x, 'x', 1240)
        except NameError: test(None, 'x', 1241)
        del x
        try: test(x, None, 1243)
        except NameError: test(None, None, 1244)
    A_ncap_b2_glob()
    def A_ncap_b2_loc():
        try: test(x, None, 1247)
        except NameError: test(None, None, 1248)
        [x := _ for _ in ["A_ncap_b2_loc.x"]]
        try: test(x, 'A_ncap_b2_loc.x', 1250)
        except NameError: test(None, 'A_ncap_b2_loc.x', 1251)
        def A_ncap_b2_loc_delfunc():
            nonlocal x; del x
        A_ncap_b2_loc_delfunc()
        try: test(x, None, 1255)
        except NameError: test(None, None, 1256)
        x = "A_ncap_b2_loc.x"
        try: test(x, 'A_ncap_b2_loc.x', 1258)
        except NameError: test(None, 'A_ncap_b2_loc.x', 1259)
        del x
        try: test(x, None, 1261)
        except NameError: test(None, None, 1262)
    A_ncap_b2_loc()
    del x
    try: test(x, None, 1265)
    except NameError: test(None, None, 1266)
def a():
    class a_B:
        pass
    class a_B_use:
        try: test(x, None, 1271)
        except NameError: test(None, None, 1272)
    class a_B_anno:
        x: str
        try: test(x, None, 1275)
        except NameError: test(None, None, 1276)
    class a_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1280)
        else: error("Enclosed binding exists", 1281)
    class a_B_glob:
        global x
        try: test(x, None, 1284)
        except NameError: test(None, None, 1285)
        def a_B_glob_setfunc():
            global x; x = "x"
        a_B_glob_setfunc()
        try: test(x, 'x', 1289)
        except NameError: test(None, 'x', 1290)
        def a_B_glob_delfunc():
            global x; del x
        a_B_glob_delfunc()
        try: test(x, None, 1294)
        except NameError: test(None, None, 1295)
        x = "x"
        try: test(x, 'x', 1297)
        except NameError: test(None, 'x', 1298)
        del x
        try: test(x, None, 1300)
        except NameError: test(None, None, 1301)
    class a_B_loc:
        try: test(x, None, 1303)
        except NameError: test(None, None, 1304)
        def a_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_B_loc.x"
        a_B_loc_setfunc()
        try: test(x, 'a_B_loc.x', 1308)
        except NameError: test(None, 'a_B_loc.x', 1309)
        def a_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_B_loc_delfunc()
        try: test(x, None, 1313)
        except NameError: test(None, None, 1314)
        x = "a_B_loc.x"
        try: test(x, 'a_B_loc.x', 1316)
        except NameError: test(None, 'a_B_loc.x', 1317)
        del x
        try: test(x, None, 1319)
        except NameError: test(None, None, 1320)
    class a_B_ncap:
        try: test(x, None, 1322)
        except NameError: test(None, None, 1323)
        def a_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_B_ncap.x"
        a_B_ncap_setfunc()
        try: test(x, 'a_B_ncap.x', 1327)
        except NameError: test(None, 'a_B_ncap.x', 1328)
        def a_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_B_ncap_delfunc()
        try: test(x, None, 1332)
        except NameError: test(None, None, 1333)
        x = "a_B_ncap.x"
        try: test(x, 'a_B_ncap.x', 1335)
        except NameError: test(None, 'a_B_ncap.x', 1336)
        del x
        try: test(x, None, 1338)
        except NameError: test(None, None, 1339)
    def a_b():
        pass
    a_b()
    def a_b_use():
        try: test(x, None, 1344)
        except NameError: test(None, None, 1345)
    a_b_use()
    def a_b_anno():
        x: str
        try: test(x, None, 1349)
        except NameError: test(None, None, 1350)
    a_b_anno()
    def a_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1355)
        else: error("Enclosed binding exists", 1356)
    a_b_nloc()
    def a_b_glob():
        global x
        try: test(x, None, 1360)
        except NameError: test(None, None, 1361)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1363)
        except NameError: test(None, 'x', 1364)
        def a_b_glob_delfunc():
            global x; del x
        a_b_glob_delfunc()
        try: test(x, None, 1368)
        except NameError: test(None, None, 1369)
        x = "x"
        try: test(x, 'x', 1371)
        except NameError: test(None, 'x', 1372)
        del x
        try: test(x, None, 1374)
        except NameError: test(None, None, 1375)
    a_b_glob()
    def a_b_loc():
        try: test(x, None, 1378)
        except NameError: test(None, None, 1379)
        [x := _ for _ in ["a_b_loc.x"]]
        try: test(x, 'a_b_loc.x', 1381)
        except NameError: test(None, 'a_b_loc.x', 1382)
        def a_b_loc_delfunc():
            nonlocal x; del x
        a_b_loc_delfunc()
        try: test(x, None, 1386)
        except NameError: test(None, None, 1387)
        x = "a_b_loc.x"
        try: test(x, 'a_b_loc.x', 1389)
        except NameError: test(None, 'a_b_loc.x', 1390)
        del x
        try: test(x, None, 1392)
        except NameError: test(None, None, 1393)
    a_b_loc()
    def a_b_ncap():
        try: test(x, None, 1396)
        except NameError: test(None, None, 1397)
        [x := _ for _ in ["a_b_ncap.x"]]
        try: test(x, 'a_b_ncap.x', 1399)
        except NameError: test(None, 'a_b_ncap.x', 1400)
        def a_b_ncap_delfunc():
            nonlocal x; del x
        a_b_ncap_delfunc()
        try: test(x, None, 1404)
        except NameError: test(None, None, 1405)
        x = "a_b_ncap.x"
        try: test(x, 'a_b_ncap.x', 1407)
        except NameError: test(None, 'a_b_ncap.x', 1408)
        del x
        try: test(x, None, 1410)
        except NameError: test(None, None, 1411)
    a_b_ncap()
a()
def a_use():
    try: test(x, None, 1415)
    except NameError: test(None, None, 1416)
    class a_use_B:
        pass
    class a_use_B_use:
        try: test(x, None, 1420)
        except NameError: test(None, None, 1421)
    class a_use_B_anno:
        x: str
        try: test(x, None, 1424)
        except NameError: test(None, None, 1425)
    class a_use_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1429)
        else: error("Enclosed binding exists", 1430)
    class a_use_B_glob:
        global x
        try: test(x, None, 1433)
        except NameError: test(None, None, 1434)
        def a_use_B_glob_setfunc():
            global x; x = "x"
        a_use_B_glob_setfunc()
        try: test(x, 'x', 1438)
        except NameError: test(None, 'x', 1439)
        def a_use_B_glob_delfunc():
            global x; del x
        a_use_B_glob_delfunc()
        try: test(x, None, 1443)
        except NameError: test(None, None, 1444)
        x = "x"
        try: test(x, 'x', 1446)
        except NameError: test(None, 'x', 1447)
        del x
        try: test(x, None, 1449)
        except NameError: test(None, None, 1450)
    class a_use_B_loc:
        try: test(x, None, 1452)
        except NameError: test(None, None, 1453)
        def a_use_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_use_B_loc.x"
        a_use_B_loc_setfunc()
        try: test(x, 'a_use_B_loc.x', 1457)
        except NameError: test(None, 'a_use_B_loc.x', 1458)
        def a_use_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_use_B_loc_delfunc()
        try: test(x, None, 1462)
        except NameError: test(None, None, 1463)
        x = "a_use_B_loc.x"
        try: test(x, 'a_use_B_loc.x', 1465)
        except NameError: test(None, 'a_use_B_loc.x', 1466)
        del x
        try: test(x, None, 1468)
        except NameError: test(None, None, 1469)
    class a_use_B_ncap:
        try: test(x, None, 1471)
        except NameError: test(None, None, 1472)
        def a_use_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_use_B_ncap.x"
        a_use_B_ncap_setfunc()
        try: test(x, 'a_use_B_ncap.x', 1476)
        except NameError: test(None, 'a_use_B_ncap.x', 1477)
        def a_use_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_use_B_ncap_delfunc()
        try: test(x, None, 1481)
        except NameError: test(None, None, 1482)
        x = "a_use_B_ncap.x"
        try: test(x, 'a_use_B_ncap.x', 1484)
        except NameError: test(None, 'a_use_B_ncap.x', 1485)
        del x
        try: test(x, None, 1487)
        except NameError: test(None, None, 1488)
    def a_use_b():
        pass
    a_use_b()
    def a_use_b_use():
        try: test(x, None, 1493)
        except NameError: test(None, None, 1494)
    a_use_b_use()
    def a_use_b_anno():
        x: str
        try: test(x, None, 1498)
        except NameError: test(None, None, 1499)
    a_use_b_anno()
    def a_use_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1504)
        else: error("Enclosed binding exists", 1505)
    a_use_b_nloc()
    def a_use_b_glob():
        global x
        try: test(x, None, 1509)
        except NameError: test(None, None, 1510)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1512)
        except NameError: test(None, 'x', 1513)
        def a_use_b_glob_delfunc():
            global x; del x
        a_use_b_glob_delfunc()
        try: test(x, None, 1517)
        except NameError: test(None, None, 1518)
        x = "x"
        try: test(x, 'x', 1520)
        except NameError: test(None, 'x', 1521)
        del x
        try: test(x, None, 1523)
        except NameError: test(None, None, 1524)
    a_use_b_glob()
    def a_use_b_loc():
        try: test(x, None, 1527)
        except NameError: test(None, None, 1528)
        [x := _ for _ in ["a_use_b_loc.x"]]
        try: test(x, 'a_use_b_loc.x', 1530)
        except NameError: test(None, 'a_use_b_loc.x', 1531)
        def a_use_b_loc_delfunc():
            nonlocal x; del x
        a_use_b_loc_delfunc()
        try: test(x, None, 1535)
        except NameError: test(None, None, 1536)
        x = "a_use_b_loc.x"
        try: test(x, 'a_use_b_loc.x', 1538)
        except NameError: test(None, 'a_use_b_loc.x', 1539)
        del x
        try: test(x, None, 1541)
        except NameError: test(None, None, 1542)
    a_use_b_loc()
    def a_use_b_ncap():
        try: test(x, None, 1545)
        except NameError: test(None, None, 1546)
        [x := _ for _ in ["a_use_b_ncap.x"]]
        try: test(x, 'a_use_b_ncap.x', 1548)
        except NameError: test(None, 'a_use_b_ncap.x', 1549)
        def a_use_b_ncap_delfunc():
            nonlocal x; del x
        a_use_b_ncap_delfunc()
        try: test(x, None, 1553)
        except NameError: test(None, None, 1554)
        x = "a_use_b_ncap.x"
        try: test(x, 'a_use_b_ncap.x', 1556)
        except NameError: test(None, 'a_use_b_ncap.x', 1557)
        del x
        try: test(x, None, 1559)
        except NameError: test(None, None, 1560)
    a_use_b_ncap()
a_use()
def a_anno():
    x: str
    try: test(x, None, 1565)
    except NameError: test(None, None, 1566)
    class a_anno_B:
        pass
    class a_anno_B_use:
        try: test(x, None, 1570)
        except NameError: test(None, None, 1571)
    class a_anno_B_anno:
        x: str
        try: test(x, None, 1574)
        except NameError: test(None, None, 1575)
    class a_anno_B_nloc:
        nonlocal x
        try: test(x, None, 1578)
        except NameError: test(None, None, 1579)
        def a_anno_B_nloc_setfunc():
            nonlocal x; x = "a_anno.x"
        a_anno_B_nloc_setfunc()
        try: test(x, 'a_anno.x', 1583)
        except NameError: test(None, 'a_anno.x', 1584)
        def a_anno_B_nloc_delfunc():
            nonlocal x; del x
        a_anno_B_nloc_delfunc()
        try: test(x, None, 1588)
        except NameError: test(None, None, 1589)
        x = "a_anno.x"
        try: test(x, 'a_anno.x', 1591)
        except NameError: test(None, 'a_anno.x', 1592)
        del x
        try: test(x, None, 1594)
        except NameError: test(None, None, 1595)
    class a_anno_B_glob:
        global x
        try: test(x, None, 1598)
        except NameError: test(None, None, 1599)
        def a_anno_B_glob_setfunc():
            global x; x = "x"
        a_anno_B_glob_setfunc()
        try: test(x, 'x', 1603)
        except NameError: test(None, 'x', 1604)
        def a_anno_B_glob_delfunc():
            global x; del x
        a_anno_B_glob_delfunc()
        try: test(x, None, 1608)
        except NameError: test(None, None, 1609)
        x = "x"
        try: test(x, 'x', 1611)
        except NameError: test(None, 'x', 1612)
        del x
        try: test(x, None, 1614)
        except NameError: test(None, None, 1615)
    class a_anno_B_loc:
        try: test(x, None, 1617)
        except NameError: test(None, None, 1618)
        def a_anno_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_anno_B_loc.x"
        a_anno_B_loc_setfunc()
        try: test(x, 'a_anno_B_loc.x', 1622)
        except NameError: test(None, 'a_anno_B_loc.x', 1623)
        def a_anno_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_anno_B_loc_delfunc()
        try: test(x, None, 1627)
        except NameError: test(None, None, 1628)
        x = "a_anno_B_loc.x"
        try: test(x, 'a_anno_B_loc.x', 1630)
        except NameError: test(None, 'a_anno_B_loc.x', 1631)
        del x
        try: test(x, None, 1633)
        except NameError: test(None, None, 1634)
    class a_anno_B_ncap:
        try: test(x, None, 1636)
        except NameError: test(None, None, 1637)
        def a_anno_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_anno_B_ncap.x"
        a_anno_B_ncap_setfunc()
        try: test(x, 'a_anno_B_ncap.x', 1641)
        except NameError: test(None, 'a_anno_B_ncap.x', 1642)
        def a_anno_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_anno_B_ncap_delfunc()
        try: test(x, None, 1646)
        except NameError: test(None, None, 1647)
        x = "a_anno_B_ncap.x"
        try: test(x, 'a_anno_B_ncap.x', 1649)
        except NameError: test(None, 'a_anno_B_ncap.x', 1650)
        del x
        try: test(x, None, 1652)
        except NameError: test(None, None, 1653)
    def a_anno_b():
        pass
    a_anno_b()
    def a_anno_b_use():
        try: test(x, None, 1658)
        except NameError: test(None, None, 1659)
    a_anno_b_use()
    def a_anno_b_anno():
        x: str
        try: test(x, None, 1663)
        except NameError: test(None, None, 1664)
    a_anno_b_anno()
    def a_anno_b_nloc():
        nonlocal x
        try: test(x, None, 1668)
        except NameError: test(None, None, 1669)
        [x := _ for _ in ["a_anno.x"]]
        try: test(x, 'a_anno.x', 1671)
        except NameError: test(None, 'a_anno.x', 1672)
        def a_anno_b_nloc_delfunc():
            nonlocal x; del x
        a_anno_b_nloc_delfunc()
        try: test(x, None, 1676)
        except NameError: test(None, None, 1677)
        x = "a_anno.x"
        try: test(x, 'a_anno.x', 1679)
        except NameError: test(None, 'a_anno.x', 1680)
        del x
        try: test(x, None, 1682)
        except NameError: test(None, None, 1683)
    a_anno_b_nloc()
    def a_anno_b_glob():
        global x
        try: test(x, None, 1687)
        except NameError: test(None, None, 1688)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1690)
        except NameError: test(None, 'x', 1691)
        def a_anno_b_glob_delfunc():
            global x; del x
        a_anno_b_glob_delfunc()
        try: test(x, None, 1695)
        except NameError: test(None, None, 1696)
        x = "x"
        try: test(x, 'x', 1698)
        except NameError: test(None, 'x', 1699)
        del x
        try: test(x, None, 1701)
        except NameError: test(None, None, 1702)
    a_anno_b_glob()
    def a_anno_b_loc():
        try: test(x, None, 1705)
        except NameError: test(None, None, 1706)
        [x := _ for _ in ["a_anno_b_loc.x"]]
        try: test(x, 'a_anno_b_loc.x', 1708)
        except NameError: test(None, 'a_anno_b_loc.x', 1709)
        def a_anno_b_loc_delfunc():
            nonlocal x; del x
        a_anno_b_loc_delfunc()
        try: test(x, None, 1713)
        except NameError: test(None, None, 1714)
        x = "a_anno_b_loc.x"
        try: test(x, 'a_anno_b_loc.x', 1716)
        except NameError: test(None, 'a_anno_b_loc.x', 1717)
        del x
        try: test(x, None, 1719)
        except NameError: test(None, None, 1720)
    a_anno_b_loc()
    def a_anno_b_ncap():
        try: test(x, None, 1723)
        except NameError: test(None, None, 1724)
        [x := _ for _ in ["a_anno_b_ncap.x"]]
        try: test(x, 'a_anno_b_ncap.x', 1726)
        except NameError: test(None, 'a_anno_b_ncap.x', 1727)
        def a_anno_b_ncap_delfunc():
            nonlocal x; del x
        a_anno_b_ncap_delfunc()
        try: test(x, None, 1731)
        except NameError: test(None, None, 1732)
        x = "a_anno_b_ncap.x"
        try: test(x, 'a_anno_b_ncap.x', 1734)
        except NameError: test(None, 'a_anno_b_ncap.x', 1735)
        del x
        try: test(x, None, 1737)
        except NameError: test(None, None, 1738)
    a_anno_b_ncap()
a_anno()
def a_nloc():
    # No enclosed binding exists.
    try: compile("nonlocal x", "<string>", "exec")
    except SyntaxError: test(None, None, 1744)
    else: error("Enclosed binding exists", 1745)
a_nloc()
def a_glob():
    global x
    try: test(x, None, 1749)
    except NameError: test(None, None, 1750)
    class a_glob_B:
        pass
    class a_glob_B_use:
        try: test(x, None, 1754)
        except NameError: test(None, None, 1755)
    class a_glob_B_anno:
        x: str
        try: test(x, None, 1758)
        except NameError: test(None, None, 1759)
    class a_glob_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1763)
        else: error("Enclosed binding exists", 1764)
    class a_glob_B_glob:
        global x
        try: test(x, None, 1767)
        except NameError: test(None, None, 1768)
        def a_glob_B_glob_setfunc():
            global x; x = "x"
        a_glob_B_glob_setfunc()
        try: test(x, 'x', 1772)
        except NameError: test(None, 'x', 1773)
        def a_glob_B_glob_delfunc():
            global x; del x
        a_glob_B_glob_delfunc()
        try: test(x, None, 1777)
        except NameError: test(None, None, 1778)
        x = "x"
        try: test(x, 'x', 1780)
        except NameError: test(None, 'x', 1781)
        del x
        try: test(x, None, 1783)
        except NameError: test(None, None, 1784)
    class a_glob_B_loc:
        try: test(x, None, 1786)
        except NameError: test(None, None, 1787)
        def a_glob_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_glob_B_loc.x"
        a_glob_B_loc_setfunc()
        try: test(x, 'a_glob_B_loc.x', 1791)
        except NameError: test(None, 'a_glob_B_loc.x', 1792)
        def a_glob_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_glob_B_loc_delfunc()
        try: test(x, None, 1796)
        except NameError: test(None, None, 1797)
        x = "a_glob_B_loc.x"
        try: test(x, 'a_glob_B_loc.x', 1799)
        except NameError: test(None, 'a_glob_B_loc.x', 1800)
        del x
        try: test(x, None, 1802)
        except NameError: test(None, None, 1803)
    class a_glob_B_ncap:
        try: test(x, None, 1805)
        except NameError: test(None, None, 1806)
        def a_glob_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_glob_B_ncap.x"
        a_glob_B_ncap_setfunc()
        try: test(x, 'a_glob_B_ncap.x', 1810)
        except NameError: test(None, 'a_glob_B_ncap.x', 1811)
        def a_glob_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_glob_B_ncap_delfunc()
        try: test(x, None, 1815)
        except NameError: test(None, None, 1816)
        x = "a_glob_B_ncap.x"
        try: test(x, 'a_glob_B_ncap.x', 1818)
        except NameError: test(None, 'a_glob_B_ncap.x', 1819)
        del x
        try: test(x, None, 1821)
        except NameError: test(None, None, 1822)
    def a_glob_b():
        pass
    a_glob_b()
    def a_glob_b_use():
        try: test(x, None, 1827)
        except NameError: test(None, None, 1828)
    a_glob_b_use()
    def a_glob_b_anno():
        x: str
        try: test(x, None, 1832)
        except NameError: test(None, None, 1833)
    a_glob_b_anno()
    def a_glob_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1838)
        else: error("Enclosed binding exists", 1839)
    a_glob_b_nloc()
    def a_glob_b_glob():
        global x
        try: test(x, None, 1843)
        except NameError: test(None, None, 1844)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 1846)
        except NameError: test(None, 'x', 1847)
        def a_glob_b_glob_delfunc():
            global x; del x
        a_glob_b_glob_delfunc()
        try: test(x, None, 1851)
        except NameError: test(None, None, 1852)
        x = "x"
        try: test(x, 'x', 1854)
        except NameError: test(None, 'x', 1855)
        del x
        try: test(x, None, 1857)
        except NameError: test(None, None, 1858)
    a_glob_b_glob()
    def a_glob_b_loc():
        try: test(x, None, 1861)
        except NameError: test(None, None, 1862)
        [x := _ for _ in ["a_glob_b_loc.x"]]
        try: test(x, 'a_glob_b_loc.x', 1864)
        except NameError: test(None, 'a_glob_b_loc.x', 1865)
        def a_glob_b_loc_delfunc():
            nonlocal x; del x
        a_glob_b_loc_delfunc()
        try: test(x, None, 1869)
        except NameError: test(None, None, 1870)
        x = "a_glob_b_loc.x"
        try: test(x, 'a_glob_b_loc.x', 1872)
        except NameError: test(None, 'a_glob_b_loc.x', 1873)
        del x
        try: test(x, None, 1875)
        except NameError: test(None, None, 1876)
    a_glob_b_loc()
    def a_glob_b_ncap():
        try: test(x, None, 1879)
        except NameError: test(None, None, 1880)
        [x := _ for _ in ["a_glob_b_ncap.x"]]
        try: test(x, 'a_glob_b_ncap.x', 1882)
        except NameError: test(None, 'a_glob_b_ncap.x', 1883)
        def a_glob_b_ncap_delfunc():
            nonlocal x; del x
        a_glob_b_ncap_delfunc()
        try: test(x, None, 1887)
        except NameError: test(None, None, 1888)
        x = "a_glob_b_ncap.x"
        try: test(x, 'a_glob_b_ncap.x', 1890)
        except NameError: test(None, 'a_glob_b_ncap.x', 1891)
        del x
        try: test(x, None, 1893)
        except NameError: test(None, None, 1894)
    a_glob_b_ncap()
    [x := _ for _ in ["x"]]
    try: test(x, 'x', 1897)
    except NameError: test(None, 'x', 1898)
    def a_glob_delfunc():
        global x; del x
    a_glob_delfunc()
    try: test(x, None, 1902)
    except NameError: test(None, None, 1903)
    x = "x"
    try: test(x, 'x', 1905)
    except NameError: test(None, 'x', 1906)
    class a_glob_B2:
        pass
    class a_glob_B2_use:
        try: test(x, 'x', 1910)
        except NameError: test(None, 'x', 1911)
    class a_glob_B2_anno:
        x: str
        try: test(x, 'x', 1914)
        except NameError: test(None, 'x', 1915)
    class a_glob_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1919)
        else: error("Enclosed binding exists", 1920)
    class a_glob_B2_glob:
        global x
        try: test(x, 'x', 1923)
        except NameError: test(None, 'x', 1924)
        del x
        try: test(x, None, 1926)
        except NameError: test(None, None, 1927)
        def a_glob_B2_glob_setfunc():
            global x; x = "x"
        a_glob_B2_glob_setfunc()
        try: test(x, 'x', 1931)
        except NameError: test(None, 'x', 1932)
        def a_glob_B2_glob_delfunc():
            global x; del x
        a_glob_B2_glob_delfunc()
        try: test(x, None, 1936)
        except NameError: test(None, None, 1937)
        x = "x"
        try: test(x, 'x', 1939)
        except NameError: test(None, 'x', 1940)
    class a_glob_B2_loc:
        try: test(x, 'x', 1942)
        except NameError: test(None, 'x', 1943)
        def a_glob_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_glob_B2_loc.x"
        a_glob_B2_loc_setfunc()
        try: test(x, 'a_glob_B2_loc.x', 1947)
        except NameError: test(None, 'a_glob_B2_loc.x', 1948)
        def a_glob_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_glob_B2_loc_delfunc()
        try: test(x, 'x', 1952)
        except NameError: test(None, 'x', 1953)
        x = "a_glob_B2_loc.x"
        try: test(x, 'a_glob_B2_loc.x', 1955)
        except NameError: test(None, 'a_glob_B2_loc.x', 1956)
        del x
        try: test(x, 'x', 1958)
        except NameError: test(None, 'x', 1959)
    class a_glob_B2_ncap:
        try: test(x, 'x', 1961)
        except NameError: test(None, 'x', 1962)
        def a_glob_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_glob_B2_ncap.x"
        a_glob_B2_ncap_setfunc()
        try: test(x, 'a_glob_B2_ncap.x', 1966)
        except NameError: test(None, 'a_glob_B2_ncap.x', 1967)
        def a_glob_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_glob_B2_ncap_delfunc()
        try: test(x, 'x', 1971)
        except NameError: test(None, 'x', 1972)
        x = "a_glob_B2_ncap.x"
        try: test(x, 'a_glob_B2_ncap.x', 1974)
        except NameError: test(None, 'a_glob_B2_ncap.x', 1975)
        del x
        try: test(x, 'x', 1977)
        except NameError: test(None, 'x', 1978)
    def a_glob_b2():
        pass
    a_glob_b2()
    def a_glob_b2_use():
        try: test(x, 'x', 1983)
        except NameError: test(None, 'x', 1984)
    a_glob_b2_use()
    def a_glob_b2_anno():
        x: str
        try: test(x, None, 1988)
        except NameError: test(None, None, 1989)
    a_glob_b2_anno()
    def a_glob_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 1994)
        else: error("Enclosed binding exists", 1995)
    a_glob_b2_nloc()
    def a_glob_b2_glob():
        global x
        try: test(x, 'x', 1999)
        except NameError: test(None, 'x', 2000)
        del x
        try: test(x, None, 2002)
        except NameError: test(None, None, 2003)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2005)
        except NameError: test(None, 'x', 2006)
        def a_glob_b2_glob_delfunc():
            global x; del x
        a_glob_b2_glob_delfunc()
        try: test(x, None, 2010)
        except NameError: test(None, None, 2011)
        x = "x"
        try: test(x, 'x', 2013)
        except NameError: test(None, 'x', 2014)
    a_glob_b2_glob()
    def a_glob_b2_loc():
        try: test(x, None, 2017)
        except NameError: test(None, None, 2018)
        [x := _ for _ in ["a_glob_b2_loc.x"]]
        try: test(x, 'a_glob_b2_loc.x', 2020)
        except NameError: test(None, 'a_glob_b2_loc.x', 2021)
        def a_glob_b2_loc_delfunc():
            nonlocal x; del x
        a_glob_b2_loc_delfunc()
        try: test(x, None, 2025)
        except NameError: test(None, None, 2026)
        x = "a_glob_b2_loc.x"
        try: test(x, 'a_glob_b2_loc.x', 2028)
        except NameError: test(None, 'a_glob_b2_loc.x', 2029)
        del x
        try: test(x, None, 2031)
        except NameError: test(None, None, 2032)
    a_glob_b2_loc()
    def a_glob_b2_ncap():
        try: test(x, None, 2035)
        except NameError: test(None, None, 2036)
        [x := _ for _ in ["a_glob_b2_ncap.x"]]
        try: test(x, 'a_glob_b2_ncap.x', 2038)
        except NameError: test(None, 'a_glob_b2_ncap.x', 2039)
        def a_glob_b2_ncap_delfunc():
            nonlocal x; del x
        a_glob_b2_ncap_delfunc()
        try: test(x, None, 2043)
        except NameError: test(None, None, 2044)
        x = "a_glob_b2_ncap.x"
        try: test(x, 'a_glob_b2_ncap.x', 2046)
        except NameError: test(None, 'a_glob_b2_ncap.x', 2047)
        del x
        try: test(x, None, 2049)
        except NameError: test(None, None, 2050)
    a_glob_b2_ncap()
    del x
    try: test(x, None, 2053)
    except NameError: test(None, None, 2054)
a_glob()
def a_loc():
    try: test(x, None, 2057)
    except NameError: test(None, None, 2058)
    class a_loc_B:
        pass
    class a_loc_B_use:
        try: test(x, None, 2062)
        except NameError: test(None, None, 2063)
    class a_loc_B_anno:
        x: str
        try: test(x, None, 2066)
        except NameError: test(None, None, 2067)
    class a_loc_B_nloc:
        nonlocal x
        try: test(x, None, 2070)
        except NameError: test(None, None, 2071)
        def a_loc_B_nloc_setfunc():
            nonlocal x; x = "a_loc.x"
        a_loc_B_nloc_setfunc()
        try: test(x, 'a_loc.x', 2075)
        except NameError: test(None, 'a_loc.x', 2076)
        def a_loc_B_nloc_delfunc():
            nonlocal x; del x
        a_loc_B_nloc_delfunc()
        try: test(x, None, 2080)
        except NameError: test(None, None, 2081)
        x = "a_loc.x"
        try: test(x, 'a_loc.x', 2083)
        except NameError: test(None, 'a_loc.x', 2084)
        del x
        try: test(x, None, 2086)
        except NameError: test(None, None, 2087)
    class a_loc_B_glob:
        global x
        try: test(x, None, 2090)
        except NameError: test(None, None, 2091)
        def a_loc_B_glob_setfunc():
            global x; x = "x"
        a_loc_B_glob_setfunc()
        try: test(x, 'x', 2095)
        except NameError: test(None, 'x', 2096)
        def a_loc_B_glob_delfunc():
            global x; del x
        a_loc_B_glob_delfunc()
        try: test(x, None, 2100)
        except NameError: test(None, None, 2101)
        x = "x"
        try: test(x, 'x', 2103)
        except NameError: test(None, 'x', 2104)
        del x
        try: test(x, None, 2106)
        except NameError: test(None, None, 2107)
    class a_loc_B_loc:
        try: test(x, None, 2109)
        except NameError: test(None, None, 2110)
        def a_loc_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_loc_B_loc.x"
        a_loc_B_loc_setfunc()
        try: test(x, 'a_loc_B_loc.x', 2114)
        except NameError: test(None, 'a_loc_B_loc.x', 2115)
        def a_loc_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_loc_B_loc_delfunc()
        try: test(x, None, 2119)
        except NameError: test(None, None, 2120)
        x = "a_loc_B_loc.x"
        try: test(x, 'a_loc_B_loc.x', 2122)
        except NameError: test(None, 'a_loc_B_loc.x', 2123)
        del x
        try: test(x, None, 2125)
        except NameError: test(None, None, 2126)
    class a_loc_B_ncap:
        try: test(x, None, 2128)
        except NameError: test(None, None, 2129)
        def a_loc_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_loc_B_ncap.x"
        a_loc_B_ncap_setfunc()
        try: test(x, 'a_loc_B_ncap.x', 2133)
        except NameError: test(None, 'a_loc_B_ncap.x', 2134)
        def a_loc_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_loc_B_ncap_delfunc()
        try: test(x, None, 2138)
        except NameError: test(None, None, 2139)
        x = "a_loc_B_ncap.x"
        try: test(x, 'a_loc_B_ncap.x', 2141)
        except NameError: test(None, 'a_loc_B_ncap.x', 2142)
        del x
        try: test(x, None, 2144)
        except NameError: test(None, None, 2145)
    def a_loc_b():
        pass
    a_loc_b()
    def a_loc_b_use():
        try: test(x, None, 2150)
        except NameError: test(None, None, 2151)
    a_loc_b_use()
    def a_loc_b_anno():
        x: str
        try: test(x, None, 2155)
        except NameError: test(None, None, 2156)
    a_loc_b_anno()
    def a_loc_b_nloc():
        nonlocal x
        try: test(x, None, 2160)
        except NameError: test(None, None, 2161)
        [x := _ for _ in ["a_loc.x"]]
        try: test(x, 'a_loc.x', 2163)
        except NameError: test(None, 'a_loc.x', 2164)
        def a_loc_b_nloc_delfunc():
            nonlocal x; del x
        a_loc_b_nloc_delfunc()
        try: test(x, None, 2168)
        except NameError: test(None, None, 2169)
        x = "a_loc.x"
        try: test(x, 'a_loc.x', 2171)
        except NameError: test(None, 'a_loc.x', 2172)
        del x
        try: test(x, None, 2174)
        except NameError: test(None, None, 2175)
    a_loc_b_nloc()
    def a_loc_b_glob():
        global x
        try: test(x, None, 2179)
        except NameError: test(None, None, 2180)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2182)
        except NameError: test(None, 'x', 2183)
        def a_loc_b_glob_delfunc():
            global x; del x
        a_loc_b_glob_delfunc()
        try: test(x, None, 2187)
        except NameError: test(None, None, 2188)
        x = "x"
        try: test(x, 'x', 2190)
        except NameError: test(None, 'x', 2191)
        del x
        try: test(x, None, 2193)
        except NameError: test(None, None, 2194)
    a_loc_b_glob()
    def a_loc_b_loc():
        try: test(x, None, 2197)
        except NameError: test(None, None, 2198)
        [x := _ for _ in ["a_loc_b_loc.x"]]
        try: test(x, 'a_loc_b_loc.x', 2200)
        except NameError: test(None, 'a_loc_b_loc.x', 2201)
        def a_loc_b_loc_delfunc():
            nonlocal x; del x
        a_loc_b_loc_delfunc()
        try: test(x, None, 2205)
        except NameError: test(None, None, 2206)
        x = "a_loc_b_loc.x"
        try: test(x, 'a_loc_b_loc.x', 2208)
        except NameError: test(None, 'a_loc_b_loc.x', 2209)
        del x
        try: test(x, None, 2211)
        except NameError: test(None, None, 2212)
    a_loc_b_loc()
    def a_loc_b_ncap():
        try: test(x, None, 2215)
        except NameError: test(None, None, 2216)
        [x := _ for _ in ["a_loc_b_ncap.x"]]
        try: test(x, 'a_loc_b_ncap.x', 2218)
        except NameError: test(None, 'a_loc_b_ncap.x', 2219)
        def a_loc_b_ncap_delfunc():
            nonlocal x; del x
        a_loc_b_ncap_delfunc()
        try: test(x, None, 2223)
        except NameError: test(None, None, 2224)
        x = "a_loc_b_ncap.x"
        try: test(x, 'a_loc_b_ncap.x', 2226)
        except NameError: test(None, 'a_loc_b_ncap.x', 2227)
        del x
        try: test(x, None, 2229)
        except NameError: test(None, None, 2230)
    a_loc_b_ncap()
    [x := _ for _ in ["a_loc.x"]]
    try: test(x, 'a_loc.x', 2233)
    except NameError: test(None, 'a_loc.x', 2234)
    def a_loc_delfunc():
        nonlocal x; del x
    a_loc_delfunc()
    try: test(x, None, 2238)
    except NameError: test(None, None, 2239)
    x = "a_loc.x"
    try: test(x, 'a_loc.x', 2241)
    except NameError: test(None, 'a_loc.x', 2242)
    class a_loc_B2:
        pass
    class a_loc_B2_use:
        try: test(x, 'a_loc.x', 2246)
        except NameError: test(None, 'a_loc.x', 2247)
    class a_loc_B2_anno:
        x: str
        try: test(x, None, 2250)
        except NameError: test(None, None, 2251)
    class a_loc_B2_nloc:
        nonlocal x
        try: test(x, 'a_loc.x', 2254)
        except NameError: test(None, 'a_loc.x', 2255)
        del x
        try: test(x, None, 2257)
        except NameError: test(None, None, 2258)
        def a_loc_B2_nloc_setfunc():
            nonlocal x; x = "a_loc.x"
        a_loc_B2_nloc_setfunc()
        try: test(x, 'a_loc.x', 2262)
        except NameError: test(None, 'a_loc.x', 2263)
        def a_loc_B2_nloc_delfunc():
            nonlocal x; del x
        a_loc_B2_nloc_delfunc()
        try: test(x, None, 2267)
        except NameError: test(None, None, 2268)
        x = "a_loc.x"
        try: test(x, 'a_loc.x', 2270)
        except NameError: test(None, 'a_loc.x', 2271)
    class a_loc_B2_glob:
        global x
        try: test(x, None, 2274)
        except NameError: test(None, None, 2275)
        def a_loc_B2_glob_setfunc():
            global x; x = "x"
        a_loc_B2_glob_setfunc()
        try: test(x, 'x', 2279)
        except NameError: test(None, 'x', 2280)
        def a_loc_B2_glob_delfunc():
            global x; del x
        a_loc_B2_glob_delfunc()
        try: test(x, None, 2284)
        except NameError: test(None, None, 2285)
        x = "x"
        try: test(x, 'x', 2287)
        except NameError: test(None, 'x', 2288)
        del x
        try: test(x, None, 2290)
        except NameError: test(None, None, 2291)
    class a_loc_B2_loc:
        try: test(x, None, 2293)
        except NameError: test(None, None, 2294)
        def a_loc_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_loc_B2_loc.x"
        a_loc_B2_loc_setfunc()
        try: test(x, 'a_loc_B2_loc.x', 2298)
        except NameError: test(None, 'a_loc_B2_loc.x', 2299)
        def a_loc_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_loc_B2_loc_delfunc()
        try: test(x, None, 2303)
        except NameError: test(None, None, 2304)
        x = "a_loc_B2_loc.x"
        try: test(x, 'a_loc_B2_loc.x', 2306)
        except NameError: test(None, 'a_loc_B2_loc.x', 2307)
        del x
        try: test(x, None, 2309)
        except NameError: test(None, None, 2310)
    class a_loc_B2_ncap:
        try: test(x, None, 2312)
        except NameError: test(None, None, 2313)
        def a_loc_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_loc_B2_ncap.x"
        a_loc_B2_ncap_setfunc()
        try: test(x, 'a_loc_B2_ncap.x', 2317)
        except NameError: test(None, 'a_loc_B2_ncap.x', 2318)
        def a_loc_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_loc_B2_ncap_delfunc()
        try: test(x, None, 2322)
        except NameError: test(None, None, 2323)
        x = "a_loc_B2_ncap.x"
        try: test(x, 'a_loc_B2_ncap.x', 2325)
        except NameError: test(None, 'a_loc_B2_ncap.x', 2326)
        del x
        try: test(x, None, 2328)
        except NameError: test(None, None, 2329)
    def a_loc_b2():
        pass
    a_loc_b2()
    def a_loc_b2_use():
        try: test(x, 'a_loc.x', 2334)
        except NameError: test(None, 'a_loc.x', 2335)
    a_loc_b2_use()
    def a_loc_b2_anno():
        x: str
        try: test(x, None, 2339)
        except NameError: test(None, None, 2340)
    a_loc_b2_anno()
    def a_loc_b2_nloc():
        nonlocal x
        try: test(x, 'a_loc.x', 2344)
        except NameError: test(None, 'a_loc.x', 2345)
        del x
        try: test(x, None, 2347)
        except NameError: test(None, None, 2348)
        [x := _ for _ in ["a_loc.x"]]
        try: test(x, 'a_loc.x', 2350)
        except NameError: test(None, 'a_loc.x', 2351)
        def a_loc_b2_nloc_delfunc():
            nonlocal x; del x
        a_loc_b2_nloc_delfunc()
        try: test(x, None, 2355)
        except NameError: test(None, None, 2356)
        x = "a_loc.x"
        try: test(x, 'a_loc.x', 2358)
        except NameError: test(None, 'a_loc.x', 2359)
    a_loc_b2_nloc()
    def a_loc_b2_glob():
        global x
        try: test(x, None, 2363)
        except NameError: test(None, None, 2364)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2366)
        except NameError: test(None, 'x', 2367)
        def a_loc_b2_glob_delfunc():
            global x; del x
        a_loc_b2_glob_delfunc()
        try: test(x, None, 2371)
        except NameError: test(None, None, 2372)
        x = "x"
        try: test(x, 'x', 2374)
        except NameError: test(None, 'x', 2375)
        del x
        try: test(x, None, 2377)
        except NameError: test(None, None, 2378)
    a_loc_b2_glob()
    def a_loc_b2_loc():
        try: test(x, None, 2381)
        except NameError: test(None, None, 2382)
        [x := _ for _ in ["a_loc_b2_loc.x"]]
        try: test(x, 'a_loc_b2_loc.x', 2384)
        except NameError: test(None, 'a_loc_b2_loc.x', 2385)
        def a_loc_b2_loc_delfunc():
            nonlocal x; del x
        a_loc_b2_loc_delfunc()
        try: test(x, None, 2389)
        except NameError: test(None, None, 2390)
        x = "a_loc_b2_loc.x"
        try: test(x, 'a_loc_b2_loc.x', 2392)
        except NameError: test(None, 'a_loc_b2_loc.x', 2393)
        del x
        try: test(x, None, 2395)
        except NameError: test(None, None, 2396)
    a_loc_b2_loc()
    def a_loc_b2_ncap():
        try: test(x, None, 2399)
        except NameError: test(None, None, 2400)
        [x := _ for _ in ["a_loc_b2_ncap.x"]]
        try: test(x, 'a_loc_b2_ncap.x', 2402)
        except NameError: test(None, 'a_loc_b2_ncap.x', 2403)
        def a_loc_b2_ncap_delfunc():
            nonlocal x; del x
        a_loc_b2_ncap_delfunc()
        try: test(x, None, 2407)
        except NameError: test(None, None, 2408)
        x = "a_loc_b2_ncap.x"
        try: test(x, 'a_loc_b2_ncap.x', 2410)
        except NameError: test(None, 'a_loc_b2_ncap.x', 2411)
        del x
        try: test(x, None, 2413)
        except NameError: test(None, None, 2414)
    a_loc_b2_ncap()
    del x
    try: test(x, None, 2417)
    except NameError: test(None, None, 2418)
a_loc()
def a_ncap():
    try: test(x, None, 2421)
    except NameError: test(None, None, 2422)
    class a_ncap_B:
        pass
    class a_ncap_B_glob:
        global x
        try: test(x, None, 2427)
        except NameError: test(None, None, 2428)
        def a_ncap_B_glob_setfunc():
            global x; x = "x"
        a_ncap_B_glob_setfunc()
        try: test(x, 'x', 2432)
        except NameError: test(None, 'x', 2433)
        def a_ncap_B_glob_delfunc():
            global x; del x
        a_ncap_B_glob_delfunc()
        try: test(x, None, 2437)
        except NameError: test(None, None, 2438)
        x = "x"
        try: test(x, 'x', 2440)
        except NameError: test(None, 'x', 2441)
        del x
        try: test(x, None, 2443)
        except NameError: test(None, None, 2444)
    class a_ncap_B_loc:
        try: test(x, None, 2446)
        except NameError: test(None, None, 2447)
        def a_ncap_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_ncap_B_loc.x"
        a_ncap_B_loc_setfunc()
        try: test(x, 'a_ncap_B_loc.x', 2451)
        except NameError: test(None, 'a_ncap_B_loc.x', 2452)
        def a_ncap_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_ncap_B_loc_delfunc()
        try: test(x, None, 2456)
        except NameError: test(None, None, 2457)
        x = "a_ncap_B_loc.x"
        try: test(x, 'a_ncap_B_loc.x', 2459)
        except NameError: test(None, 'a_ncap_B_loc.x', 2460)
        del x
        try: test(x, None, 2462)
        except NameError: test(None, None, 2463)
    def a_ncap_b():
        pass
    a_ncap_b()
    def a_ncap_b_glob():
        global x
        try: test(x, None, 2469)
        except NameError: test(None, None, 2470)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2472)
        except NameError: test(None, 'x', 2473)
        def a_ncap_b_glob_delfunc():
            global x; del x
        a_ncap_b_glob_delfunc()
        try: test(x, None, 2477)
        except NameError: test(None, None, 2478)
        x = "x"
        try: test(x, 'x', 2480)
        except NameError: test(None, 'x', 2481)
        del x
        try: test(x, None, 2483)
        except NameError: test(None, None, 2484)
    a_ncap_b_glob()
    def a_ncap_b_loc():
        try: test(x, None, 2487)
        except NameError: test(None, None, 2488)
        [x := _ for _ in ["a_ncap_b_loc.x"]]
        try: test(x, 'a_ncap_b_loc.x', 2490)
        except NameError: test(None, 'a_ncap_b_loc.x', 2491)
        def a_ncap_b_loc_delfunc():
            nonlocal x; del x
        a_ncap_b_loc_delfunc()
        try: test(x, None, 2495)
        except NameError: test(None, None, 2496)
        x = "a_ncap_b_loc.x"
        try: test(x, 'a_ncap_b_loc.x', 2498)
        except NameError: test(None, 'a_ncap_b_loc.x', 2499)
        del x
        try: test(x, None, 2501)
        except NameError: test(None, None, 2502)
    a_ncap_b_loc()
    [x := _ for _ in ["a_ncap.x"]]
    try: test(x, 'a_ncap.x', 2505)
    except NameError: test(None, 'a_ncap.x', 2506)
    def a_ncap_delfunc():
        nonlocal x; del x
    a_ncap_delfunc()
    try: test(x, None, 2510)
    except NameError: test(None, None, 2511)
    x = "a_ncap.x"
    try: test(x, 'a_ncap.x', 2513)
    except NameError: test(None, 'a_ncap.x', 2514)
    class a_ncap_B2:
        pass
    class a_ncap_B2_glob:
        global x
        try: test(x, None, 2519)
        except NameError: test(None, None, 2520)
        def a_ncap_B2_glob_setfunc():
            global x; x = "x"
        a_ncap_B2_glob_setfunc()
        try: test(x, 'x', 2524)
        except NameError: test(None, 'x', 2525)
        def a_ncap_B2_glob_delfunc():
            global x; del x
        a_ncap_B2_glob_delfunc()
        try: test(x, None, 2529)
        except NameError: test(None, None, 2530)
        x = "x"
        try: test(x, 'x', 2532)
        except NameError: test(None, 'x', 2533)
        del x
        try: test(x, None, 2535)
        except NameError: test(None, None, 2536)
    class a_ncap_B2_loc:
        try: test(x, None, 2538)
        except NameError: test(None, None, 2539)
        def a_ncap_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a_ncap_B2_loc.x"
        a_ncap_B2_loc_setfunc()
        try: test(x, 'a_ncap_B2_loc.x', 2543)
        except NameError: test(None, 'a_ncap_B2_loc.x', 2544)
        def a_ncap_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a_ncap_B2_loc_delfunc()
        try: test(x, None, 2548)
        except NameError: test(None, None, 2549)
        x = "a_ncap_B2_loc.x"
        try: test(x, 'a_ncap_B2_loc.x', 2551)
        except NameError: test(None, 'a_ncap_B2_loc.x', 2552)
        del x
        try: test(x, None, 2554)
        except NameError: test(None, None, 2555)
    def a_ncap_b2():
        pass
    a_ncap_b2()
    def a_ncap_b2_glob():
        global x
        try: test(x, None, 2561)
        except NameError: test(None, None, 2562)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2564)
        except NameError: test(None, 'x', 2565)
        def a_ncap_b2_glob_delfunc():
            global x; del x
        a_ncap_b2_glob_delfunc()
        try: test(x, None, 2569)
        except NameError: test(None, None, 2570)
        x = "x"
        try: test(x, 'x', 2572)
        except NameError: test(None, 'x', 2573)
        del x
        try: test(x, None, 2575)
        except NameError: test(None, None, 2576)
    a_ncap_b2_glob()
    def a_ncap_b2_loc():
        try: test(x, None, 2579)
        except NameError: test(None, None, 2580)
        [x := _ for _ in ["a_ncap_b2_loc.x"]]
        try: test(x, 'a_ncap_b2_loc.x', 2582)
        except NameError: test(None, 'a_ncap_b2_loc.x', 2583)
        def a_ncap_b2_loc_delfunc():
            nonlocal x; del x
        a_ncap_b2_loc_delfunc()
        try: test(x, None, 2587)
        except NameError: test(None, None, 2588)
        x = "a_ncap_b2_loc.x"
        try: test(x, 'a_ncap_b2_loc.x', 2590)
        except NameError: test(None, 'a_ncap_b2_loc.x', 2591)
        del x
        try: test(x, None, 2593)
        except NameError: test(None, None, 2594)
    a_ncap_b2_loc()
    del x
    try: test(x, None, 2597)
    except NameError: test(None, None, 2598)
a_ncap()
[x := _ for _ in ["x"]]
try: test(x, 'x', 2601)
except NameError: test(None, 'x', 2602)
def _delfunc():
    global x; del x
_delfunc()
try: test(x, None, 2606)
except NameError: test(None, None, 2607)
x = "x"
try: test(x, 'x', 2609)
except NameError: test(None, 'x', 2610)
class A2:
    class A2_B:
        pass
    class A2_B_use:
        try: test(x, 'x', 2615)
        except NameError: test(None, 'x', 2616)
    class A2_B_anno:
        x: str
        try: test(x, 'x', 2619)
        except NameError: test(None, 'x', 2620)
    class A2_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2624)
        else: error("Enclosed binding exists", 2625)
    class A2_B_glob:
        global x
        try: test(x, 'x', 2628)
        except NameError: test(None, 'x', 2629)
        del x
        try: test(x, None, 2631)
        except NameError: test(None, None, 2632)
        def A2_B_glob_setfunc():
            global x; x = "x"
        A2_B_glob_setfunc()
        try: test(x, 'x', 2636)
        except NameError: test(None, 'x', 2637)
        def A2_B_glob_delfunc():
            global x; del x
        A2_B_glob_delfunc()
        try: test(x, None, 2641)
        except NameError: test(None, None, 2642)
        x = "x"
        try: test(x, 'x', 2644)
        except NameError: test(None, 'x', 2645)
    class A2_B_loc:
        try: test(x, 'x', 2647)
        except NameError: test(None, 'x', 2648)
        def A2_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_B_loc.x"
        A2_B_loc_setfunc()
        try: test(x, 'A2_B_loc.x', 2652)
        except NameError: test(None, 'A2_B_loc.x', 2653)
        def A2_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_B_loc_delfunc()
        try: test(x, 'x', 2657)
        except NameError: test(None, 'x', 2658)
        x = "A2_B_loc.x"
        try: test(x, 'A2_B_loc.x', 2660)
        except NameError: test(None, 'A2_B_loc.x', 2661)
        del x
        try: test(x, 'x', 2663)
        except NameError: test(None, 'x', 2664)
    class A2_B_ncap:
        try: test(x, 'x', 2666)
        except NameError: test(None, 'x', 2667)
        def A2_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_B_ncap.x"
        A2_B_ncap_setfunc()
        try: test(x, 'A2_B_ncap.x', 2671)
        except NameError: test(None, 'A2_B_ncap.x', 2672)
        def A2_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_B_ncap_delfunc()
        try: test(x, 'x', 2676)
        except NameError: test(None, 'x', 2677)
        x = "A2_B_ncap.x"
        try: test(x, 'A2_B_ncap.x', 2679)
        except NameError: test(None, 'A2_B_ncap.x', 2680)
        del x
        try: test(x, 'x', 2682)
        except NameError: test(None, 'x', 2683)
    def A2_b():
        pass
    A2_b()
    def A2_b_use():
        try: test(x, 'x', 2688)
        except NameError: test(None, 'x', 2689)
    A2_b_use()
    def A2_b_anno():
        x: str
        try: test(x, None, 2693)
        except NameError: test(None, None, 2694)
    A2_b_anno()
    def A2_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2699)
        else: error("Enclosed binding exists", 2700)
    A2_b_nloc()
    def A2_b_glob():
        global x
        try: test(x, 'x', 2704)
        except NameError: test(None, 'x', 2705)
        del x
        try: test(x, None, 2707)
        except NameError: test(None, None, 2708)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2710)
        except NameError: test(None, 'x', 2711)
        def A2_b_glob_delfunc():
            global x; del x
        A2_b_glob_delfunc()
        try: test(x, None, 2715)
        except NameError: test(None, None, 2716)
        x = "x"
        try: test(x, 'x', 2718)
        except NameError: test(None, 'x', 2719)
    A2_b_glob()
    def A2_b_loc():
        try: test(x, None, 2722)
        except NameError: test(None, None, 2723)
        [x := _ for _ in ["A2_b_loc.x"]]
        try: test(x, 'A2_b_loc.x', 2725)
        except NameError: test(None, 'A2_b_loc.x', 2726)
        def A2_b_loc_delfunc():
            nonlocal x; del x
        A2_b_loc_delfunc()
        try: test(x, None, 2730)
        except NameError: test(None, None, 2731)
        x = "A2_b_loc.x"
        try: test(x, 'A2_b_loc.x', 2733)
        except NameError: test(None, 'A2_b_loc.x', 2734)
        del x
        try: test(x, None, 2736)
        except NameError: test(None, None, 2737)
    A2_b_loc()
    def A2_b_ncap():
        try: test(x, None, 2740)
        except NameError: test(None, None, 2741)
        [x := _ for _ in ["A2_b_ncap.x"]]
        try: test(x, 'A2_b_ncap.x', 2743)
        except NameError: test(None, 'A2_b_ncap.x', 2744)
        def A2_b_ncap_delfunc():
            nonlocal x; del x
        A2_b_ncap_delfunc()
        try: test(x, None, 2748)
        except NameError: test(None, None, 2749)
        x = "A2_b_ncap.x"
        try: test(x, 'A2_b_ncap.x', 2751)
        except NameError: test(None, 'A2_b_ncap.x', 2752)
        del x
        try: test(x, None, 2754)
        except NameError: test(None, None, 2755)
    A2_b_ncap()
class A2_use:
    try: test(x, 'x', 2758)
    except NameError: test(None, 'x', 2759)
    class A2_use_B:
        pass
    class A2_use_B_use:
        try: test(x, 'x', 2763)
        except NameError: test(None, 'x', 2764)
    class A2_use_B_anno:
        x: str
        try: test(x, 'x', 2767)
        except NameError: test(None, 'x', 2768)
    class A2_use_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2772)
        else: error("Enclosed binding exists", 2773)
    class A2_use_B_glob:
        global x
        try: test(x, 'x', 2776)
        except NameError: test(None, 'x', 2777)
        del x
        try: test(x, None, 2779)
        except NameError: test(None, None, 2780)
        def A2_use_B_glob_setfunc():
            global x; x = "x"
        A2_use_B_glob_setfunc()
        try: test(x, 'x', 2784)
        except NameError: test(None, 'x', 2785)
        def A2_use_B_glob_delfunc():
            global x; del x
        A2_use_B_glob_delfunc()
        try: test(x, None, 2789)
        except NameError: test(None, None, 2790)
        x = "x"
        try: test(x, 'x', 2792)
        except NameError: test(None, 'x', 2793)
    class A2_use_B_loc:
        try: test(x, 'x', 2795)
        except NameError: test(None, 'x', 2796)
        def A2_use_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_use_B_loc.x"
        A2_use_B_loc_setfunc()
        try: test(x, 'A2_use_B_loc.x', 2800)
        except NameError: test(None, 'A2_use_B_loc.x', 2801)
        def A2_use_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_use_B_loc_delfunc()
        try: test(x, 'x', 2805)
        except NameError: test(None, 'x', 2806)
        x = "A2_use_B_loc.x"
        try: test(x, 'A2_use_B_loc.x', 2808)
        except NameError: test(None, 'A2_use_B_loc.x', 2809)
        del x
        try: test(x, 'x', 2811)
        except NameError: test(None, 'x', 2812)
    class A2_use_B_ncap:
        try: test(x, 'x', 2814)
        except NameError: test(None, 'x', 2815)
        def A2_use_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_use_B_ncap.x"
        A2_use_B_ncap_setfunc()
        try: test(x, 'A2_use_B_ncap.x', 2819)
        except NameError: test(None, 'A2_use_B_ncap.x', 2820)
        def A2_use_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_use_B_ncap_delfunc()
        try: test(x, 'x', 2824)
        except NameError: test(None, 'x', 2825)
        x = "A2_use_B_ncap.x"
        try: test(x, 'A2_use_B_ncap.x', 2827)
        except NameError: test(None, 'A2_use_B_ncap.x', 2828)
        del x
        try: test(x, 'x', 2830)
        except NameError: test(None, 'x', 2831)
    def A2_use_b():
        pass
    A2_use_b()
    def A2_use_b_use():
        try: test(x, 'x', 2836)
        except NameError: test(None, 'x', 2837)
    A2_use_b_use()
    def A2_use_b_anno():
        x: str
        try: test(x, None, 2841)
        except NameError: test(None, None, 2842)
    A2_use_b_anno()
    def A2_use_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2847)
        else: error("Enclosed binding exists", 2848)
    A2_use_b_nloc()
    def A2_use_b_glob():
        global x
        try: test(x, 'x', 2852)
        except NameError: test(None, 'x', 2853)
        del x
        try: test(x, None, 2855)
        except NameError: test(None, None, 2856)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 2858)
        except NameError: test(None, 'x', 2859)
        def A2_use_b_glob_delfunc():
            global x; del x
        A2_use_b_glob_delfunc()
        try: test(x, None, 2863)
        except NameError: test(None, None, 2864)
        x = "x"
        try: test(x, 'x', 2866)
        except NameError: test(None, 'x', 2867)
    A2_use_b_glob()
    def A2_use_b_loc():
        try: test(x, None, 2870)
        except NameError: test(None, None, 2871)
        [x := _ for _ in ["A2_use_b_loc.x"]]
        try: test(x, 'A2_use_b_loc.x', 2873)
        except NameError: test(None, 'A2_use_b_loc.x', 2874)
        def A2_use_b_loc_delfunc():
            nonlocal x; del x
        A2_use_b_loc_delfunc()
        try: test(x, None, 2878)
        except NameError: test(None, None, 2879)
        x = "A2_use_b_loc.x"
        try: test(x, 'A2_use_b_loc.x', 2881)
        except NameError: test(None, 'A2_use_b_loc.x', 2882)
        del x
        try: test(x, None, 2884)
        except NameError: test(None, None, 2885)
    A2_use_b_loc()
    def A2_use_b_ncap():
        try: test(x, None, 2888)
        except NameError: test(None, None, 2889)
        [x := _ for _ in ["A2_use_b_ncap.x"]]
        try: test(x, 'A2_use_b_ncap.x', 2891)
        except NameError: test(None, 'A2_use_b_ncap.x', 2892)
        def A2_use_b_ncap_delfunc():
            nonlocal x; del x
        A2_use_b_ncap_delfunc()
        try: test(x, None, 2896)
        except NameError: test(None, None, 2897)
        x = "A2_use_b_ncap.x"
        try: test(x, 'A2_use_b_ncap.x', 2899)
        except NameError: test(None, 'A2_use_b_ncap.x', 2900)
        del x
        try: test(x, None, 2902)
        except NameError: test(None, None, 2903)
    A2_use_b_ncap()
class A2_anno:
    x: str
    try: test(x, 'x', 2907)
    except NameError: test(None, 'x', 2908)
    class A2_anno_B:
        pass
    class A2_anno_B_use:
        try: test(x, 'x', 2912)
        except NameError: test(None, 'x', 2913)
    class A2_anno_B_anno:
        x: str
        try: test(x, 'x', 2916)
        except NameError: test(None, 'x', 2917)
    class A2_anno_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2921)
        else: error("Enclosed binding exists", 2922)
    class A2_anno_B_glob:
        global x
        try: test(x, 'x', 2925)
        except NameError: test(None, 'x', 2926)
        del x
        try: test(x, None, 2928)
        except NameError: test(None, None, 2929)
        def A2_anno_B_glob_setfunc():
            global x; x = "x"
        A2_anno_B_glob_setfunc()
        try: test(x, 'x', 2933)
        except NameError: test(None, 'x', 2934)
        def A2_anno_B_glob_delfunc():
            global x; del x
        A2_anno_B_glob_delfunc()
        try: test(x, None, 2938)
        except NameError: test(None, None, 2939)
        x = "x"
        try: test(x, 'x', 2941)
        except NameError: test(None, 'x', 2942)
    class A2_anno_B_loc:
        try: test(x, 'x', 2944)
        except NameError: test(None, 'x', 2945)
        def A2_anno_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_anno_B_loc.x"
        A2_anno_B_loc_setfunc()
        try: test(x, 'A2_anno_B_loc.x', 2949)
        except NameError: test(None, 'A2_anno_B_loc.x', 2950)
        def A2_anno_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_anno_B_loc_delfunc()
        try: test(x, 'x', 2954)
        except NameError: test(None, 'x', 2955)
        x = "A2_anno_B_loc.x"
        try: test(x, 'A2_anno_B_loc.x', 2957)
        except NameError: test(None, 'A2_anno_B_loc.x', 2958)
        del x
        try: test(x, 'x', 2960)
        except NameError: test(None, 'x', 2961)
    class A2_anno_B_ncap:
        try: test(x, 'x', 2963)
        except NameError: test(None, 'x', 2964)
        def A2_anno_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_anno_B_ncap.x"
        A2_anno_B_ncap_setfunc()
        try: test(x, 'A2_anno_B_ncap.x', 2968)
        except NameError: test(None, 'A2_anno_B_ncap.x', 2969)
        def A2_anno_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_anno_B_ncap_delfunc()
        try: test(x, 'x', 2973)
        except NameError: test(None, 'x', 2974)
        x = "A2_anno_B_ncap.x"
        try: test(x, 'A2_anno_B_ncap.x', 2976)
        except NameError: test(None, 'A2_anno_B_ncap.x', 2977)
        del x
        try: test(x, 'x', 2979)
        except NameError: test(None, 'x', 2980)
    def A2_anno_b():
        pass
    A2_anno_b()
    def A2_anno_b_use():
        try: test(x, 'x', 2985)
        except NameError: test(None, 'x', 2986)
    A2_anno_b_use()
    def A2_anno_b_anno():
        x: str
        try: test(x, None, 2990)
        except NameError: test(None, None, 2991)
    A2_anno_b_anno()
    def A2_anno_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 2996)
        else: error("Enclosed binding exists", 2997)
    A2_anno_b_nloc()
    def A2_anno_b_glob():
        global x
        try: test(x, 'x', 3001)
        except NameError: test(None, 'x', 3002)
        del x
        try: test(x, None, 3004)
        except NameError: test(None, None, 3005)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3007)
        except NameError: test(None, 'x', 3008)
        def A2_anno_b_glob_delfunc():
            global x; del x
        A2_anno_b_glob_delfunc()
        try: test(x, None, 3012)
        except NameError: test(None, None, 3013)
        x = "x"
        try: test(x, 'x', 3015)
        except NameError: test(None, 'x', 3016)
    A2_anno_b_glob()
    def A2_anno_b_loc():
        try: test(x, None, 3019)
        except NameError: test(None, None, 3020)
        [x := _ for _ in ["A2_anno_b_loc.x"]]
        try: test(x, 'A2_anno_b_loc.x', 3022)
        except NameError: test(None, 'A2_anno_b_loc.x', 3023)
        def A2_anno_b_loc_delfunc():
            nonlocal x; del x
        A2_anno_b_loc_delfunc()
        try: test(x, None, 3027)
        except NameError: test(None, None, 3028)
        x = "A2_anno_b_loc.x"
        try: test(x, 'A2_anno_b_loc.x', 3030)
        except NameError: test(None, 'A2_anno_b_loc.x', 3031)
        del x
        try: test(x, None, 3033)
        except NameError: test(None, None, 3034)
    A2_anno_b_loc()
    def A2_anno_b_ncap():
        try: test(x, None, 3037)
        except NameError: test(None, None, 3038)
        [x := _ for _ in ["A2_anno_b_ncap.x"]]
        try: test(x, 'A2_anno_b_ncap.x', 3040)
        except NameError: test(None, 'A2_anno_b_ncap.x', 3041)
        def A2_anno_b_ncap_delfunc():
            nonlocal x; del x
        A2_anno_b_ncap_delfunc()
        try: test(x, None, 3045)
        except NameError: test(None, None, 3046)
        x = "A2_anno_b_ncap.x"
        try: test(x, 'A2_anno_b_ncap.x', 3048)
        except NameError: test(None, 'A2_anno_b_ncap.x', 3049)
        del x
        try: test(x, None, 3051)
        except NameError: test(None, None, 3052)
    A2_anno_b_ncap()
class A2_nloc:
    # No enclosed binding exists.
    try: compile("nonlocal x", "<string>", "exec")
    except SyntaxError: test(None, None, 3057)
    else: error("Enclosed binding exists", 3058)
class A2_glob:
    global x
    try: test(x, 'x', 3061)
    except NameError: test(None, 'x', 3062)
    class A2_glob_B:
        pass
    class A2_glob_B_use:
        try: test(x, 'x', 3066)
        except NameError: test(None, 'x', 3067)
    class A2_glob_B_anno:
        x: str
        try: test(x, 'x', 3070)
        except NameError: test(None, 'x', 3071)
    class A2_glob_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3075)
        else: error("Enclosed binding exists", 3076)
    class A2_glob_B_glob:
        global x
        try: test(x, 'x', 3079)
        except NameError: test(None, 'x', 3080)
        del x
        try: test(x, None, 3082)
        except NameError: test(None, None, 3083)
        def A2_glob_B_glob_setfunc():
            global x; x = "x"
        A2_glob_B_glob_setfunc()
        try: test(x, 'x', 3087)
        except NameError: test(None, 'x', 3088)
        def A2_glob_B_glob_delfunc():
            global x; del x
        A2_glob_B_glob_delfunc()
        try: test(x, None, 3092)
        except NameError: test(None, None, 3093)
        x = "x"
        try: test(x, 'x', 3095)
        except NameError: test(None, 'x', 3096)
    class A2_glob_B_loc:
        try: test(x, 'x', 3098)
        except NameError: test(None, 'x', 3099)
        def A2_glob_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_glob_B_loc.x"
        A2_glob_B_loc_setfunc()
        try: test(x, 'A2_glob_B_loc.x', 3103)
        except NameError: test(None, 'A2_glob_B_loc.x', 3104)
        def A2_glob_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_glob_B_loc_delfunc()
        try: test(x, 'x', 3108)
        except NameError: test(None, 'x', 3109)
        x = "A2_glob_B_loc.x"
        try: test(x, 'A2_glob_B_loc.x', 3111)
        except NameError: test(None, 'A2_glob_B_loc.x', 3112)
        del x
        try: test(x, 'x', 3114)
        except NameError: test(None, 'x', 3115)
    class A2_glob_B_ncap:
        try: test(x, 'x', 3117)
        except NameError: test(None, 'x', 3118)
        def A2_glob_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_glob_B_ncap.x"
        A2_glob_B_ncap_setfunc()
        try: test(x, 'A2_glob_B_ncap.x', 3122)
        except NameError: test(None, 'A2_glob_B_ncap.x', 3123)
        def A2_glob_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_glob_B_ncap_delfunc()
        try: test(x, 'x', 3127)
        except NameError: test(None, 'x', 3128)
        x = "A2_glob_B_ncap.x"
        try: test(x, 'A2_glob_B_ncap.x', 3130)
        except NameError: test(None, 'A2_glob_B_ncap.x', 3131)
        del x
        try: test(x, 'x', 3133)
        except NameError: test(None, 'x', 3134)
    def A2_glob_b():
        pass
    A2_glob_b()
    def A2_glob_b_use():
        try: test(x, 'x', 3139)
        except NameError: test(None, 'x', 3140)
    A2_glob_b_use()
    def A2_glob_b_anno():
        x: str
        try: test(x, None, 3144)
        except NameError: test(None, None, 3145)
    A2_glob_b_anno()
    def A2_glob_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3150)
        else: error("Enclosed binding exists", 3151)
    A2_glob_b_nloc()
    def A2_glob_b_glob():
        global x
        try: test(x, 'x', 3155)
        except NameError: test(None, 'x', 3156)
        del x
        try: test(x, None, 3158)
        except NameError: test(None, None, 3159)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3161)
        except NameError: test(None, 'x', 3162)
        def A2_glob_b_glob_delfunc():
            global x; del x
        A2_glob_b_glob_delfunc()
        try: test(x, None, 3166)
        except NameError: test(None, None, 3167)
        x = "x"
        try: test(x, 'x', 3169)
        except NameError: test(None, 'x', 3170)
    A2_glob_b_glob()
    def A2_glob_b_loc():
        try: test(x, None, 3173)
        except NameError: test(None, None, 3174)
        [x := _ for _ in ["A2_glob_b_loc.x"]]
        try: test(x, 'A2_glob_b_loc.x', 3176)
        except NameError: test(None, 'A2_glob_b_loc.x', 3177)
        def A2_glob_b_loc_delfunc():
            nonlocal x; del x
        A2_glob_b_loc_delfunc()
        try: test(x, None, 3181)
        except NameError: test(None, None, 3182)
        x = "A2_glob_b_loc.x"
        try: test(x, 'A2_glob_b_loc.x', 3184)
        except NameError: test(None, 'A2_glob_b_loc.x', 3185)
        del x
        try: test(x, None, 3187)
        except NameError: test(None, None, 3188)
    A2_glob_b_loc()
    def A2_glob_b_ncap():
        try: test(x, None, 3191)
        except NameError: test(None, None, 3192)
        [x := _ for _ in ["A2_glob_b_ncap.x"]]
        try: test(x, 'A2_glob_b_ncap.x', 3194)
        except NameError: test(None, 'A2_glob_b_ncap.x', 3195)
        def A2_glob_b_ncap_delfunc():
            nonlocal x; del x
        A2_glob_b_ncap_delfunc()
        try: test(x, None, 3199)
        except NameError: test(None, None, 3200)
        x = "A2_glob_b_ncap.x"
        try: test(x, 'A2_glob_b_ncap.x', 3202)
        except NameError: test(None, 'A2_glob_b_ncap.x', 3203)
        del x
        try: test(x, None, 3205)
        except NameError: test(None, None, 3206)
    A2_glob_b_ncap()
    del x
    try: test(x, None, 3209)
    except NameError: test(None, None, 3210)
    def A2_glob_setfunc():
        global x; x = "x"
    A2_glob_setfunc()
    try: test(x, 'x', 3214)
    except NameError: test(None, 'x', 3215)
    def A2_glob_delfunc():
        global x; del x
    A2_glob_delfunc()
    try: test(x, None, 3219)
    except NameError: test(None, None, 3220)
    class A2_glob_B2:
        pass
    class A2_glob_B2_use:
        try: test(x, None, 3224)
        except NameError: test(None, None, 3225)
    class A2_glob_B2_anno:
        x: str
        try: test(x, None, 3228)
        except NameError: test(None, None, 3229)
    class A2_glob_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3233)
        else: error("Enclosed binding exists", 3234)
    class A2_glob_B2_glob:
        global x
        try: test(x, None, 3237)
        except NameError: test(None, None, 3238)
        def A2_glob_B2_glob_setfunc():
            global x; x = "x"
        A2_glob_B2_glob_setfunc()
        try: test(x, 'x', 3242)
        except NameError: test(None, 'x', 3243)
        def A2_glob_B2_glob_delfunc():
            global x; del x
        A2_glob_B2_glob_delfunc()
        try: test(x, None, 3247)
        except NameError: test(None, None, 3248)
        x = "x"
        try: test(x, 'x', 3250)
        except NameError: test(None, 'x', 3251)
        del x
        try: test(x, None, 3253)
        except NameError: test(None, None, 3254)
    class A2_glob_B2_loc:
        try: test(x, None, 3256)
        except NameError: test(None, None, 3257)
        def A2_glob_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_glob_B2_loc.x"
        A2_glob_B2_loc_setfunc()
        try: test(x, 'A2_glob_B2_loc.x', 3261)
        except NameError: test(None, 'A2_glob_B2_loc.x', 3262)
        def A2_glob_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_glob_B2_loc_delfunc()
        try: test(x, None, 3266)
        except NameError: test(None, None, 3267)
        x = "A2_glob_B2_loc.x"
        try: test(x, 'A2_glob_B2_loc.x', 3269)
        except NameError: test(None, 'A2_glob_B2_loc.x', 3270)
        del x
        try: test(x, None, 3272)
        except NameError: test(None, None, 3273)
    class A2_glob_B2_ncap:
        try: test(x, None, 3275)
        except NameError: test(None, None, 3276)
        def A2_glob_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_glob_B2_ncap.x"
        A2_glob_B2_ncap_setfunc()
        try: test(x, 'A2_glob_B2_ncap.x', 3280)
        except NameError: test(None, 'A2_glob_B2_ncap.x', 3281)
        def A2_glob_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_glob_B2_ncap_delfunc()
        try: test(x, None, 3285)
        except NameError: test(None, None, 3286)
        x = "A2_glob_B2_ncap.x"
        try: test(x, 'A2_glob_B2_ncap.x', 3288)
        except NameError: test(None, 'A2_glob_B2_ncap.x', 3289)
        del x
        try: test(x, None, 3291)
        except NameError: test(None, None, 3292)
    def A2_glob_b2():
        pass
    A2_glob_b2()
    def A2_glob_b2_use():
        try: test(x, None, 3297)
        except NameError: test(None, None, 3298)
    A2_glob_b2_use()
    def A2_glob_b2_anno():
        x: str
        try: test(x, None, 3302)
        except NameError: test(None, None, 3303)
    A2_glob_b2_anno()
    def A2_glob_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3308)
        else: error("Enclosed binding exists", 3309)
    A2_glob_b2_nloc()
    def A2_glob_b2_glob():
        global x
        try: test(x, None, 3313)
        except NameError: test(None, None, 3314)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3316)
        except NameError: test(None, 'x', 3317)
        def A2_glob_b2_glob_delfunc():
            global x; del x
        A2_glob_b2_glob_delfunc()
        try: test(x, None, 3321)
        except NameError: test(None, None, 3322)
        x = "x"
        try: test(x, 'x', 3324)
        except NameError: test(None, 'x', 3325)
        del x
        try: test(x, None, 3327)
        except NameError: test(None, None, 3328)
    A2_glob_b2_glob()
    def A2_glob_b2_loc():
        try: test(x, None, 3331)
        except NameError: test(None, None, 3332)
        [x := _ for _ in ["A2_glob_b2_loc.x"]]
        try: test(x, 'A2_glob_b2_loc.x', 3334)
        except NameError: test(None, 'A2_glob_b2_loc.x', 3335)
        def A2_glob_b2_loc_delfunc():
            nonlocal x; del x
        A2_glob_b2_loc_delfunc()
        try: test(x, None, 3339)
        except NameError: test(None, None, 3340)
        x = "A2_glob_b2_loc.x"
        try: test(x, 'A2_glob_b2_loc.x', 3342)
        except NameError: test(None, 'A2_glob_b2_loc.x', 3343)
        del x
        try: test(x, None, 3345)
        except NameError: test(None, None, 3346)
    A2_glob_b2_loc()
    def A2_glob_b2_ncap():
        try: test(x, None, 3349)
        except NameError: test(None, None, 3350)
        [x := _ for _ in ["A2_glob_b2_ncap.x"]]
        try: test(x, 'A2_glob_b2_ncap.x', 3352)
        except NameError: test(None, 'A2_glob_b2_ncap.x', 3353)
        def A2_glob_b2_ncap_delfunc():
            nonlocal x; del x
        A2_glob_b2_ncap_delfunc()
        try: test(x, None, 3357)
        except NameError: test(None, None, 3358)
        x = "A2_glob_b2_ncap.x"
        try: test(x, 'A2_glob_b2_ncap.x', 3360)
        except NameError: test(None, 'A2_glob_b2_ncap.x', 3361)
        del x
        try: test(x, None, 3363)
        except NameError: test(None, None, 3364)
    A2_glob_b2_ncap()
    x = "x"
    try: test(x, 'x', 3367)
    except NameError: test(None, 'x', 3368)
class A2_loc:
    try: test(x, 'x', 3370)
    except NameError: test(None, 'x', 3371)
    class A2_loc_B:
        pass
    class A2_loc_B_use:
        try: test(x, 'x', 3375)
        except NameError: test(None, 'x', 3376)
    class A2_loc_B_anno:
        x: str
        try: test(x, 'x', 3379)
        except NameError: test(None, 'x', 3380)
    class A2_loc_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3384)
        else: error("Enclosed binding exists", 3385)
    class A2_loc_B_glob:
        global x
        try: test(x, 'x', 3388)
        except NameError: test(None, 'x', 3389)
        del x
        try: test(x, None, 3391)
        except NameError: test(None, None, 3392)
        def A2_loc_B_glob_setfunc():
            global x; x = "x"
        A2_loc_B_glob_setfunc()
        try: test(x, 'x', 3396)
        except NameError: test(None, 'x', 3397)
        def A2_loc_B_glob_delfunc():
            global x; del x
        A2_loc_B_glob_delfunc()
        try: test(x, None, 3401)
        except NameError: test(None, None, 3402)
        x = "x"
        try: test(x, 'x', 3404)
        except NameError: test(None, 'x', 3405)
    class A2_loc_B_loc:
        try: test(x, 'x', 3407)
        except NameError: test(None, 'x', 3408)
        def A2_loc_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_loc_B_loc.x"
        A2_loc_B_loc_setfunc()
        try: test(x, 'A2_loc_B_loc.x', 3412)
        except NameError: test(None, 'A2_loc_B_loc.x', 3413)
        def A2_loc_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_loc_B_loc_delfunc()
        try: test(x, 'x', 3417)
        except NameError: test(None, 'x', 3418)
        x = "A2_loc_B_loc.x"
        try: test(x, 'A2_loc_B_loc.x', 3420)
        except NameError: test(None, 'A2_loc_B_loc.x', 3421)
        del x
        try: test(x, 'x', 3423)
        except NameError: test(None, 'x', 3424)
    class A2_loc_B_ncap:
        try: test(x, 'x', 3426)
        except NameError: test(None, 'x', 3427)
        def A2_loc_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_loc_B_ncap.x"
        A2_loc_B_ncap_setfunc()
        try: test(x, 'A2_loc_B_ncap.x', 3431)
        except NameError: test(None, 'A2_loc_B_ncap.x', 3432)
        def A2_loc_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_loc_B_ncap_delfunc()
        try: test(x, 'x', 3436)
        except NameError: test(None, 'x', 3437)
        x = "A2_loc_B_ncap.x"
        try: test(x, 'A2_loc_B_ncap.x', 3439)
        except NameError: test(None, 'A2_loc_B_ncap.x', 3440)
        del x
        try: test(x, 'x', 3442)
        except NameError: test(None, 'x', 3443)
    def A2_loc_b():
        pass
    A2_loc_b()
    def A2_loc_b_use():
        try: test(x, 'x', 3448)
        except NameError: test(None, 'x', 3449)
    A2_loc_b_use()
    def A2_loc_b_anno():
        x: str
        try: test(x, None, 3453)
        except NameError: test(None, None, 3454)
    A2_loc_b_anno()
    def A2_loc_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3459)
        else: error("Enclosed binding exists", 3460)
    A2_loc_b_nloc()
    def A2_loc_b_glob():
        global x
        try: test(x, 'x', 3464)
        except NameError: test(None, 'x', 3465)
        del x
        try: test(x, None, 3467)
        except NameError: test(None, None, 3468)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3470)
        except NameError: test(None, 'x', 3471)
        def A2_loc_b_glob_delfunc():
            global x; del x
        A2_loc_b_glob_delfunc()
        try: test(x, None, 3475)
        except NameError: test(None, None, 3476)
        x = "x"
        try: test(x, 'x', 3478)
        except NameError: test(None, 'x', 3479)
    A2_loc_b_glob()
    def A2_loc_b_loc():
        try: test(x, None, 3482)
        except NameError: test(None, None, 3483)
        [x := _ for _ in ["A2_loc_b_loc.x"]]
        try: test(x, 'A2_loc_b_loc.x', 3485)
        except NameError: test(None, 'A2_loc_b_loc.x', 3486)
        def A2_loc_b_loc_delfunc():
            nonlocal x; del x
        A2_loc_b_loc_delfunc()
        try: test(x, None, 3490)
        except NameError: test(None, None, 3491)
        x = "A2_loc_b_loc.x"
        try: test(x, 'A2_loc_b_loc.x', 3493)
        except NameError: test(None, 'A2_loc_b_loc.x', 3494)
        del x
        try: test(x, None, 3496)
        except NameError: test(None, None, 3497)
    A2_loc_b_loc()
    def A2_loc_b_ncap():
        try: test(x, None, 3500)
        except NameError: test(None, None, 3501)
        [x := _ for _ in ["A2_loc_b_ncap.x"]]
        try: test(x, 'A2_loc_b_ncap.x', 3503)
        except NameError: test(None, 'A2_loc_b_ncap.x', 3504)
        def A2_loc_b_ncap_delfunc():
            nonlocal x; del x
        A2_loc_b_ncap_delfunc()
        try: test(x, None, 3508)
        except NameError: test(None, None, 3509)
        x = "A2_loc_b_ncap.x"
        try: test(x, 'A2_loc_b_ncap.x', 3511)
        except NameError: test(None, 'A2_loc_b_ncap.x', 3512)
        del x
        try: test(x, None, 3514)
        except NameError: test(None, None, 3515)
    A2_loc_b_ncap()
    def A2_loc_setfunc():
        inspect.stack()[1].frame.f_locals["x"] = "A2_loc.x"
    A2_loc_setfunc()
    try: test(x, 'A2_loc.x', 3520)
    except NameError: test(None, 'A2_loc.x', 3521)
    def A2_loc_delfunc():
        del inspect.stack()[1].frame.f_locals["x"]
    A2_loc_delfunc()
    try: test(x, 'x', 3525)
    except NameError: test(None, 'x', 3526)
    x = "A2_loc.x"
    try: test(x, 'A2_loc.x', 3528)
    except NameError: test(None, 'A2_loc.x', 3529)
    class A2_loc_B2:
        pass
    class A2_loc_B2_use:
        try: test(x, 'x', 3533)
        except NameError: test(None, 'x', 3534)
    class A2_loc_B2_anno:
        x: str
        try: test(x, 'x', 3537)
        except NameError: test(None, 'x', 3538)
    class A2_loc_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3542)
        else: error("Enclosed binding exists", 3543)
    class A2_loc_B2_glob:
        global x
        try: test(x, 'x', 3546)
        except NameError: test(None, 'x', 3547)
        del x
        try: test(x, None, 3549)
        except NameError: test(None, None, 3550)
        def A2_loc_B2_glob_setfunc():
            global x; x = "x"
        A2_loc_B2_glob_setfunc()
        try: test(x, 'x', 3554)
        except NameError: test(None, 'x', 3555)
        def A2_loc_B2_glob_delfunc():
            global x; del x
        A2_loc_B2_glob_delfunc()
        try: test(x, None, 3559)
        except NameError: test(None, None, 3560)
        x = "x"
        try: test(x, 'x', 3562)
        except NameError: test(None, 'x', 3563)
    class A2_loc_B2_loc:
        try: test(x, 'x', 3565)
        except NameError: test(None, 'x', 3566)
        def A2_loc_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_loc_B2_loc.x"
        A2_loc_B2_loc_setfunc()
        try: test(x, 'A2_loc_B2_loc.x', 3570)
        except NameError: test(None, 'A2_loc_B2_loc.x', 3571)
        def A2_loc_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_loc_B2_loc_delfunc()
        try: test(x, 'x', 3575)
        except NameError: test(None, 'x', 3576)
        x = "A2_loc_B2_loc.x"
        try: test(x, 'A2_loc_B2_loc.x', 3578)
        except NameError: test(None, 'A2_loc_B2_loc.x', 3579)
        del x
        try: test(x, 'x', 3581)
        except NameError: test(None, 'x', 3582)
    class A2_loc_B2_ncap:
        try: test(x, 'x', 3584)
        except NameError: test(None, 'x', 3585)
        def A2_loc_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_loc_B2_ncap.x"
        A2_loc_B2_ncap_setfunc()
        try: test(x, 'A2_loc_B2_ncap.x', 3589)
        except NameError: test(None, 'A2_loc_B2_ncap.x', 3590)
        def A2_loc_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_loc_B2_ncap_delfunc()
        try: test(x, 'x', 3594)
        except NameError: test(None, 'x', 3595)
        x = "A2_loc_B2_ncap.x"
        try: test(x, 'A2_loc_B2_ncap.x', 3597)
        except NameError: test(None, 'A2_loc_B2_ncap.x', 3598)
        del x
        try: test(x, 'x', 3600)
        except NameError: test(None, 'x', 3601)
    def A2_loc_b2():
        pass
    A2_loc_b2()
    def A2_loc_b2_use():
        try: test(x, 'x', 3606)
        except NameError: test(None, 'x', 3607)
    A2_loc_b2_use()
    def A2_loc_b2_anno():
        x: str
        try: test(x, None, 3611)
        except NameError: test(None, None, 3612)
    A2_loc_b2_anno()
    def A2_loc_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3617)
        else: error("Enclosed binding exists", 3618)
    A2_loc_b2_nloc()
    def A2_loc_b2_glob():
        global x
        try: test(x, 'x', 3622)
        except NameError: test(None, 'x', 3623)
        del x
        try: test(x, None, 3625)
        except NameError: test(None, None, 3626)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3628)
        except NameError: test(None, 'x', 3629)
        def A2_loc_b2_glob_delfunc():
            global x; del x
        A2_loc_b2_glob_delfunc()
        try: test(x, None, 3633)
        except NameError: test(None, None, 3634)
        x = "x"
        try: test(x, 'x', 3636)
        except NameError: test(None, 'x', 3637)
    A2_loc_b2_glob()
    def A2_loc_b2_loc():
        try: test(x, None, 3640)
        except NameError: test(None, None, 3641)
        [x := _ for _ in ["A2_loc_b2_loc.x"]]
        try: test(x, 'A2_loc_b2_loc.x', 3643)
        except NameError: test(None, 'A2_loc_b2_loc.x', 3644)
        def A2_loc_b2_loc_delfunc():
            nonlocal x; del x
        A2_loc_b2_loc_delfunc()
        try: test(x, None, 3648)
        except NameError: test(None, None, 3649)
        x = "A2_loc_b2_loc.x"
        try: test(x, 'A2_loc_b2_loc.x', 3651)
        except NameError: test(None, 'A2_loc_b2_loc.x', 3652)
        del x
        try: test(x, None, 3654)
        except NameError: test(None, None, 3655)
    A2_loc_b2_loc()
    def A2_loc_b2_ncap():
        try: test(x, None, 3658)
        except NameError: test(None, None, 3659)
        [x := _ for _ in ["A2_loc_b2_ncap.x"]]
        try: test(x, 'A2_loc_b2_ncap.x', 3661)
        except NameError: test(None, 'A2_loc_b2_ncap.x', 3662)
        def A2_loc_b2_ncap_delfunc():
            nonlocal x; del x
        A2_loc_b2_ncap_delfunc()
        try: test(x, None, 3666)
        except NameError: test(None, None, 3667)
        x = "A2_loc_b2_ncap.x"
        try: test(x, 'A2_loc_b2_ncap.x', 3669)
        except NameError: test(None, 'A2_loc_b2_ncap.x', 3670)
        del x
        try: test(x, None, 3672)
        except NameError: test(None, None, 3673)
    A2_loc_b2_ncap()
    del x
    try: test(x, 'x', 3676)
    except NameError: test(None, 'x', 3677)
class A2_ncap:
    try: test(x, 'x', 3679)
    except NameError: test(None, 'x', 3680)
    class A2_ncap_B:
        pass
    class A2_ncap_B_glob:
        global x
        try: test(x, 'x', 3685)
        except NameError: test(None, 'x', 3686)
        del x
        try: test(x, None, 3688)
        except NameError: test(None, None, 3689)
        def A2_ncap_B_glob_setfunc():
            global x; x = "x"
        A2_ncap_B_glob_setfunc()
        try: test(x, 'x', 3693)
        except NameError: test(None, 'x', 3694)
        def A2_ncap_B_glob_delfunc():
            global x; del x
        A2_ncap_B_glob_delfunc()
        try: test(x, None, 3698)
        except NameError: test(None, None, 3699)
        x = "x"
        try: test(x, 'x', 3701)
        except NameError: test(None, 'x', 3702)
    class A2_ncap_B_loc:
        try: test(x, 'x', 3704)
        except NameError: test(None, 'x', 3705)
        def A2_ncap_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_ncap_B_loc.x"
        A2_ncap_B_loc_setfunc()
        try: test(x, 'A2_ncap_B_loc.x', 3709)
        except NameError: test(None, 'A2_ncap_B_loc.x', 3710)
        def A2_ncap_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_ncap_B_loc_delfunc()
        try: test(x, 'x', 3714)
        except NameError: test(None, 'x', 3715)
        x = "A2_ncap_B_loc.x"
        try: test(x, 'A2_ncap_B_loc.x', 3717)
        except NameError: test(None, 'A2_ncap_B_loc.x', 3718)
        del x
        try: test(x, 'x', 3720)
        except NameError: test(None, 'x', 3721)
    def A2_ncap_b():
        pass
    A2_ncap_b()
    def A2_ncap_b_glob():
        global x
        try: test(x, 'x', 3727)
        except NameError: test(None, 'x', 3728)
        del x
        try: test(x, None, 3730)
        except NameError: test(None, None, 3731)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3733)
        except NameError: test(None, 'x', 3734)
        def A2_ncap_b_glob_delfunc():
            global x; del x
        A2_ncap_b_glob_delfunc()
        try: test(x, None, 3738)
        except NameError: test(None, None, 3739)
        x = "x"
        try: test(x, 'x', 3741)
        except NameError: test(None, 'x', 3742)
    A2_ncap_b_glob()
    def A2_ncap_b_loc():
        try: test(x, None, 3745)
        except NameError: test(None, None, 3746)
        [x := _ for _ in ["A2_ncap_b_loc.x"]]
        try: test(x, 'A2_ncap_b_loc.x', 3748)
        except NameError: test(None, 'A2_ncap_b_loc.x', 3749)
        def A2_ncap_b_loc_delfunc():
            nonlocal x; del x
        A2_ncap_b_loc_delfunc()
        try: test(x, None, 3753)
        except NameError: test(None, None, 3754)
        x = "A2_ncap_b_loc.x"
        try: test(x, 'A2_ncap_b_loc.x', 3756)
        except NameError: test(None, 'A2_ncap_b_loc.x', 3757)
        del x
        try: test(x, None, 3759)
        except NameError: test(None, None, 3760)
    A2_ncap_b_loc()
    def A2_ncap_setfunc():
        inspect.stack()[1].frame.f_locals["x"] = "A2_ncap.x"
    A2_ncap_setfunc()
    try: test(x, 'A2_ncap.x', 3765)
    except NameError: test(None, 'A2_ncap.x', 3766)
    def A2_ncap_delfunc():
        del inspect.stack()[1].frame.f_locals["x"]
    A2_ncap_delfunc()
    try: test(x, 'x', 3770)
    except NameError: test(None, 'x', 3771)
    x = "A2_ncap.x"
    try: test(x, 'A2_ncap.x', 3773)
    except NameError: test(None, 'A2_ncap.x', 3774)
    class A2_ncap_B2:
        pass
    class A2_ncap_B2_glob:
        global x
        try: test(x, 'x', 3779)
        except NameError: test(None, 'x', 3780)
        del x
        try: test(x, None, 3782)
        except NameError: test(None, None, 3783)
        def A2_ncap_B2_glob_setfunc():
            global x; x = "x"
        A2_ncap_B2_glob_setfunc()
        try: test(x, 'x', 3787)
        except NameError: test(None, 'x', 3788)
        def A2_ncap_B2_glob_delfunc():
            global x; del x
        A2_ncap_B2_glob_delfunc()
        try: test(x, None, 3792)
        except NameError: test(None, None, 3793)
        x = "x"
        try: test(x, 'x', 3795)
        except NameError: test(None, 'x', 3796)
    class A2_ncap_B2_loc:
        try: test(x, 'x', 3798)
        except NameError: test(None, 'x', 3799)
        def A2_ncap_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "A2_ncap_B2_loc.x"
        A2_ncap_B2_loc_setfunc()
        try: test(x, 'A2_ncap_B2_loc.x', 3803)
        except NameError: test(None, 'A2_ncap_B2_loc.x', 3804)
        def A2_ncap_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        A2_ncap_B2_loc_delfunc()
        try: test(x, 'x', 3808)
        except NameError: test(None, 'x', 3809)
        x = "A2_ncap_B2_loc.x"
        try: test(x, 'A2_ncap_B2_loc.x', 3811)
        except NameError: test(None, 'A2_ncap_B2_loc.x', 3812)
        del x
        try: test(x, 'x', 3814)
        except NameError: test(None, 'x', 3815)
    def A2_ncap_b2():
        pass
    A2_ncap_b2()
    def A2_ncap_b2_glob():
        global x
        try: test(x, 'x', 3821)
        except NameError: test(None, 'x', 3822)
        del x
        try: test(x, None, 3824)
        except NameError: test(None, None, 3825)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3827)
        except NameError: test(None, 'x', 3828)
        def A2_ncap_b2_glob_delfunc():
            global x; del x
        A2_ncap_b2_glob_delfunc()
        try: test(x, None, 3832)
        except NameError: test(None, None, 3833)
        x = "x"
        try: test(x, 'x', 3835)
        except NameError: test(None, 'x', 3836)
    A2_ncap_b2_glob()
    def A2_ncap_b2_loc():
        try: test(x, None, 3839)
        except NameError: test(None, None, 3840)
        [x := _ for _ in ["A2_ncap_b2_loc.x"]]
        try: test(x, 'A2_ncap_b2_loc.x', 3842)
        except NameError: test(None, 'A2_ncap_b2_loc.x', 3843)
        def A2_ncap_b2_loc_delfunc():
            nonlocal x; del x
        A2_ncap_b2_loc_delfunc()
        try: test(x, None, 3847)
        except NameError: test(None, None, 3848)
        x = "A2_ncap_b2_loc.x"
        try: test(x, 'A2_ncap_b2_loc.x', 3850)
        except NameError: test(None, 'A2_ncap_b2_loc.x', 3851)
        del x
        try: test(x, None, 3853)
        except NameError: test(None, None, 3854)
    A2_ncap_b2_loc()
    del x
    try: test(x, 'x', 3857)
    except NameError: test(None, 'x', 3858)
def a2():
    class a2_B:
        pass
    class a2_B_use:
        try: test(x, 'x', 3863)
        except NameError: test(None, 'x', 3864)
    class a2_B_anno:
        x: str
        try: test(x, 'x', 3867)
        except NameError: test(None, 'x', 3868)
    class a2_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3872)
        else: error("Enclosed binding exists", 3873)
    class a2_B_glob:
        global x
        try: test(x, 'x', 3876)
        except NameError: test(None, 'x', 3877)
        del x
        try: test(x, None, 3879)
        except NameError: test(None, None, 3880)
        def a2_B_glob_setfunc():
            global x; x = "x"
        a2_B_glob_setfunc()
        try: test(x, 'x', 3884)
        except NameError: test(None, 'x', 3885)
        def a2_B_glob_delfunc():
            global x; del x
        a2_B_glob_delfunc()
        try: test(x, None, 3889)
        except NameError: test(None, None, 3890)
        x = "x"
        try: test(x, 'x', 3892)
        except NameError: test(None, 'x', 3893)
    class a2_B_loc:
        try: test(x, 'x', 3895)
        except NameError: test(None, 'x', 3896)
        def a2_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_B_loc.x"
        a2_B_loc_setfunc()
        try: test(x, 'a2_B_loc.x', 3900)
        except NameError: test(None, 'a2_B_loc.x', 3901)
        def a2_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_B_loc_delfunc()
        try: test(x, 'x', 3905)
        except NameError: test(None, 'x', 3906)
        x = "a2_B_loc.x"
        try: test(x, 'a2_B_loc.x', 3908)
        except NameError: test(None, 'a2_B_loc.x', 3909)
        del x
        try: test(x, 'x', 3911)
        except NameError: test(None, 'x', 3912)
    class a2_B_ncap:
        try: test(x, 'x', 3914)
        except NameError: test(None, 'x', 3915)
        def a2_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_B_ncap.x"
        a2_B_ncap_setfunc()
        try: test(x, 'a2_B_ncap.x', 3919)
        except NameError: test(None, 'a2_B_ncap.x', 3920)
        def a2_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_B_ncap_delfunc()
        try: test(x, 'x', 3924)
        except NameError: test(None, 'x', 3925)
        x = "a2_B_ncap.x"
        try: test(x, 'a2_B_ncap.x', 3927)
        except NameError: test(None, 'a2_B_ncap.x', 3928)
        del x
        try: test(x, 'x', 3930)
        except NameError: test(None, 'x', 3931)
    def a2_b():
        pass
    a2_b()
    def a2_b_use():
        try: test(x, 'x', 3936)
        except NameError: test(None, 'x', 3937)
    a2_b_use()
    def a2_b_anno():
        x: str
        try: test(x, None, 3941)
        except NameError: test(None, None, 3942)
    a2_b_anno()
    def a2_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 3947)
        else: error("Enclosed binding exists", 3948)
    a2_b_nloc()
    def a2_b_glob():
        global x
        try: test(x, 'x', 3952)
        except NameError: test(None, 'x', 3953)
        del x
        try: test(x, None, 3955)
        except NameError: test(None, None, 3956)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 3958)
        except NameError: test(None, 'x', 3959)
        def a2_b_glob_delfunc():
            global x; del x
        a2_b_glob_delfunc()
        try: test(x, None, 3963)
        except NameError: test(None, None, 3964)
        x = "x"
        try: test(x, 'x', 3966)
        except NameError: test(None, 'x', 3967)
    a2_b_glob()
    def a2_b_loc():
        try: test(x, None, 3970)
        except NameError: test(None, None, 3971)
        [x := _ for _ in ["a2_b_loc.x"]]
        try: test(x, 'a2_b_loc.x', 3973)
        except NameError: test(None, 'a2_b_loc.x', 3974)
        def a2_b_loc_delfunc():
            nonlocal x; del x
        a2_b_loc_delfunc()
        try: test(x, None, 3978)
        except NameError: test(None, None, 3979)
        x = "a2_b_loc.x"
        try: test(x, 'a2_b_loc.x', 3981)
        except NameError: test(None, 'a2_b_loc.x', 3982)
        del x
        try: test(x, None, 3984)
        except NameError: test(None, None, 3985)
    a2_b_loc()
    def a2_b_ncap():
        try: test(x, None, 3988)
        except NameError: test(None, None, 3989)
        [x := _ for _ in ["a2_b_ncap.x"]]
        try: test(x, 'a2_b_ncap.x', 3991)
        except NameError: test(None, 'a2_b_ncap.x', 3992)
        def a2_b_ncap_delfunc():
            nonlocal x; del x
        a2_b_ncap_delfunc()
        try: test(x, None, 3996)
        except NameError: test(None, None, 3997)
        x = "a2_b_ncap.x"
        try: test(x, 'a2_b_ncap.x', 3999)
        except NameError: test(None, 'a2_b_ncap.x', 4000)
        del x
        try: test(x, None, 4002)
        except NameError: test(None, None, 4003)
    a2_b_ncap()
a2()
def a2_use():
    try: test(x, 'x', 4007)
    except NameError: test(None, 'x', 4008)
    class a2_use_B:
        pass
    class a2_use_B_use:
        try: test(x, 'x', 4012)
        except NameError: test(None, 'x', 4013)
    class a2_use_B_anno:
        x: str
        try: test(x, 'x', 4016)
        except NameError: test(None, 'x', 4017)
    class a2_use_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4021)
        else: error("Enclosed binding exists", 4022)
    class a2_use_B_glob:
        global x
        try: test(x, 'x', 4025)
        except NameError: test(None, 'x', 4026)
        del x
        try: test(x, None, 4028)
        except NameError: test(None, None, 4029)
        def a2_use_B_glob_setfunc():
            global x; x = "x"
        a2_use_B_glob_setfunc()
        try: test(x, 'x', 4033)
        except NameError: test(None, 'x', 4034)
        def a2_use_B_glob_delfunc():
            global x; del x
        a2_use_B_glob_delfunc()
        try: test(x, None, 4038)
        except NameError: test(None, None, 4039)
        x = "x"
        try: test(x, 'x', 4041)
        except NameError: test(None, 'x', 4042)
    class a2_use_B_loc:
        try: test(x, 'x', 4044)
        except NameError: test(None, 'x', 4045)
        def a2_use_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_use_B_loc.x"
        a2_use_B_loc_setfunc()
        try: test(x, 'a2_use_B_loc.x', 4049)
        except NameError: test(None, 'a2_use_B_loc.x', 4050)
        def a2_use_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_use_B_loc_delfunc()
        try: test(x, 'x', 4054)
        except NameError: test(None, 'x', 4055)
        x = "a2_use_B_loc.x"
        try: test(x, 'a2_use_B_loc.x', 4057)
        except NameError: test(None, 'a2_use_B_loc.x', 4058)
        del x
        try: test(x, 'x', 4060)
        except NameError: test(None, 'x', 4061)
    class a2_use_B_ncap:
        try: test(x, 'x', 4063)
        except NameError: test(None, 'x', 4064)
        def a2_use_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_use_B_ncap.x"
        a2_use_B_ncap_setfunc()
        try: test(x, 'a2_use_B_ncap.x', 4068)
        except NameError: test(None, 'a2_use_B_ncap.x', 4069)
        def a2_use_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_use_B_ncap_delfunc()
        try: test(x, 'x', 4073)
        except NameError: test(None, 'x', 4074)
        x = "a2_use_B_ncap.x"
        try: test(x, 'a2_use_B_ncap.x', 4076)
        except NameError: test(None, 'a2_use_B_ncap.x', 4077)
        del x
        try: test(x, 'x', 4079)
        except NameError: test(None, 'x', 4080)
    def a2_use_b():
        pass
    a2_use_b()
    def a2_use_b_use():
        try: test(x, 'x', 4085)
        except NameError: test(None, 'x', 4086)
    a2_use_b_use()
    def a2_use_b_anno():
        x: str
        try: test(x, None, 4090)
        except NameError: test(None, None, 4091)
    a2_use_b_anno()
    def a2_use_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4096)
        else: error("Enclosed binding exists", 4097)
    a2_use_b_nloc()
    def a2_use_b_glob():
        global x
        try: test(x, 'x', 4101)
        except NameError: test(None, 'x', 4102)
        del x
        try: test(x, None, 4104)
        except NameError: test(None, None, 4105)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4107)
        except NameError: test(None, 'x', 4108)
        def a2_use_b_glob_delfunc():
            global x; del x
        a2_use_b_glob_delfunc()
        try: test(x, None, 4112)
        except NameError: test(None, None, 4113)
        x = "x"
        try: test(x, 'x', 4115)
        except NameError: test(None, 'x', 4116)
    a2_use_b_glob()
    def a2_use_b_loc():
        try: test(x, None, 4119)
        except NameError: test(None, None, 4120)
        [x := _ for _ in ["a2_use_b_loc.x"]]
        try: test(x, 'a2_use_b_loc.x', 4122)
        except NameError: test(None, 'a2_use_b_loc.x', 4123)
        def a2_use_b_loc_delfunc():
            nonlocal x; del x
        a2_use_b_loc_delfunc()
        try: test(x, None, 4127)
        except NameError: test(None, None, 4128)
        x = "a2_use_b_loc.x"
        try: test(x, 'a2_use_b_loc.x', 4130)
        except NameError: test(None, 'a2_use_b_loc.x', 4131)
        del x
        try: test(x, None, 4133)
        except NameError: test(None, None, 4134)
    a2_use_b_loc()
    def a2_use_b_ncap():
        try: test(x, None, 4137)
        except NameError: test(None, None, 4138)
        [x := _ for _ in ["a2_use_b_ncap.x"]]
        try: test(x, 'a2_use_b_ncap.x', 4140)
        except NameError: test(None, 'a2_use_b_ncap.x', 4141)
        def a2_use_b_ncap_delfunc():
            nonlocal x; del x
        a2_use_b_ncap_delfunc()
        try: test(x, None, 4145)
        except NameError: test(None, None, 4146)
        x = "a2_use_b_ncap.x"
        try: test(x, 'a2_use_b_ncap.x', 4148)
        except NameError: test(None, 'a2_use_b_ncap.x', 4149)
        del x
        try: test(x, None, 4151)
        except NameError: test(None, None, 4152)
    a2_use_b_ncap()
a2_use()
def a2_anno():
    x: str
    try: test(x, None, 4157)
    except NameError: test(None, None, 4158)
    class a2_anno_B:
        pass
    class a2_anno_B_use:
        try: test(x, None, 4162)
        except NameError: test(None, None, 4163)
    class a2_anno_B_anno:
        x: str
        try: test(x, 'x', 4166)
        except NameError: test(None, 'x', 4167)
    class a2_anno_B_nloc:
        nonlocal x
        try: test(x, None, 4170)
        except NameError: test(None, None, 4171)
        def a2_anno_B_nloc_setfunc():
            nonlocal x; x = "a2_anno.x"
        a2_anno_B_nloc_setfunc()
        try: test(x, 'a2_anno.x', 4175)
        except NameError: test(None, 'a2_anno.x', 4176)
        def a2_anno_B_nloc_delfunc():
            nonlocal x; del x
        a2_anno_B_nloc_delfunc()
        try: test(x, None, 4180)
        except NameError: test(None, None, 4181)
        x = "a2_anno.x"
        try: test(x, 'a2_anno.x', 4183)
        except NameError: test(None, 'a2_anno.x', 4184)
        del x
        try: test(x, None, 4186)
        except NameError: test(None, None, 4187)
    class a2_anno_B_glob:
        global x
        try: test(x, 'x', 4190)
        except NameError: test(None, 'x', 4191)
        del x
        try: test(x, None, 4193)
        except NameError: test(None, None, 4194)
        def a2_anno_B_glob_setfunc():
            global x; x = "x"
        a2_anno_B_glob_setfunc()
        try: test(x, 'x', 4198)
        except NameError: test(None, 'x', 4199)
        def a2_anno_B_glob_delfunc():
            global x; del x
        a2_anno_B_glob_delfunc()
        try: test(x, None, 4203)
        except NameError: test(None, None, 4204)
        x = "x"
        try: test(x, 'x', 4206)
        except NameError: test(None, 'x', 4207)
    class a2_anno_B_loc:
        try: test(x, 'x', 4209)
        except NameError: test(None, 'x', 4210)
        def a2_anno_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_anno_B_loc.x"
        a2_anno_B_loc_setfunc()
        try: test(x, 'a2_anno_B_loc.x', 4214)
        except NameError: test(None, 'a2_anno_B_loc.x', 4215)
        def a2_anno_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_anno_B_loc_delfunc()
        try: test(x, 'x', 4219)
        except NameError: test(None, 'x', 4220)
        x = "a2_anno_B_loc.x"
        try: test(x, 'a2_anno_B_loc.x', 4222)
        except NameError: test(None, 'a2_anno_B_loc.x', 4223)
        del x
        try: test(x, 'x', 4225)
        except NameError: test(None, 'x', 4226)
    class a2_anno_B_ncap:
        try: test(x, 'x', 4228)
        except NameError: test(None, 'x', 4229)
        def a2_anno_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_anno_B_ncap.x"
        a2_anno_B_ncap_setfunc()
        try: test(x, 'a2_anno_B_ncap.x', 4233)
        except NameError: test(None, 'a2_anno_B_ncap.x', 4234)
        def a2_anno_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_anno_B_ncap_delfunc()
        try: test(x, 'x', 4238)
        except NameError: test(None, 'x', 4239)
        x = "a2_anno_B_ncap.x"
        try: test(x, 'a2_anno_B_ncap.x', 4241)
        except NameError: test(None, 'a2_anno_B_ncap.x', 4242)
        del x
        try: test(x, 'x', 4244)
        except NameError: test(None, 'x', 4245)
    def a2_anno_b():
        pass
    a2_anno_b()
    def a2_anno_b_use():
        try: test(x, None, 4250)
        except NameError: test(None, None, 4251)
    a2_anno_b_use()
    def a2_anno_b_anno():
        x: str
        try: test(x, None, 4255)
        except NameError: test(None, None, 4256)
    a2_anno_b_anno()
    def a2_anno_b_nloc():
        nonlocal x
        try: test(x, None, 4260)
        except NameError: test(None, None, 4261)
        [x := _ for _ in ["a2_anno.x"]]
        try: test(x, 'a2_anno.x', 4263)
        except NameError: test(None, 'a2_anno.x', 4264)
        def a2_anno_b_nloc_delfunc():
            nonlocal x; del x
        a2_anno_b_nloc_delfunc()
        try: test(x, None, 4268)
        except NameError: test(None, None, 4269)
        x = "a2_anno.x"
        try: test(x, 'a2_anno.x', 4271)
        except NameError: test(None, 'a2_anno.x', 4272)
        del x
        try: test(x, None, 4274)
        except NameError: test(None, None, 4275)
    a2_anno_b_nloc()
    def a2_anno_b_glob():
        global x
        try: test(x, 'x', 4279)
        except NameError: test(None, 'x', 4280)
        del x
        try: test(x, None, 4282)
        except NameError: test(None, None, 4283)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4285)
        except NameError: test(None, 'x', 4286)
        def a2_anno_b_glob_delfunc():
            global x; del x
        a2_anno_b_glob_delfunc()
        try: test(x, None, 4290)
        except NameError: test(None, None, 4291)
        x = "x"
        try: test(x, 'x', 4293)
        except NameError: test(None, 'x', 4294)
    a2_anno_b_glob()
    def a2_anno_b_loc():
        try: test(x, None, 4297)
        except NameError: test(None, None, 4298)
        [x := _ for _ in ["a2_anno_b_loc.x"]]
        try: test(x, 'a2_anno_b_loc.x', 4300)
        except NameError: test(None, 'a2_anno_b_loc.x', 4301)
        def a2_anno_b_loc_delfunc():
            nonlocal x; del x
        a2_anno_b_loc_delfunc()
        try: test(x, None, 4305)
        except NameError: test(None, None, 4306)
        x = "a2_anno_b_loc.x"
        try: test(x, 'a2_anno_b_loc.x', 4308)
        except NameError: test(None, 'a2_anno_b_loc.x', 4309)
        del x
        try: test(x, None, 4311)
        except NameError: test(None, None, 4312)
    a2_anno_b_loc()
    def a2_anno_b_ncap():
        try: test(x, None, 4315)
        except NameError: test(None, None, 4316)
        [x := _ for _ in ["a2_anno_b_ncap.x"]]
        try: test(x, 'a2_anno_b_ncap.x', 4318)
        except NameError: test(None, 'a2_anno_b_ncap.x', 4319)
        def a2_anno_b_ncap_delfunc():
            nonlocal x; del x
        a2_anno_b_ncap_delfunc()
        try: test(x, None, 4323)
        except NameError: test(None, None, 4324)
        x = "a2_anno_b_ncap.x"
        try: test(x, 'a2_anno_b_ncap.x', 4326)
        except NameError: test(None, 'a2_anno_b_ncap.x', 4327)
        del x
        try: test(x, None, 4329)
        except NameError: test(None, None, 4330)
    a2_anno_b_ncap()
a2_anno()
def a2_nloc():
    # No enclosed binding exists.
    try: compile("nonlocal x", "<string>", "exec")
    except SyntaxError: test(None, None, 4336)
    else: error("Enclosed binding exists", 4337)
a2_nloc()
def a2_glob():
    global x
    try: test(x, 'x', 4341)
    except NameError: test(None, 'x', 4342)
    class a2_glob_B:
        pass
    class a2_glob_B_use:
        try: test(x, 'x', 4346)
        except NameError: test(None, 'x', 4347)
    class a2_glob_B_anno:
        x: str
        try: test(x, 'x', 4350)
        except NameError: test(None, 'x', 4351)
    class a2_glob_B_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4355)
        else: error("Enclosed binding exists", 4356)
    class a2_glob_B_glob:
        global x
        try: test(x, 'x', 4359)
        except NameError: test(None, 'x', 4360)
        del x
        try: test(x, None, 4362)
        except NameError: test(None, None, 4363)
        def a2_glob_B_glob_setfunc():
            global x; x = "x"
        a2_glob_B_glob_setfunc()
        try: test(x, 'x', 4367)
        except NameError: test(None, 'x', 4368)
        def a2_glob_B_glob_delfunc():
            global x; del x
        a2_glob_B_glob_delfunc()
        try: test(x, None, 4372)
        except NameError: test(None, None, 4373)
        x = "x"
        try: test(x, 'x', 4375)
        except NameError: test(None, 'x', 4376)
    class a2_glob_B_loc:
        try: test(x, 'x', 4378)
        except NameError: test(None, 'x', 4379)
        def a2_glob_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_glob_B_loc.x"
        a2_glob_B_loc_setfunc()
        try: test(x, 'a2_glob_B_loc.x', 4383)
        except NameError: test(None, 'a2_glob_B_loc.x', 4384)
        def a2_glob_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_glob_B_loc_delfunc()
        try: test(x, 'x', 4388)
        except NameError: test(None, 'x', 4389)
        x = "a2_glob_B_loc.x"
        try: test(x, 'a2_glob_B_loc.x', 4391)
        except NameError: test(None, 'a2_glob_B_loc.x', 4392)
        del x
        try: test(x, 'x', 4394)
        except NameError: test(None, 'x', 4395)
    class a2_glob_B_ncap:
        try: test(x, 'x', 4397)
        except NameError: test(None, 'x', 4398)
        def a2_glob_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_glob_B_ncap.x"
        a2_glob_B_ncap_setfunc()
        try: test(x, 'a2_glob_B_ncap.x', 4402)
        except NameError: test(None, 'a2_glob_B_ncap.x', 4403)
        def a2_glob_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_glob_B_ncap_delfunc()
        try: test(x, 'x', 4407)
        except NameError: test(None, 'x', 4408)
        x = "a2_glob_B_ncap.x"
        try: test(x, 'a2_glob_B_ncap.x', 4410)
        except NameError: test(None, 'a2_glob_B_ncap.x', 4411)
        del x
        try: test(x, 'x', 4413)
        except NameError: test(None, 'x', 4414)
    def a2_glob_b():
        pass
    a2_glob_b()
    def a2_glob_b_use():
        try: test(x, 'x', 4419)
        except NameError: test(None, 'x', 4420)
    a2_glob_b_use()
    def a2_glob_b_anno():
        x: str
        try: test(x, None, 4424)
        except NameError: test(None, None, 4425)
    a2_glob_b_anno()
    def a2_glob_b_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4430)
        else: error("Enclosed binding exists", 4431)
    a2_glob_b_nloc()
    def a2_glob_b_glob():
        global x
        try: test(x, 'x', 4435)
        except NameError: test(None, 'x', 4436)
        del x
        try: test(x, None, 4438)
        except NameError: test(None, None, 4439)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4441)
        except NameError: test(None, 'x', 4442)
        def a2_glob_b_glob_delfunc():
            global x; del x
        a2_glob_b_glob_delfunc()
        try: test(x, None, 4446)
        except NameError: test(None, None, 4447)
        x = "x"
        try: test(x, 'x', 4449)
        except NameError: test(None, 'x', 4450)
    a2_glob_b_glob()
    def a2_glob_b_loc():
        try: test(x, None, 4453)
        except NameError: test(None, None, 4454)
        [x := _ for _ in ["a2_glob_b_loc.x"]]
        try: test(x, 'a2_glob_b_loc.x', 4456)
        except NameError: test(None, 'a2_glob_b_loc.x', 4457)
        def a2_glob_b_loc_delfunc():
            nonlocal x; del x
        a2_glob_b_loc_delfunc()
        try: test(x, None, 4461)
        except NameError: test(None, None, 4462)
        x = "a2_glob_b_loc.x"
        try: test(x, 'a2_glob_b_loc.x', 4464)
        except NameError: test(None, 'a2_glob_b_loc.x', 4465)
        del x
        try: test(x, None, 4467)
        except NameError: test(None, None, 4468)
    a2_glob_b_loc()
    def a2_glob_b_ncap():
        try: test(x, None, 4471)
        except NameError: test(None, None, 4472)
        [x := _ for _ in ["a2_glob_b_ncap.x"]]
        try: test(x, 'a2_glob_b_ncap.x', 4474)
        except NameError: test(None, 'a2_glob_b_ncap.x', 4475)
        def a2_glob_b_ncap_delfunc():
            nonlocal x; del x
        a2_glob_b_ncap_delfunc()
        try: test(x, None, 4479)
        except NameError: test(None, None, 4480)
        x = "a2_glob_b_ncap.x"
        try: test(x, 'a2_glob_b_ncap.x', 4482)
        except NameError: test(None, 'a2_glob_b_ncap.x', 4483)
        del x
        try: test(x, None, 4485)
        except NameError: test(None, None, 4486)
    a2_glob_b_ncap()
    del x
    try: test(x, None, 4489)
    except NameError: test(None, None, 4490)
    [x := _ for _ in ["x"]]
    try: test(x, 'x', 4492)
    except NameError: test(None, 'x', 4493)
    def a2_glob_delfunc():
        global x; del x
    a2_glob_delfunc()
    try: test(x, None, 4497)
    except NameError: test(None, None, 4498)
    class a2_glob_B2:
        pass
    class a2_glob_B2_use:
        try: test(x, None, 4502)
        except NameError: test(None, None, 4503)
    class a2_glob_B2_anno:
        x: str
        try: test(x, None, 4506)
        except NameError: test(None, None, 4507)
    class a2_glob_B2_nloc:
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4511)
        else: error("Enclosed binding exists", 4512)
    class a2_glob_B2_glob:
        global x
        try: test(x, None, 4515)
        except NameError: test(None, None, 4516)
        def a2_glob_B2_glob_setfunc():
            global x; x = "x"
        a2_glob_B2_glob_setfunc()
        try: test(x, 'x', 4520)
        except NameError: test(None, 'x', 4521)
        def a2_glob_B2_glob_delfunc():
            global x; del x
        a2_glob_B2_glob_delfunc()
        try: test(x, None, 4525)
        except NameError: test(None, None, 4526)
        x = "x"
        try: test(x, 'x', 4528)
        except NameError: test(None, 'x', 4529)
        del x
        try: test(x, None, 4531)
        except NameError: test(None, None, 4532)
    class a2_glob_B2_loc:
        try: test(x, None, 4534)
        except NameError: test(None, None, 4535)
        def a2_glob_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_glob_B2_loc.x"
        a2_glob_B2_loc_setfunc()
        try: test(x, 'a2_glob_B2_loc.x', 4539)
        except NameError: test(None, 'a2_glob_B2_loc.x', 4540)
        def a2_glob_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_glob_B2_loc_delfunc()
        try: test(x, None, 4544)
        except NameError: test(None, None, 4545)
        x = "a2_glob_B2_loc.x"
        try: test(x, 'a2_glob_B2_loc.x', 4547)
        except NameError: test(None, 'a2_glob_B2_loc.x', 4548)
        del x
        try: test(x, None, 4550)
        except NameError: test(None, None, 4551)
    class a2_glob_B2_ncap:
        try: test(x, None, 4553)
        except NameError: test(None, None, 4554)
        def a2_glob_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_glob_B2_ncap.x"
        a2_glob_B2_ncap_setfunc()
        try: test(x, 'a2_glob_B2_ncap.x', 4558)
        except NameError: test(None, 'a2_glob_B2_ncap.x', 4559)
        def a2_glob_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_glob_B2_ncap_delfunc()
        try: test(x, None, 4563)
        except NameError: test(None, None, 4564)
        x = "a2_glob_B2_ncap.x"
        try: test(x, 'a2_glob_B2_ncap.x', 4566)
        except NameError: test(None, 'a2_glob_B2_ncap.x', 4567)
        del x
        try: test(x, None, 4569)
        except NameError: test(None, None, 4570)
    def a2_glob_b2():
        pass
    a2_glob_b2()
    def a2_glob_b2_use():
        try: test(x, None, 4575)
        except NameError: test(None, None, 4576)
    a2_glob_b2_use()
    def a2_glob_b2_anno():
        x: str
        try: test(x, None, 4580)
        except NameError: test(None, None, 4581)
    a2_glob_b2_anno()
    def a2_glob_b2_nloc():
        # No enclosed binding exists.
        try: compile("nonlocal x", "<string>", "exec")
        except SyntaxError: test(None, None, 4586)
        else: error("Enclosed binding exists", 4587)
    a2_glob_b2_nloc()
    def a2_glob_b2_glob():
        global x
        try: test(x, None, 4591)
        except NameError: test(None, None, 4592)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4594)
        except NameError: test(None, 'x', 4595)
        def a2_glob_b2_glob_delfunc():
            global x; del x
        a2_glob_b2_glob_delfunc()
        try: test(x, None, 4599)
        except NameError: test(None, None, 4600)
        x = "x"
        try: test(x, 'x', 4602)
        except NameError: test(None, 'x', 4603)
        del x
        try: test(x, None, 4605)
        except NameError: test(None, None, 4606)
    a2_glob_b2_glob()
    def a2_glob_b2_loc():
        try: test(x, None, 4609)
        except NameError: test(None, None, 4610)
        [x := _ for _ in ["a2_glob_b2_loc.x"]]
        try: test(x, 'a2_glob_b2_loc.x', 4612)
        except NameError: test(None, 'a2_glob_b2_loc.x', 4613)
        def a2_glob_b2_loc_delfunc():
            nonlocal x; del x
        a2_glob_b2_loc_delfunc()
        try: test(x, None, 4617)
        except NameError: test(None, None, 4618)
        x = "a2_glob_b2_loc.x"
        try: test(x, 'a2_glob_b2_loc.x', 4620)
        except NameError: test(None, 'a2_glob_b2_loc.x', 4621)
        del x
        try: test(x, None, 4623)
        except NameError: test(None, None, 4624)
    a2_glob_b2_loc()
    def a2_glob_b2_ncap():
        try: test(x, None, 4627)
        except NameError: test(None, None, 4628)
        [x := _ for _ in ["a2_glob_b2_ncap.x"]]
        try: test(x, 'a2_glob_b2_ncap.x', 4630)
        except NameError: test(None, 'a2_glob_b2_ncap.x', 4631)
        def a2_glob_b2_ncap_delfunc():
            nonlocal x; del x
        a2_glob_b2_ncap_delfunc()
        try: test(x, None, 4635)
        except NameError: test(None, None, 4636)
        x = "a2_glob_b2_ncap.x"
        try: test(x, 'a2_glob_b2_ncap.x', 4638)
        except NameError: test(None, 'a2_glob_b2_ncap.x', 4639)
        del x
        try: test(x, None, 4641)
        except NameError: test(None, None, 4642)
    a2_glob_b2_ncap()
    x = "x"
    try: test(x, 'x', 4645)
    except NameError: test(None, 'x', 4646)
a2_glob()
def a2_loc():
    try: test(x, None, 4649)
    except NameError: test(None, None, 4650)
    class a2_loc_B:
        pass
    class a2_loc_B_use:
        try: test(x, None, 4654)
        except NameError: test(None, None, 4655)
    class a2_loc_B_anno:
        x: str
        try: test(x, 'x', 4658)
        except NameError: test(None, 'x', 4659)
    class a2_loc_B_nloc:
        nonlocal x
        try: test(x, None, 4662)
        except NameError: test(None, None, 4663)
        def a2_loc_B_nloc_setfunc():
            nonlocal x; x = "a2_loc.x"
        a2_loc_B_nloc_setfunc()
        try: test(x, 'a2_loc.x', 4667)
        except NameError: test(None, 'a2_loc.x', 4668)
        def a2_loc_B_nloc_delfunc():
            nonlocal x; del x
        a2_loc_B_nloc_delfunc()
        try: test(x, None, 4672)
        except NameError: test(None, None, 4673)
        x = "a2_loc.x"
        try: test(x, 'a2_loc.x', 4675)
        except NameError: test(None, 'a2_loc.x', 4676)
        del x
        try: test(x, None, 4678)
        except NameError: test(None, None, 4679)
    class a2_loc_B_glob:
        global x
        try: test(x, 'x', 4682)
        except NameError: test(None, 'x', 4683)
        del x
        try: test(x, None, 4685)
        except NameError: test(None, None, 4686)
        def a2_loc_B_glob_setfunc():
            global x; x = "x"
        a2_loc_B_glob_setfunc()
        try: test(x, 'x', 4690)
        except NameError: test(None, 'x', 4691)
        def a2_loc_B_glob_delfunc():
            global x; del x
        a2_loc_B_glob_delfunc()
        try: test(x, None, 4695)
        except NameError: test(None, None, 4696)
        x = "x"
        try: test(x, 'x', 4698)
        except NameError: test(None, 'x', 4699)
    class a2_loc_B_loc:
        try: test(x, 'x', 4701)
        except NameError: test(None, 'x', 4702)
        def a2_loc_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_loc_B_loc.x"
        a2_loc_B_loc_setfunc()
        try: test(x, 'a2_loc_B_loc.x', 4706)
        except NameError: test(None, 'a2_loc_B_loc.x', 4707)
        def a2_loc_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_loc_B_loc_delfunc()
        try: test(x, 'x', 4711)
        except NameError: test(None, 'x', 4712)
        x = "a2_loc_B_loc.x"
        try: test(x, 'a2_loc_B_loc.x', 4714)
        except NameError: test(None, 'a2_loc_B_loc.x', 4715)
        del x
        try: test(x, 'x', 4717)
        except NameError: test(None, 'x', 4718)
    class a2_loc_B_ncap:
        try: test(x, 'x', 4720)
        except NameError: test(None, 'x', 4721)
        def a2_loc_B_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_loc_B_ncap.x"
        a2_loc_B_ncap_setfunc()
        try: test(x, 'a2_loc_B_ncap.x', 4725)
        except NameError: test(None, 'a2_loc_B_ncap.x', 4726)
        def a2_loc_B_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_loc_B_ncap_delfunc()
        try: test(x, 'x', 4730)
        except NameError: test(None, 'x', 4731)
        x = "a2_loc_B_ncap.x"
        try: test(x, 'a2_loc_B_ncap.x', 4733)
        except NameError: test(None, 'a2_loc_B_ncap.x', 4734)
        del x
        try: test(x, 'x', 4736)
        except NameError: test(None, 'x', 4737)
    def a2_loc_b():
        pass
    a2_loc_b()
    def a2_loc_b_use():
        try: test(x, None, 4742)
        except NameError: test(None, None, 4743)
    a2_loc_b_use()
    def a2_loc_b_anno():
        x: str
        try: test(x, None, 4747)
        except NameError: test(None, None, 4748)
    a2_loc_b_anno()
    def a2_loc_b_nloc():
        nonlocal x
        try: test(x, None, 4752)
        except NameError: test(None, None, 4753)
        [x := _ for _ in ["a2_loc.x"]]
        try: test(x, 'a2_loc.x', 4755)
        except NameError: test(None, 'a2_loc.x', 4756)
        def a2_loc_b_nloc_delfunc():
            nonlocal x; del x
        a2_loc_b_nloc_delfunc()
        try: test(x, None, 4760)
        except NameError: test(None, None, 4761)
        x = "a2_loc.x"
        try: test(x, 'a2_loc.x', 4763)
        except NameError: test(None, 'a2_loc.x', 4764)
        del x
        try: test(x, None, 4766)
        except NameError: test(None, None, 4767)
    a2_loc_b_nloc()
    def a2_loc_b_glob():
        global x
        try: test(x, 'x', 4771)
        except NameError: test(None, 'x', 4772)
        del x
        try: test(x, None, 4774)
        except NameError: test(None, None, 4775)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4777)
        except NameError: test(None, 'x', 4778)
        def a2_loc_b_glob_delfunc():
            global x; del x
        a2_loc_b_glob_delfunc()
        try: test(x, None, 4782)
        except NameError: test(None, None, 4783)
        x = "x"
        try: test(x, 'x', 4785)
        except NameError: test(None, 'x', 4786)
    a2_loc_b_glob()
    def a2_loc_b_loc():
        try: test(x, None, 4789)
        except NameError: test(None, None, 4790)
        [x := _ for _ in ["a2_loc_b_loc.x"]]
        try: test(x, 'a2_loc_b_loc.x', 4792)
        except NameError: test(None, 'a2_loc_b_loc.x', 4793)
        def a2_loc_b_loc_delfunc():
            nonlocal x; del x
        a2_loc_b_loc_delfunc()
        try: test(x, None, 4797)
        except NameError: test(None, None, 4798)
        x = "a2_loc_b_loc.x"
        try: test(x, 'a2_loc_b_loc.x', 4800)
        except NameError: test(None, 'a2_loc_b_loc.x', 4801)
        del x
        try: test(x, None, 4803)
        except NameError: test(None, None, 4804)
    a2_loc_b_loc()
    def a2_loc_b_ncap():
        try: test(x, None, 4807)
        except NameError: test(None, None, 4808)
        [x := _ for _ in ["a2_loc_b_ncap.x"]]
        try: test(x, 'a2_loc_b_ncap.x', 4810)
        except NameError: test(None, 'a2_loc_b_ncap.x', 4811)
        def a2_loc_b_ncap_delfunc():
            nonlocal x; del x
        a2_loc_b_ncap_delfunc()
        try: test(x, None, 4815)
        except NameError: test(None, None, 4816)
        x = "a2_loc_b_ncap.x"
        try: test(x, 'a2_loc_b_ncap.x', 4818)
        except NameError: test(None, 'a2_loc_b_ncap.x', 4819)
        del x
        try: test(x, None, 4821)
        except NameError: test(None, None, 4822)
    a2_loc_b_ncap()
    [x := _ for _ in ["a2_loc.x"]]
    try: test(x, 'a2_loc.x', 4825)
    except NameError: test(None, 'a2_loc.x', 4826)
    def a2_loc_delfunc():
        nonlocal x; del x
    a2_loc_delfunc()
    try: test(x, None, 4830)
    except NameError: test(None, None, 4831)
    x = "a2_loc.x"
    try: test(x, 'a2_loc.x', 4833)
    except NameError: test(None, 'a2_loc.x', 4834)
    class a2_loc_B2:
        pass
    class a2_loc_B2_use:
        try: test(x, 'a2_loc.x', 4838)
        except NameError: test(None, 'a2_loc.x', 4839)
    class a2_loc_B2_anno:
        x: str
        try: test(x, 'x', 4842)
        except NameError: test(None, 'x', 4843)
    class a2_loc_B2_nloc:
        nonlocal x
        try: test(x, 'a2_loc.x', 4846)
        except NameError: test(None, 'a2_loc.x', 4847)
        del x
        try: test(x, None, 4849)
        except NameError: test(None, None, 4850)
        def a2_loc_B2_nloc_setfunc():
            nonlocal x; x = "a2_loc.x"
        a2_loc_B2_nloc_setfunc()
        try: test(x, 'a2_loc.x', 4854)
        except NameError: test(None, 'a2_loc.x', 4855)
        def a2_loc_B2_nloc_delfunc():
            nonlocal x; del x
        a2_loc_B2_nloc_delfunc()
        try: test(x, None, 4859)
        except NameError: test(None, None, 4860)
        x = "a2_loc.x"
        try: test(x, 'a2_loc.x', 4862)
        except NameError: test(None, 'a2_loc.x', 4863)
    class a2_loc_B2_glob:
        global x
        try: test(x, 'x', 4866)
        except NameError: test(None, 'x', 4867)
        del x
        try: test(x, None, 4869)
        except NameError: test(None, None, 4870)
        def a2_loc_B2_glob_setfunc():
            global x; x = "x"
        a2_loc_B2_glob_setfunc()
        try: test(x, 'x', 4874)
        except NameError: test(None, 'x', 4875)
        def a2_loc_B2_glob_delfunc():
            global x; del x
        a2_loc_B2_glob_delfunc()
        try: test(x, None, 4879)
        except NameError: test(None, None, 4880)
        x = "x"
        try: test(x, 'x', 4882)
        except NameError: test(None, 'x', 4883)
    class a2_loc_B2_loc:
        try: test(x, 'x', 4885)
        except NameError: test(None, 'x', 4886)
        def a2_loc_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_loc_B2_loc.x"
        a2_loc_B2_loc_setfunc()
        try: test(x, 'a2_loc_B2_loc.x', 4890)
        except NameError: test(None, 'a2_loc_B2_loc.x', 4891)
        def a2_loc_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_loc_B2_loc_delfunc()
        try: test(x, 'x', 4895)
        except NameError: test(None, 'x', 4896)
        x = "a2_loc_B2_loc.x"
        try: test(x, 'a2_loc_B2_loc.x', 4898)
        except NameError: test(None, 'a2_loc_B2_loc.x', 4899)
        del x
        try: test(x, 'x', 4901)
        except NameError: test(None, 'x', 4902)
    class a2_loc_B2_ncap:
        try: test(x, 'x', 4904)
        except NameError: test(None, 'x', 4905)
        def a2_loc_B2_ncap_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_loc_B2_ncap.x"
        a2_loc_B2_ncap_setfunc()
        try: test(x, 'a2_loc_B2_ncap.x', 4909)
        except NameError: test(None, 'a2_loc_B2_ncap.x', 4910)
        def a2_loc_B2_ncap_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_loc_B2_ncap_delfunc()
        try: test(x, 'x', 4914)
        except NameError: test(None, 'x', 4915)
        x = "a2_loc_B2_ncap.x"
        try: test(x, 'a2_loc_B2_ncap.x', 4917)
        except NameError: test(None, 'a2_loc_B2_ncap.x', 4918)
        del x
        try: test(x, 'x', 4920)
        except NameError: test(None, 'x', 4921)
    def a2_loc_b2():
        pass
    a2_loc_b2()
    def a2_loc_b2_use():
        try: test(x, 'a2_loc.x', 4926)
        except NameError: test(None, 'a2_loc.x', 4927)
    a2_loc_b2_use()
    def a2_loc_b2_anno():
        x: str
        try: test(x, None, 4931)
        except NameError: test(None, None, 4932)
    a2_loc_b2_anno()
    def a2_loc_b2_nloc():
        nonlocal x
        try: test(x, 'a2_loc.x', 4936)
        except NameError: test(None, 'a2_loc.x', 4937)
        del x
        try: test(x, None, 4939)
        except NameError: test(None, None, 4940)
        [x := _ for _ in ["a2_loc.x"]]
        try: test(x, 'a2_loc.x', 4942)
        except NameError: test(None, 'a2_loc.x', 4943)
        def a2_loc_b2_nloc_delfunc():
            nonlocal x; del x
        a2_loc_b2_nloc_delfunc()
        try: test(x, None, 4947)
        except NameError: test(None, None, 4948)
        x = "a2_loc.x"
        try: test(x, 'a2_loc.x', 4950)
        except NameError: test(None, 'a2_loc.x', 4951)
    a2_loc_b2_nloc()
    def a2_loc_b2_glob():
        global x
        try: test(x, 'x', 4955)
        except NameError: test(None, 'x', 4956)
        del x
        try: test(x, None, 4958)
        except NameError: test(None, None, 4959)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 4961)
        except NameError: test(None, 'x', 4962)
        def a2_loc_b2_glob_delfunc():
            global x; del x
        a2_loc_b2_glob_delfunc()
        try: test(x, None, 4966)
        except NameError: test(None, None, 4967)
        x = "x"
        try: test(x, 'x', 4969)
        except NameError: test(None, 'x', 4970)
    a2_loc_b2_glob()
    def a2_loc_b2_loc():
        try: test(x, None, 4973)
        except NameError: test(None, None, 4974)
        [x := _ for _ in ["a2_loc_b2_loc.x"]]
        try: test(x, 'a2_loc_b2_loc.x', 4976)
        except NameError: test(None, 'a2_loc_b2_loc.x', 4977)
        def a2_loc_b2_loc_delfunc():
            nonlocal x; del x
        a2_loc_b2_loc_delfunc()
        try: test(x, None, 4981)
        except NameError: test(None, None, 4982)
        x = "a2_loc_b2_loc.x"
        try: test(x, 'a2_loc_b2_loc.x', 4984)
        except NameError: test(None, 'a2_loc_b2_loc.x', 4985)
        del x
        try: test(x, None, 4987)
        except NameError: test(None, None, 4988)
    a2_loc_b2_loc()
    def a2_loc_b2_ncap():
        try: test(x, None, 4991)
        except NameError: test(None, None, 4992)
        [x := _ for _ in ["a2_loc_b2_ncap.x"]]
        try: test(x, 'a2_loc_b2_ncap.x', 4994)
        except NameError: test(None, 'a2_loc_b2_ncap.x', 4995)
        def a2_loc_b2_ncap_delfunc():
            nonlocal x; del x
        a2_loc_b2_ncap_delfunc()
        try: test(x, None, 4999)
        except NameError: test(None, None, 5000)
        x = "a2_loc_b2_ncap.x"
        try: test(x, 'a2_loc_b2_ncap.x', 5002)
        except NameError: test(None, 'a2_loc_b2_ncap.x', 5003)
        del x
        try: test(x, None, 5005)
        except NameError: test(None, None, 5006)
    a2_loc_b2_ncap()
    del x
    try: test(x, None, 5009)
    except NameError: test(None, None, 5010)
a2_loc()
def a2_ncap():
    try: test(x, None, 5013)
    except NameError: test(None, None, 5014)
    class a2_ncap_B:
        pass
    class a2_ncap_B_glob:
        global x
        try: test(x, 'x', 5019)
        except NameError: test(None, 'x', 5020)
        del x
        try: test(x, None, 5022)
        except NameError: test(None, None, 5023)
        def a2_ncap_B_glob_setfunc():
            global x; x = "x"
        a2_ncap_B_glob_setfunc()
        try: test(x, 'x', 5027)
        except NameError: test(None, 'x', 5028)
        def a2_ncap_B_glob_delfunc():
            global x; del x
        a2_ncap_B_glob_delfunc()
        try: test(x, None, 5032)
        except NameError: test(None, None, 5033)
        x = "x"
        try: test(x, 'x', 5035)
        except NameError: test(None, 'x', 5036)
    class a2_ncap_B_loc:
        try: test(x, 'x', 5038)
        except NameError: test(None, 'x', 5039)
        def a2_ncap_B_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_ncap_B_loc.x"
        a2_ncap_B_loc_setfunc()
        try: test(x, 'a2_ncap_B_loc.x', 5043)
        except NameError: test(None, 'a2_ncap_B_loc.x', 5044)
        def a2_ncap_B_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_ncap_B_loc_delfunc()
        try: test(x, 'x', 5048)
        except NameError: test(None, 'x', 5049)
        x = "a2_ncap_B_loc.x"
        try: test(x, 'a2_ncap_B_loc.x', 5051)
        except NameError: test(None, 'a2_ncap_B_loc.x', 5052)
        del x
        try: test(x, 'x', 5054)
        except NameError: test(None, 'x', 5055)
    def a2_ncap_b():
        pass
    a2_ncap_b()
    def a2_ncap_b_glob():
        global x
        try: test(x, 'x', 5061)
        except NameError: test(None, 'x', 5062)
        del x
        try: test(x, None, 5064)
        except NameError: test(None, None, 5065)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 5067)
        except NameError: test(None, 'x', 5068)
        def a2_ncap_b_glob_delfunc():
            global x; del x
        a2_ncap_b_glob_delfunc()
        try: test(x, None, 5072)
        except NameError: test(None, None, 5073)
        x = "x"
        try: test(x, 'x', 5075)
        except NameError: test(None, 'x', 5076)
    a2_ncap_b_glob()
    def a2_ncap_b_loc():
        try: test(x, None, 5079)
        except NameError: test(None, None, 5080)
        [x := _ for _ in ["a2_ncap_b_loc.x"]]
        try: test(x, 'a2_ncap_b_loc.x', 5082)
        except NameError: test(None, 'a2_ncap_b_loc.x', 5083)
        def a2_ncap_b_loc_delfunc():
            nonlocal x; del x
        a2_ncap_b_loc_delfunc()
        try: test(x, None, 5087)
        except NameError: test(None, None, 5088)
        x = "a2_ncap_b_loc.x"
        try: test(x, 'a2_ncap_b_loc.x', 5090)
        except NameError: test(None, 'a2_ncap_b_loc.x', 5091)
        del x
        try: test(x, None, 5093)
        except NameError: test(None, None, 5094)
    a2_ncap_b_loc()
    [x := _ for _ in ["a2_ncap.x"]]
    try: test(x, 'a2_ncap.x', 5097)
    except NameError: test(None, 'a2_ncap.x', 5098)
    def a2_ncap_delfunc():
        nonlocal x; del x
    a2_ncap_delfunc()
    try: test(x, None, 5102)
    except NameError: test(None, None, 5103)
    x = "a2_ncap.x"
    try: test(x, 'a2_ncap.x', 5105)
    except NameError: test(None, 'a2_ncap.x', 5106)
    class a2_ncap_B2:
        pass
    class a2_ncap_B2_glob:
        global x
        try: test(x, 'x', 5111)
        except NameError: test(None, 'x', 5112)
        del x
        try: test(x, None, 5114)
        except NameError: test(None, None, 5115)
        def a2_ncap_B2_glob_setfunc():
            global x; x = "x"
        a2_ncap_B2_glob_setfunc()
        try: test(x, 'x', 5119)
        except NameError: test(None, 'x', 5120)
        def a2_ncap_B2_glob_delfunc():
            global x; del x
        a2_ncap_B2_glob_delfunc()
        try: test(x, None, 5124)
        except NameError: test(None, None, 5125)
        x = "x"
        try: test(x, 'x', 5127)
        except NameError: test(None, 'x', 5128)
    class a2_ncap_B2_loc:
        try: test(x, 'x', 5130)
        except NameError: test(None, 'x', 5131)
        def a2_ncap_B2_loc_setfunc():
            inspect.stack()[1].frame.f_locals["x"] = "a2_ncap_B2_loc.x"
        a2_ncap_B2_loc_setfunc()
        try: test(x, 'a2_ncap_B2_loc.x', 5135)
        except NameError: test(None, 'a2_ncap_B2_loc.x', 5136)
        def a2_ncap_B2_loc_delfunc():
            del inspect.stack()[1].frame.f_locals["x"]
        a2_ncap_B2_loc_delfunc()
        try: test(x, 'x', 5140)
        except NameError: test(None, 'x', 5141)
        x = "a2_ncap_B2_loc.x"
        try: test(x, 'a2_ncap_B2_loc.x', 5143)
        except NameError: test(None, 'a2_ncap_B2_loc.x', 5144)
        del x
        try: test(x, 'x', 5146)
        except NameError: test(None, 'x', 5147)
    def a2_ncap_b2():
        pass
    a2_ncap_b2()
    def a2_ncap_b2_glob():
        global x
        try: test(x, 'x', 5153)
        except NameError: test(None, 'x', 5154)
        del x
        try: test(x, None, 5156)
        except NameError: test(None, None, 5157)
        [x := _ for _ in ["x"]]
        try: test(x, 'x', 5159)
        except NameError: test(None, 'x', 5160)
        def a2_ncap_b2_glob_delfunc():
            global x; del x
        a2_ncap_b2_glob_delfunc()
        try: test(x, None, 5164)
        except NameError: test(None, None, 5165)
        x = "x"
        try: test(x, 'x', 5167)
        except NameError: test(None, 'x', 5168)
    a2_ncap_b2_glob()
    def a2_ncap_b2_loc():
        try: test(x, None, 5171)
        except NameError: test(None, None, 5172)
        [x := _ for _ in ["a2_ncap_b2_loc.x"]]
        try: test(x, 'a2_ncap_b2_loc.x', 5174)
        except NameError: test(None, 'a2_ncap_b2_loc.x', 5175)
        def a2_ncap_b2_loc_delfunc():
            nonlocal x; del x
        a2_ncap_b2_loc_delfunc()
        try: test(x, None, 5179)
        except NameError: test(None, None, 5180)
        x = "a2_ncap_b2_loc.x"
        try: test(x, 'a2_ncap_b2_loc.x', 5182)
        except NameError: test(None, 'a2_ncap_b2_loc.x', 5183)
        del x
        try: test(x, None, 5185)
        except NameError: test(None, None, 5186)
    a2_ncap_b2_loc()
    del x
    try: test(x, None, 5189)
    except NameError: test(None, None, 5190)
a2_ncap()
del x
try: test(x, None, 5193)
except NameError: test(None, None, 5194)
