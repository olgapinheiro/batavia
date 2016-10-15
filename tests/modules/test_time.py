from ..utils import TranspileTestCase, adjust, SAMPLE_DATA
import unittest


class TimeTests(TranspileTestCase):
    @unittest.expectedFailure
    def test_time(self):
        self.assertCodeExecution("""
            import time

            # Demonstrate that we're getting the same type...
            print(type(time.time()))

            # ...and that type is infact a float.
            print(isinstance(time.time(), float))

            print('Done.')
            """)

    def test_sleep(self):
        self.assertCodeExecution("""
            import time
            time.sleep(.1)
            print('Done.')
            """)

    def test_sleep_negative(self):
        self.assertCodeExecution("""
            import time
            try:
                time.sleep(-1)
            except ValueError as err:
                print(err)
            print('Done.')
            """)

    def test_struct_time_valid(self):
        """
        valid construction
        """

        seed = list(range(1, 10))
        sequences = (
            bytes(seed),
            dict(zip(seed, seed)),
            frozenset(seed),
            seed,
            range(1, 10),
            set(seed),
            ''.join([str(i) for i in seed]),
            tuple(seed)
        )

        setup= adjust("""
        print('>>> import time')
        import time
        """)
        sequence_tests = [struct_time_setup(seq) for seq in sequences]
        test_str = ''.join(sequence_tests)
        self.assertCodeExecution(test_str)

    @unittest.expectedFailure
    def test_struct_time_bad_types(self):
        """
        currently bytearray will break the constructor
        """

        setup = adjust("""
        print('>>> import time')
        import time
        """)
        test_str = setup + adjust(struct_time_setup(bytearray([1]*9)))
        self.assertCodeExecution(test_str)

    def test_struct_time_valid_lengths(self):
        """
        length 9, 10, 11 are acceptable
        """

        setup= adjust("""
        print('>>> import time')
        import time
        """)
        sequence_tests = [struct_time_setup([1] * size) for size in range(9, 12)]
        test_str = ''.join(sequence_tests)
        self.assertCodeExecution(test_str)

    def test_struct_time_invalid(self):
        """
        invalid construction due to bad type
        """

        bad_types = [
            True,
            0j,
            1,
            None,
            NotImplemented
        ]

        setup= adjust("""
        print('>>> import time')
        import time
        """)
        sequence_tests = [struct_time_setup(seq) for seq in bad_types]
        test_str = ''.join(sequence_tests)
        self.assertCodeExecution(test_str)


    def test_struct_time_too_short(self):
        """
        sequence less than length 9 is passed
        should raise an index error
        """
        self.assertCodeExecution(struct_time_setup([1]*8))


    def test_struct_time_too_long(self):
        """
        sequence longer than length 9 is allowed
        """
        self.assertCodeExecution(struct_time_setup([1]*12))

    def test_struct_time_attrs(self):
        """
        tests for struct_time attributes
        """

        setup = struct_time_setup()

        fields = ['n_fields', 'n_unnamed_fields', 'n_sequence_fields', 'tm_year', 'tm_mon', 'tm_mday', 'tm_hour', 'tm_min',
                  'tm_sec', 'tm_wday', 'tm_yday', 'tm_isdst', 'tm_zone', 'tm_gmtoff']
        test_strs = [adjust("""
            print('>>> st.{attr}')
            print(st.{attr})
        """.format(attr=attr)) for attr in fields]

        self.assertCodeExecution(setup + ''.join(test_strs))

    def test_get_item(self):
        """
        tries __getitem__ for index -12-12
        """

        setup = struct_time_setup([1] * 11)
        get_indecies = [adjust("""
        print('>>> st[{i}]')
        print(st[{i}])
        """)for i in range(-12, 13)]

        self.assertCodeExecution(setup + ''.join(get_indecies))

    def test_struct_time_str(self):
        """
        tests the str method
        """

        test_str = struct_time_setup()
        test_str += adjust("""
        print('>>> str(st)')
        print(str(st))
        """)

        self.assertCodeExecution(adjust(test_str))

    def test_struct_time_repr(self):
        """
        tests the repr method
        """

        test_str = struct_time_setup()
        test_str += adjust("""
        print('>>> repr(st)')
        print(repr(st))
        """)

        self.assertCodeExecution(adjust(test_str))

    # TESTS FOR MKTIME
    def test_mktime(self):
        """
        tests the happy path for the mktime constructor
        """

        seq = (1970, 1, 1, 0, 0, 0, 0, 0, 0)

        test_str = adjust("""
        print('>>> import time')
        import time
        print('>>> seq = {seq}')
        seq = {seq}
        print(">>> time.mktime({seq})")
        print(time.mktime(seq))
        #################################
        print(">>> seq = time.struct_time({seq})")
        seq = time.struct_time({seq})
        print(">>> time.mktime(seq)")
        print(time.mktime(seq))
        """).format(seq=str(seq))

        self.assertCodeExecution(test_str)

    def test_mktime_args(self):
        """
        alter arguments 0-6 one by one
        """

        test_str = adjust("""
        print('>>> import time')
        import time
        """)
        seed = [1970, 1, 1, 0, 0, 0, 0, 0, -1]
        for i in range(7):
            seq = seed[:]
            if i == 0:
                seq[i] = 1999    # change the year
            else:
                seq[i] = 5  # change something else
                if i == 1:
                    seq[8] = 1  # change dst value if needed

            test_str += mktime_setup(str(tuple(seq)))

        self.assertCodeExecution(test_str)


    def test_mktime_dst(self):
        """
        tests with each month of the year
        """

        seed = [1970, 1, 1, 0, 0, 0, 0, 0, -1]

        test_str = adjust("""
        print('>>> import time')
        import time
        """)
        for month in range(1, 13):
            seq = seed[:]
            seq[1] = month
            if month <= 3 or month == 12:
                seq[8] = 0  # dst off
            else:
                seq[8] = 1  # dst on
            test_str += adjust("""
            print('trying month {}')
            """.format(month))
            test_str += mktime_setup(str(tuple(seq)))

        self.assertCodeExecution(test_str)


    def test_mktime_bad_input(self):
        """
        When the argument passed is not tuple or struct_time.
        """

        seed = (1970, 1, 1, 0, 0, 0, 0, 0, 0)

        data = (
            False,
            1j,
            {key: key for key in seed},
            1.2,
            frozenset(seed),
            1,
            list(seed),
            range(1,2,3),
            set(seed),
            slice(1,2,3),
            '123456789',
            None,
            NotImplemented
        )

        test_str = adjust("""
        print('>>> import time')
        import time
        """)

        tests = [mktime_setup(str(d)) for d in data]
        test_str += ''.join(tests)

        self.assertCodeExecution(test_str)

    def test_mktime_non_integer_types(self):
        """
        Tests behavior when non integer types are part of the sequence passed
        """

        test_str = adjust("""
        print('>>> import time')
        import time
        """)

        strange_types = [SAMPLE_DATA[type][0] for type in SAMPLE_DATA if type != 'int']

        tests = [ mktime_setup(str((1970, t, 1, 2, 0, 0, 0, 0, 0))) for t in strange_types]
        test_str += ''.join(tests)

        self.assertCodeExecution(test_str)

    def test_mktime_seq_wrong_length(self):
        """
        Sequence has the wrong length
        """

        seq = (1970, 1, 1, 0, 0, 0, 0, 0)  # length == 8

        test_str = adjust("""
        print('>>> import time')
        import time
        """)

        test_str += mktime_setup(str(seq))
        self.assertCodeExecution(test_str)

    def test_mktime_wrong_arg_count(self):
        """
        Called with the wrong number of args
        """

        test_str = adjust("""
        print('>>> import time')
        import time
        print('>>> time.mktime()')
        print(time.mktime())
        ############################
        print('>>> time.mktime(1,2)')
        print(time.mktime(1,2))
        """)

        self.assertCodeExecution(test_str)

    def test_mktime_too_early(self):
        """
        tests OverflowError on dates earlier than an arbitrarily defined date 1900-01-01

        Because the CPython implementation of mktime varies across platforms, this likely won't match behavior
        regarding the smallest possible year that can be entered.
        """

        set_up = adjust("""
        print('>>> import time')
        import time
        """)

        bad_years = (-1970, 70, 1899)

        for year in bad_years:
            test_str = set_up + mktime_setup(str((year, 1, 1, 0, 0, 0, 0, 0, 0)))

            # NOTE: because each example will raise an error, a new VM must be used for each example.
            self.assertJavaScriptExecution(test_str,
                                           js={},
                                           run_in_function=False,
                                           out="""
                >>> import time
                >>> time.mktime(({}, 1, 1, 0, 0, 0, 0, 0, 0))
                ### EXCEPTION ###
                OverflowError: mktime argument out of range
                    test.py:4
                """.format(year))

    def test_mktime_too_late(self):
        """
        tests that the year given is too large. mktime will fail when the date passed to the javascript Date constructor
        is too large per ECMA spec
        source: http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.1
        """

        test_str = adjust("""
        print('>>> import time')
        import time
        """)

        seed = [275760, 9, 0, 0, 0, 0, 0, 0, 1]

        for day in range(12, 14):
            seq = seed[:]
            seq[2] = day
            test_str += mktime_setup(str(tuple(seq)))

        self.assertJavaScriptExecution(test_str,
                                       js={},
                                       run_in_function=False,
                                       out="""
        >>> import time
        >>> time.mktime((275760, 9, 12, 0, 0, 0, 0, 0, 1))
        8639999928000.0
        >>> time.mktime((275760, 9, 13, 0, 0, 0, 0, 0, 1))
        ### EXCEPTION ###
        OverflowError: signed integer is greater than maximum
            test.py:6
        """)


    def test_mktime_no_overflow_error(self):
        """
        years that will not throw an OverflowError
        """

        test_str = adjust("""
        print('>>> import time')
        import time
        """)

        good_years = (1900, 1970, 2016)
        sequences = [mktime_setup(str((year, 1, 1, 0, 0, 0, 0, 0, 0))) for year in good_years]

        test_str += ''.join(sequences)
        self.assertJavaScriptExecution(test_str,
                                       js={},
                                       out="""
            >>> import time
            >>> time.mktime((1900, 1, 1, 0, 0, 0, 0, 0, 0))
            -2208970800.0
            >>> time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))
            18000
            >>> time.mktime((2016, 1, 1, 0, 0, 0, 0, 0, 0))
            1451624400.0
            """)

def struct_time_setup(seq = [1] * 9):
    """
    returns a string to set up a struct_time with seq the struct_time constructor
    :param seq: a valid sequence
    """

    test_str = adjust("""
    print("constructing struct_time with {type_name}")
    print(">>> st = time.struct_time({seq})")
    st = time.struct_time({seq})
    print('>>> st')
    print(st)
    """).format(type_name=type(seq), seq=seq)

    return test_str

def mktime_setup(seq):
    """
    :param seq: a string representation of a sequence
    :return: a test_string to call mktime based on seq
    """
    test_str = adjust("""
    print('''>>> time.mktime({seq})''')
    print(time.mktime({seq}))
    """).format(seq=seq)

    return test_str