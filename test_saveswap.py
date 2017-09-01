"""Test suite for saveswap.py

As this relies on helpers from py.test, it must be run with ``py.test``.
"""

from __future__ import (absolute_import, division, print_function,
                        with_statement, unicode_literals)

__author__ = "Stephan Sokolow"
__license__ = "MIT"
__appname__ = "N64-Saveswap"
__version__ = "0.0pre0"

import os, sys
from contextlib import contextmanager

from saveswap import (calculate_padding, byteswap, main, process_path,
                      FileIncomplete, FileTooBig)

@contextmanager
def set_argv(args):
    """Context manager to temporarily modify sys.argv"""
    old_argv = sys.argv
    try:
        sys.argv = [sys.argv[0]] + [str(x) for x in args]
        yield
    finally:
        sys.argv = old_argv

def test_calculate_padding(tmpdir):
    """Test that calculate_padding works as expected"""
    import pytest
    test_file = tmpdir.join("fake_dump")

    for start, expected in (
            (100, 512), (500, 2048), (1000, 32768), (10000, 131072)):
        test_file.write("1234" * start)
        assert calculate_padding(str(test_file)) == expected

    test_file.write("1234" * 100000)
    with pytest.raises(FileTooBig):
        calculate_padding(str(test_file))

def test_byteswap(tmpdir):
    """Test that byteswap produces the expected output"""
    test_file = tmpdir.join("fake_dump")

    # Test the various modes
    for options, expected in (
            ({}, "4321"),
            ({'swap_bytes': False}, "3412"),
            ({'swap_words': False}, "2143"),
            ({'swap_bytes': False, 'swap_words': False}, "1234")):
        test_file.write("1234" * 10)
        byteswap(str(test_file), **options)
        assert test_file.read() == expected * 10

def test_byteswap_padding(tmpdir):
    """Test that byteswap pads as intended"""
    test_file = tmpdir.join("fake_dump")
    test_file.write("1234" * 100000)
    byteswap(str(test_file), pad_to=500000)
    assert test_file.read() == ("4321" * 100000) + ("\x00" * 100000)

def test_byteswap_with_incomplete(tmpdir):
    """Test that byteswap reacts properly to file sizes with remainders

    (ie. file sizes that are not evenly divisible by 2 or 4)
    """
    import pytest
    test_file = tmpdir.join("fake_dump")

    # Define a function which will be called for each combination of inputs
    def test_callback(_bytes, _words, pad_to):
        """Function called many times by _vary_check_swap_inputs"""
        # Test that both types of swapping error out on odd-numbered lengths
        test_file.write("12345")
        if _bytes or _words:
            with pytest.raises(FileIncomplete):
                byteswap(str(test_file), _bytes, _words, pad_to)

        test_file.write("123456")
        if _words:
            with pytest.raises(FileIncomplete):
                byteswap(str(test_file), _bytes, _words, pad_to)
        else:
            byteswap(str(test_file), False, _words, pad_to)

    # Let _vary_check_swap_inputs call test_callback once for each combination
    _vary_check_swap_inputs(test_callback)

def test_process_path_autopad_error(tmpdir):
    """Test that process_path reacts to pad_to=None properly on error"""
    import pytest
    test_file = tmpdir.join("fake_dump")
    backup_path = str(test_file) + '.bak'

    test_file.write("1234" * 100000)
    assert not os.path.exists(backup_path)
    with pytest.raises(FileTooBig):
        process_path(str(test_file), pad_to=None)
    assert test_file.read() == "1234" * 100000  # Unchanged on error
    assert not os.path.exists(backup_path)      # No backup on oversize

def test_process_path_padding(tmpdir):
    """Test that process_path pads properly"""
    import pytest
    test_file = tmpdir.join("fake_dump")
    backup_path = str(test_file) + '.bak'

    test_file.write("1234" * 100000)
    process_path(str(test_file), pad_to=500000)
    assert test_file.read() == ("4321" * 100000) + ("\x00" * 100000)
    assert os.path.exists(backup_path)

def test_process_path_nopad(tmpdir):
    """Test that process_path reacts to pad_to=0 properly"""
    import pytest
    test_file = tmpdir.join("fake_dump")
    backup_path = str(test_file) + '.bak'

    test_file.write("1234" * 100000)
    process_path(str(test_file), pad_to=0)
    assert test_file.read() == "4321" * 100000
    assert os.path.exists(backup_path)

def check_main_retcode(args, code):
    """Helper for testing return codes from main()"""
    try:
        with set_argv(args):
            main()
    except SystemExit as err:
        assert err.code == code

def test_main_works(tmpdir):
    """Functional test for basic main() use"""
    test_file = tmpdir.join("fake_dump")
    backup_path = str(test_file) + '.bak'

    # Test successful runs
    for pat_reps, options, expect_pat, expect_len, backup in (
            (500, [], '4321', 2048, False),
            (100, ['--swap-mode=words-only'], '3412', 512, True),
            (1000, ['--swap-mode=bytes-only'], '2143', 32768, False),
            (1000, ['--force-padding=0',
                    '--swap-mode=bytes-only'], '2143', 4000, False),
            (100000, ['--force-padding=500000'], '4321', 500000, True)):

        bkopt = [] if backup else ['--no-backup']
        test_file.write("1234" * pat_reps)
        with set_argv(options + bkopt + [test_file]):
            main()
        assert test_file.read() == (expect_pat * pat_reps) + (
            "\x00" * (expect_len - (4 * pat_reps)))
        if backup:
            assert os.path.exists(backup_path)
            os.remove(backup_path)

def test_main_missing_file(tmpdir):
    """Functional test for main() with nonexistant path"""
    missing_path = str(tmpdir.join("missing_file"))
    check_main_retcode([missing_path], 10)
    assert not os.path.exists(missing_path + '.bak')

def test_main_error_returns(tmpdir):
    """Functional test for main() with erroring input"""
    test_file = tmpdir.join("fake_dump")
    backup_path = str(test_file) + '.bak'

    assert not os.path.exists(backup_path)
    test_file.write("1234" * 100000)  # Too big
    check_main_retcode([test_file], 20)
    assert not os.path.exists(backup_path)

    test_file.write("12345")          # Not evenly disible by 2
    check_main_retcode([test_file], 30)
    # TODO: Fix the code so the backup is removed on this failure

def _vary_check_swap_inputs(callback):
    """Helper to avoid duplicating stuff within test_byteswap_with_incomplete

    You want to be careful about this, because the number of tests run goes up
    exponentially, but with small numbers of combinations, it's very useful.
    """
    for _bytes in (True, False):
        for _words in (True, False):
            for _padding in (0, 1000, 2048):
                callback(_bytes, _words, _padding)
