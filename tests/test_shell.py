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
    shell = sh.Shell()
    cmd = 'cd 0x41'
    shell.onecmd(cmd)
    captured = capsys.readouterr()
    assert captured.out == exp


def test_cd_binary(capsys):
    """Invoked with a binary string, `cd` returns the character for
    that address in each registered character set. A binary string is
    declared by starting the string with "0b".
    """
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()
    shell = sh.Shell()
    cmd = 'cd 0b01000001'
    shell.onecmd(cmd)
    captured = capsys.readouterr()
    assert captured.out == exp


def test_cd_string(capsys):
    """Invoked with a character, `cd` returns the character for
    that character's UTF-8 address in each registered character set.
    """
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()
    shell = sh.Shell()
    cmd = 'cd A'
    shell.onecmd(cmd)
    captured = capsys.readouterr()
    assert captured.out == exp


# Tests for ce.
def test_ce(capsys):
    """Invoked with a character, `ce` returns the address for
    that character in each registered character set.
    """
    with open('tests/data/charset_mode_r.txt') as fh:
        exp = fh.read()
    shell = sh.Shell()
    cmd = 'ce A'
    shell.onecmd(cmd)
    captured = capsys.readouterr()
    assert captured.out == exp


# Tests for cl.
def test_cl(capsys):
    """Invoked, `cl` returns the list of registered character sets with
    descriptions.
    """
    with open('tests/data/charsetlist_d.txt') as fh:
        exp = fh.read()
    shell = sh.Shell()
    cmd = 'cl'
    shell.onecmd(cmd)
    captured = capsys.readouterr()
    assert captured.out == exp
