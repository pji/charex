"""
test_shell
~~~~~~~~~~

Unit tests for :mod:`charex.shell`.
"""
from charex import shell as sh


# Tests for cd.
def test_cd(capsys):
    """Invoked with a hex string, `cd` returns the character for
    that address in each registered character set.
    """
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()
    shell = sh.Shell()
    cmd = 'cd 41'
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
