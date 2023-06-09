"""
test_main
~~~~~~~~~

Unit tests for the mainline of the `charex` package.
"""
import sys

from charex import __main__ as m
from charex import escape as esc
from charex import normal as nl


# Test cd mode.
def test_cd(capsys):
    """Called with an hex string, charset mode should return the character
    or characters that hex string becomes in each of the known character
    sets.
    """
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'cd',
        '0x41'
    )
    cli_test(exp, cmd, capsys)


def test_cd_binary(capsys):
    """Called with a number prefixed with "0b", cd mode should interpret
    the base string as binary and return the character or characters that
    binary string becomes in each of the known character sets.
    """
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'cd',
        '0b01000001',
    )
    cli_test(exp, cmd, capsys)


def test_cd_code_point(capsys):
    """Called with a character, cd mode should interpret the base
    string as binary and return the character or characters that hex
    string becomes in each of the known character sets.
    """
    with open('tests/data/charset_mode_41.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'cd',
        'A',
    )
    cli_test(exp, cmd, capsys)


def test_cd_control_character(capsys):
    """Called with an hex string, cd mode should return the character
    or characters that hex string becomes in each of the known character
    sets. If the hex string becomes a control character, print the symbol
    for that character rather than the character itself.
    """
    with open('tests/data/charset_mode_0a.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'cd',
        '0x0a'
    )
    cli_test(exp, cmd, capsys)


def test_cd_no_character(capsys):
    """Called with an hex string, cd mode should return the character
    or characters that hex string becomes in each of the known character
    sets. If some character sets do not have characters for the given
    address, that should be indicated in the output.
    """
    with open('tests/data/charset_mode_e9.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'cd',
        '0xe9'
    )
    cli_test(exp, cmd, capsys)


# Test ce mode.
def test_ce(capsys):
    """Called with an character, ce mode should return the address
    for the character in each of the registered character sets.
    """
    with open('tests/data/charset_mode_r.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'ce',
        'A',
    )
    cli_test(exp, cmd, capsys)


# Test cl mode.
def test_cl(capsys):
    """When invoked, cl mode should return a list of registered
    character set codecs.
    """
    with open('tests/data/charsetlist.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'cl'
    )
    cli_test(exp, cmd, capsys)


def test_cl_description(capsys):
    """When invoked with -d, cl mode should return a list of
    registered character set codecs and a brief description of each
    one.
    """
    with open('tests/data/charsetlist_d.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'cl',
        '-d',
    )
    cli_test(exp, cmd, capsys)


# Test ct mode.
def test_ct(capsys):
    """Invoked with a normalization form and a base string, ct mode
    should print the number of denormalizations using the given form to
    stdout.
    """
    exp = '120,270,240\n\n'
    cmd = (
        'python -m charex',
        'ct',
        'nfkd',
        '<script>'
    )
    cli_test(exp, cmd, capsys)


def test_ct_maxdepth(capsys):
    """Invoked with "-m" and an integer, ct mode limit the number of
    denormalizations per character to the given integer and print the
    number of denormalizations using the given form to stdout.
    """
    exp = '256\n\n'
    cmd = (
        'python -m charex',
        'ct',
        'nfkd',
        '<script>',
        '-m', '2',
    )
    cli_test(exp, cmd, capsys)


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
        'python -m charex',
        'dn',
        'nfkd',
        '<->'
    )
    cli_test(exp, cmd, capsys)


def test_dn_maxdepth(capsys):
    """Invoked with -n and an integer, dn mode should return no
    more than that number of results.
    """
    exp = (
        '\ufe64\ufe63\ufe65\n'
        '\n'
    )
    cmd = (
        'python -m charex',
        'dn',
        'nfkd',
        '<->',
        '-m', '1'
    )
    cli_test(exp, cmd, capsys)


def test_dn_random(capsys):
    """Called with -r, dn mode should return a randomly
    denormalize the string.
    """
    exp = (
        '﹤－﹥\n'
        '\n'
    )
    cmd = (
        'python -m charex',
        'dn',
        'nfkd',
        '<->',
        '-r',
        '-s', 'spam'
    )
    cli_test(exp, cmd, capsys)


# Test dt mode.
def test_dt(capsys):
    """Invoked with a character, details mode should print the details
    for the character.
    """
    with open('tests/data/details_mode_A.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'dt',
        'A'
    )
    cli_test(exp, cmd, capsys)


# Test el mode.
def test_el(capsys):
    """When invoked, el mode returns a list of the registered
    escape schemes.
    """
    exp = '\n'.join(scheme for scheme in esc.schemes) + '\n\n'
    cmd = (
        'python -m charex',
        'el',
    )
    cli_test(exp, cmd, capsys)


def test_el_description(capsys):
    """When invoked with -d, cl mode should return a list of
    registered escape schemes and a brief description of each
    one.
    """
    with open('tests/data/el_d.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'el',
        '-d',
    )
    cli_test(exp, cmd, capsys)


# Test es mode.
def test_es(capsys):
    """Invoked with a scheme and a base string, escape mode should
    escape the string using the given scheme and print the escaped
    string.
    """
    exp = '%41\n\n'
    cmd = (
        'python -m charex',
        'es',
        'url',
        'A',
    )
    cli_test(exp, cmd, capsys)


# Test fl mode.
def test_fl(capsys):
    """When invoked, fl mode returns a list of the registered
    normalization forms.
    """
    exp = '\n'.join(form for form in nl.forms) + '\n\n'
    cmd = (
        'python -m charex',
        'fl',
    )
    cli_test(exp, cmd, capsys)


def test_fl_description(capsys):
    """When invoked with -d, fl mode should return a list of
    registered normalization forms and a brief description of each
    one.
    """
    with open('tests/data/fl_d.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'fl',
        '-d',
    )
    cli_test(exp, cmd, capsys)


# Test nl mode.
def test_nl(capsys):
    """When invoked with a normalization form and a base string,
    nl mode returns the normalization of the base string using the
    given form.
    """
    exp = 'A\n\n'
    cmd = (
        'python -m charex',
        'nl',
        'nfkc',
        '\u24b6',
    )
    cli_test(exp, cmd, capsys)


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
        'python -m charex',
        'pf',
        'emod',
        'Y',
    )
    cli_test(exp, cmd, capsys)


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
        'python -m charex',
        'pf',
        'emod',
        'y',
        '-i'
    )
    cli_test(exp, cmd, capsys)


def test_pf_regex(capsys):
    """When invoked, pf mode should return the list characters with the
    given property value.
    """
    exp = (
        '⌢ U+2322 (FROWN)\n'
        '☹ U+2639 (WHITE FROWNING FACE)\n'
        '\U0001da41 U+1DA41 (SIGNWRITING MOUTH FROWN)\n'
        '\U0001da42 U+1DA42 (SIGNWRITING MOUTH FROWN WRINKLED)\n'
        '\U0001da43 U+1DA43 (SIGNWRITING MOUTH FROWN OPEN)\n'
        '😦 U+1F626 (FROWNING FACE WITH OPEN MOUTH)\n'
        '🙁 U+1F641 (SLIGHTLY FROWNING FACE)\n'
        '🙍 U+1F64D (PERSON FROWNING)\n'
        '\n'
    )
    cmd = (
        'python -m charex',
        'pf',
        'na',
        '.*FROWN.*',
        '-g'
    )
    cli_test(exp, cmd, capsys)


def test_pf_insensitive_regex(capsys):
    """When invoked, pf mode should return the list characters with the
    given property value.
    """
    exp = (
        '⌢ U+2322 (FROWN)\n'
        '☹ U+2639 (WHITE FROWNING FACE)\n'
        '\U0001da41 U+1DA41 (SIGNWRITING MOUTH FROWN)\n'
        '\U0001da42 U+1DA42 (SIGNWRITING MOUTH FROWN WRINKLED)\n'
        '\U0001da43 U+1DA43 (SIGNWRITING MOUTH FROWN OPEN)\n'
        '😦 U+1F626 (FROWNING FACE WITH OPEN MOUTH)\n'
        '🙁 U+1F641 (SLIGHTLY FROWNING FACE)\n'
        '🙍 U+1F64D (PERSON FROWNING)\n'
        '\n'
    )
    cmd = (
        'python -m charex',
        'pf',
        'na',
        '.*frown.*',
        '-i',
        '-g'
    )
    cli_test(exp, cmd, capsys)


# Test up mode.
def test_up(capsys):
    """When invoked, up mode should return the list of Unicode properties."""
    with open('tests/data/up.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'up',
    )
    cli_test(exp, cmd, capsys)


def test_up_description(capsys):
    """When invoked with -d, up mode should return a list of
    Unicode properties and their long names.
    """
    with open('tests/data/up_d.txt') as fh:
        exp = fh.read()
    cmd = (
        'python -m charex',
        'up',
        '-d',
    )
    cli_test(exp, cmd, capsys)


# Utility functions.
def cli_test(exp, cmd, capsys):
    """Test command line invocation."""
    # Test set up.
    orig_cmd = sys.argv
    sys.argv = cmd

    # Run test.
    m.sh.invoke()

    # Gather actual result and compare.
    captured = capsys.readouterr()
    assert captured.out == exp

    # Test tear down.
    sys.argv = orig_cmd
