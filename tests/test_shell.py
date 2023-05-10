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
    with open('tests/data/charset_mode_r.txt') as fh:
        exp = fh.read()
    shell = sh.Shell()
    cmd = 'cd A'
    shell.onecmd(cmd)
    captured = capsys.readouterr()
    assert captured.out == exp
