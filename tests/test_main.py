"""
test_main
~~~~~~~~~

Unit tests for the mainline of the `charex` package.
"""
import sys

import pytest as pt

import charex.__main__ as m


# Test charset mode.
def test_charset(capsys):
    """Called with an hex string, charset mode should return the character
    or characters that hex string becomes in each of the known character
    sets.
    """
    # Expected result.
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()

    # Test setup.
    cmd = (
        'python -m charex',
        'charset',
        '0x41'
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


def test_charset_binary(capsys):
    """Called with -b, charset mode should interpret the base string as
    binary and return the character or characters that hex string becomes
    in each of the known character sets.
    """
    # Expected result.
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()

    # Test setup.
    cmd = (
        'python -m charex',
        'charset',
        '0b01000001',
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


def test_charset_code_point(capsys):
    """Called with -c followed by a recognized character set, charset
    mode should interpret the base string as binary and return the
    character or characters that hex string becomes in each of the
    known character sets.
    """
    # Expected result.
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()

    # Test setup.
    cmd = (
        'python -m charex',
        'charset',
        'A',
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


def test_charset_control_character(capsys):
    """Called with an hex string, charset mode should return the character
    or characters that hex string becomes in each of the known character
    sets. If the hex string becomes a control character, print the symbol
    for that character rather than the character itself.
    """
    # Expected result.
    with open('tests/data/charset_mode_0a.txt') as fh:
        exp = fh.read()

    # Test setup.
    cmd = (
        'python -m charex',
        'charset',
        '0x0a'
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


def test_charset_no_character(capsys):
    """Called with an hex string, charset mode should return the character
    or characters that hex string becomes in each of the known character
    sets. If some character sets do not have characters for the given
    address, that should be indicated in the output.
    """
    # Expected result.
    with open('tests/data/charset_mode_e9.txt') as fh:
        exp = fh.read()

    # Test setup.
    cmd = (
        'python -m charex',
        'charset',
        '0xe9'
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


def test_charset_reverse(capsys):
    """Called with an character and -r, charset mode should return the
    address for the character in each of the registered character sets.
    """
    # Expected result.
    with open('tests/data/charset_mode_r.txt') as fh:
        exp = fh.read()

    # Test setup.
    cmd = (
        'python -m charex',
        'charset',
        'A',
        '-r',
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


# Test charsetlist mode.
def test_charsetlist(capsys):
    """When invoked, charsetlist mode should return a list of registered
    character set codecs.
    """
    # Expected result.
    with open('tests/data/charsetlist.txt') as fh:
        exp = fh.read()

    # Test setup.
    cmd = (
        'python -m charex',
        'charsetlist'
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


def test_charsetlist_description(capsys):
    """When invoked with -d, charsetlist mode should return a list of
    registered character set codecs and a brief description of each
    one.
    """
    # Expected result.
    with open('tests/data/charsetlist_d.txt') as fh:
        exp = fh.read()

    # Test setup.
    cmd = (
        'python -m charex',
        'charsetlist',
        '-d'
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


# Test denormal mode.
def test_denormal(capsys):
    """Called with a base string, denormal mode should print the
    denormalizations for the base string to stdout.
    """
    # Expected result.
    exp = (
        '\ufe64\ufe63\ufe65\n'
        '\ufe64\ufe63\uff1e\n'
        '\ufe64\uff0d\ufe65\n'
        '\ufe64\uff0d\uff1e\n'
        '\uff1c\ufe63\ufe65\n'
        '\uff1c\ufe63\uff1e\n'
        '\uff1c\uff0d\ufe65\n'
        '\uff1c\uff0d\uff1e\n'
        '\n'
    )

    # Test setup.
    cmd = (
        'python -m charex',
        'denormal',
        '<->'
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


def test_denormal_number(capsys):
    """Called with -n and an integer, denormal mode should return no
    more than that number of results.
    """
    # Expected result.
    exp = (
        '\ufe64\ufe63\ufe65\n'
        '\ufe64\ufe63\uff1e\n'
        '\ufe64\uff0d\ufe65\n'
        '\ufe64\uff0d\uff1e\n'
        '\n'
    )

    # Test setup.
    cmd = (
        'python -m charex',
        'denormal',
        '<->',
        '-n', '4'
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


def test_denormal_random(capsys):
    """Called with -r, denormal mode should return a randomly
    denormalized string.
    """
    # Expected result.
    exp = (
        '﹤－﹥\n'
        '\n'
    )

    # Test setup.
    cmd = (
        'python -m charex',
        'denormal',
        '<->',
        '-r',
        '-s', 'spam'
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


# Test details mode.
def test_details(capsys):
    """Called with a character, details mode should the details for the
    character.
    """
    # Expected result.
    with open('tests/data/details_mode_A.txt') as fh:
        exp = fh.read()

    # Test setup.
    cmd = (
        'python -m charex',
        'details',
        'A'
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


# Test escape mode.
def test_escape(capsys):
    """Called with a base string, escape mode should escape the string
    using the "url" scheme and display the escaped string.
    """
    # Expected result.
    exp = '%41\n\n'

    # Test setup.
    cmd = (
        'python -m charex',
        'escape',
        'A',
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


def test_escape_with_scheme(capsys):
    """Invoked with a base string and a scheme, escape mode should
    escape the string using the scheme and display the escaped string.
    """
    # Expected result.
    exp = '&#65;\n\n'

    # Test setup.
    cmd = (
        'python -m charex',
        'escape',
        'A',
        '-s', 'html',
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd


# Test esclist mode.
def test_esclist(capsys):
    """Whne invoked, esclist mode returns a list of the registered
    escape modes.
    """
    # Expected result.
    exp = (
        'cu\n'
        'html\n'
        'url\n'
        '\n'
    )

    # Test setup.
    cmd = (
        'python -m charex',
        'esclist',
    )
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.parse_invocation()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd
