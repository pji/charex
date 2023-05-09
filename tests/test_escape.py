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
