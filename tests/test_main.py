"""
test_main
~~~~~~~~~

Unit tests for the mainline of the `charex` package.
"""
import sys

import charex.__main__ as m


# Test denormal mode.
def test_denormal(capsys):
    """Called with a base string, denormal mode should print the
    denormalizations for the base string to stdout.
    """
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
    cmd = (
        'python -m charex',
        'denormal',
        '<->'
    )
    orig_cmd = sys.argv
    sys.argv = cmd
    m.parse_invocation()
    captured = capsys.readouterr()
    assert captured.out == exp
    sys.argv = orig_cmd
