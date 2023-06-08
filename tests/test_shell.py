"""
test_shell
~~~~~~~~~~

Unit tests for :mod:`charex.shell`.
"""
from charex import escape as esc
from charex import normal as nl
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


# Test dn mode.
def test_dn(capsys):
    """Invoked with a normalization form and a base string, dn mode
    should print the denormalizations for the base string to stdout.
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
    cmd = (
        'dn '
        'nfkd '
        '<->'
    )
    shell_test(exp, cmd, capsys)


def test_dn_number(capsys):
    """Invoked with -n and an integer, dn mode should return no
    more than that number of results.
    """
    exp = (
        '\ufe64\ufe63\ufe65\n'
        '\n'
    )
    cmd = (
        'dn '
        'nfkd '
        '<-> '
        '-m 1'
    )
    shell_test(exp, cmd, capsys)


def test_dn_random(capsys):
    """Called with -r, dn mode should return a randomly
    denormalize the string.
    """
    exp = (
        '﹤－﹥\n'
        '\n'
    )
    cmd = (
        'dn '
        'nfkd '
        '<-> '
        '-r '
        '-s spam'
    )
    shell_test(exp, cmd, capsys)


# Test dt mode.
def test_dt(capsys):
    """Invoked with a character, details mode should print the details
    for the character.
    """
    with open('tests/data/details_mode_A.txt') as fh:
        exp = fh.read()
    cmd = (
        'dt '
        'A'
    )
    shell_test(exp, cmd, capsys)


# Test el mode.
def test_el(capsys):
    """When invoked, el mode returns a list of the registered
    escape schemes.
    """
    exp = '\n'.join(scheme for scheme in esc.schemes) + '\n\n'
    cmd = 'el'
    shell_test(exp, cmd, capsys)


def test_el_description(capsys):
    """Invoked with "-d", `el` returns the list of registered character
    sets with descriptions.
    """
    with open('tests/data/el_d.txt') as fh:
        exp = fh.read()
    cmd = 'el -d'
    shell_test(exp, cmd, capsys)


# Test es mode.
def test_es(capsys):
    """Invoked with a scheme and a base string, escape mode should
    escape the string using the given scheme and print the escaped
    string.
    """
    exp = '%41\n\n'
    cmd = (
        'es '
        'url '
        'A'
    )
    shell_test(exp, cmd, capsys)


# Test fl mode.
def test_fl(capsys):
    """When invoked, fl mode returns a list of the registered
    normalization forms.
    """
    exp = '\n'.join(form for form in nl.forms) + '\n\n'
    cmd = (
        'fl'
    )
    shell_test(exp, cmd, capsys)


def test_fl_description(capsys):
    """When invoked with -d, fl mode should return a list of
    registered normalization forms and a brief description of each
    one.
    """
    with open('tests/data/fl_d.txt') as fh:
        exp = fh.read()
    cmd = (
        'fl '
        '-d'
    )
    shell_test(exp, cmd, capsys)


# Test nl mode.
def test_nl(capsys):
    """When invoked with a normalization form and a base string,
    nl mode returns the normalization of the base string using the
    given form.
    """
    exp = 'A\n\n'
    cmd = (
        'nl '
        'nfkc '
        '\u24b6'
    )
    shell_test(exp, cmd, capsys)


# Test pf mode.
def test_pf(capsys):
    """When invoked, pf mode should return the list characters with the
    given property value.
    """
    exp = (
        '🏻 U+1F3FB (EMOJI MODIFIER FITZPATRICK TYPE-1-2)\n'
        '🏼 U+1F3FC (EMOJI MODIFIER FITZPATRICK TYPE-3)\n'
        '🏽 U+1F3FD (EMOJI MODIFIER FITZPATRICK TYPE-4)\n'
        '🏾 U+1F3FE (EMOJI MODIFIER FITZPATRICK TYPE-5)\n'
        '🏿 U+1F3FF (EMOJI MODIFIER FITZPATRICK TYPE-6)\n'
        '\n'
    )
    cmd = (
        'pf '
        'emod '
        'Y'
    )
    shell_test(exp, cmd, capsys)


def test_pf_insensitive(capsys):
    """When invoked, pf mode should return the list characters with the
    given property value.
    """
    exp = (
        '🏻 U+1F3FB (EMOJI MODIFIER FITZPATRICK TYPE-1-2)\n'
        '🏼 U+1F3FC (EMOJI MODIFIER FITZPATRICK TYPE-3)\n'
        '🏽 U+1F3FD (EMOJI MODIFIER FITZPATRICK TYPE-4)\n'
        '🏾 U+1F3FE (EMOJI MODIFIER FITZPATRICK TYPE-5)\n'
        '🏿 U+1F3FF (EMOJI MODIFIER FITZPATRICK TYPE-6)\n'
        '\n'
    )
    cmd = (
        'pf '
        'emod '
        'y '
        '-i'
    )
    shell_test(exp, cmd, capsys)


# Test up mode.
def test_up(capsys):
    """When invoked, up mode should return the list of Unicode properties."""
    with open('tests/data/up.txt') as fh:
        exp = fh.read()
    cmd = (
        'up'
    )
    shell_test(exp, cmd, capsys)


def test_up_description(capsys):
    """When invoked with -d, up mode should return a list of
    Unicode properties and their long names.
    """
    with open('tests/data/up_d.txt') as fh:
        exp = fh.read()
    cmd = (
        'up '
        '-d'
    )
    shell_test(exp, cmd, capsys)


# Utility functions.
def shell_test(exp, cmd, capsys):
    """Test shell invocation."""
    shell = sh.Shell()
    shell.onecmd(cmd)
    captured = capsys.readouterr()
    assert captured.out == exp
