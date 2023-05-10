"""
test_escape
~~~~~~~~~~~

Unit tests for :mod:`charex.escape`.
"""
from charex import escape as esc


# Test escape.
def test_escape():
    """Given a string and the key for an escape scheme,
    :func:`charex.escape.escape` should return a string with every
    character escaped using the given string.
    """
    exp = '%73%70%61%6D'
    assert esc.escape('spam', 'url')


# Test escape_cu.
def test_escape_cu():
    """Given a character and a codec, return the C/C++ Unicode escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\u0061'
    assert esc.escape_cu('a', '') == exp


def test_escape_cu_4_byte():
    """Given a character and a codec, return the C/C++ Unicode escape
    sequence for the character. If the character is over two bytes long,
    the sequence should use a capital U and eight digits. Note: the
    codec doesn't do anything, it's just here for compatibility.
    """
    exp = r'\U00010000'
    assert esc.escape_cu('\u10000', '') == exp


# Test escape_html.
def test_escape_html():
    """Given a character and a codec, return the HTML entity for the
    address of that character.
    """
    exp = '&#97;'
    assert esc.escape_html('a', 'utf8')


# Test escape_url.
def test_escape_url():
    """Given a character and a codec, return the URL encoding for the
    address of that character.
    """
    exp = '%61'
    assert esc.escape_url('a', 'utf8')


# Tests for get_schemes.
def test_get_schemes():
    """When called, :func:`charex.escape.get_schemes` should return
    the keys of the registered escape schemes as a :class:`tuple`.
    """
    exp = tuple(scheme for scheme in esc.schemes)
    assert esc.get_schemes() == exp
