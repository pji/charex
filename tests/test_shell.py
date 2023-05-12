"""
test_shell
~~~~~~~~~~

Unit tests for :mod:`charex.shell`.
"""
from charex import shell as sh


# Tests for cd.
def test_cd(capsys):
    """Invoked with a hex string, `cd` returns the character for
    that address in each registered character set. A hex string is
    declared by starting the string with "0x".
    """
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()
    cmd = 'cd 0x41'
    shell_test(exp, cmd, capsys)


def test_cd_binary(capsys):
    """Invoked with a binary string, `cd` returns the character for
    that address in each registered character set. A binary string is
    declared by starting the string with "0b".
    """
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()
    cmd = 'cd 0b01000001'
    shell_test(exp, cmd, capsys)


def test_cd_string(capsys):
    """Invoked with a character, `cd` returns the character for
    that character's UTF-8 address in each registered character set.
    """
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()
    cmd = 'cd A'
    shell_test(exp, cmd, capsys)


# Tests for ce.
def test_ce(capsys):
    """Invoked with a character, `ce` returns the address for
    that character in each registered character set.
    """
    with open('tests/data/charset_mode_r.txt') as fh:
        exp = fh.read()
    cmd = 'ce A'
    shell_test(exp, cmd, capsys)


# Tests for cl.
def test_cl(capsys):
    """Invoked, `cl` returns the list of registered character sets."""
    with open('tests/data/charsetlist.txt') as fh:
        exp = fh.read()
    cmd = 'cl'
    shell_test(exp, cmd, capsys)


def test_cl_description(capsys):
    """Invoked with "-d", `cl` returns the list of registered character
    sets with descriptions.
    """
    with open('tests/data/charsetlist_d.txt') as fh:
        exp = fh.read()
    cmd = 'cl -d'
    shell_test(exp, cmd, capsys)


# Tests for ct.
def test_ct(capsys):
    """Invoked with a normalization form and a base string, ct mode
    should print the number of denormalizations using the given form to
    stdout.
    """
    exp = '120,270,240\n\n'
    cmd = 'ct nfkd <script>'
    shell_test(exp, cmd, capsys)


def test_ct_maxdepth(capsys):
    """Invoked with "-m" and an integer, ct mode limit the number of
    denormalizations per character to the given integer and print the
    number of denormalizations using the given form to stdout.
    """
    exp = '256\n\n'
    cmd = 'ct nfkd <script> -m 2'
    shell_test(exp, cmd, capsys)


# Utility functions.
def shell_test(exp, cmd, capsys):
    """Test shell invocation."""
    shell = sh.Shell()
    shell.onecmd(cmd)
    captured = capsys.readouterr()
    assert captured.out == exp
