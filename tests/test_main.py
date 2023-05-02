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
        '41'
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
        '01000001',
        '-b'
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
        '-c', 'utf8'
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
        '0a'
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
