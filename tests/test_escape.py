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


# Test escape_c.
def test_escape_c():
    """Given a character and a codec, return the C/C++ escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\n'
    assert esc.escape_c('\u000a', '') == exp


# Test escape_co.
def test_escape_co():
    """Given a character and a codec, return the C/C++ octal escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\141'
    assert esc.escape_co('a', '') == exp


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
    assert esc.escape_cu('\U00010000', '') == exp


# Test escape_culong.
def test_escape_culong():
    """Given a character and a codec, return the C/C++ Unicode escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\U00000061'
    assert esc.escape_culong('a', '') == exp


# Test escape_html.
def test_html():
    """Given a character and a codec, return the HTML named entity for
    the given character. Note: codec doesn't do anything, it's just
    included for compatibility."""
    exp = "&qout;"
    assert esc.escape_html('"', '')


def test_html_no_name():
    """Given a character and a codec, return the HTML named entity for
    the given character. Note: codec doesn't do anything, it's just
    included for compatibility. If there is no specific named entity,
    return the decimal encoded entity."""
    exp = "&#97;"
    assert esc.escape_html('a', '')


# Test escape_htmldec.
def test_escape_htmldec():
    """Given a character and a codec, return the HTML entity for the
    address of that character.
    """
    exp = '&#97;'
    assert esc.escape_htmldec('a', 'utf8')


# Test escape_htmlhex.
def test_escape_htmlhex():
    """Given a character and a codec, return the HTML hexadecimal
    entity for the given character. Note: codec doesn't do anything,
    it's just included for compatibility.
    """
    exp = '&#x61;'
    assert esc.escape_htmlhex('a', '')


# Test escape_java.
def test_escape_java():
    """Given a character and a codec, return the Java escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\n'
    assert esc.escape_java('\u000A', '') == exp


# Test escape_javao.
def test_escape_javao():
    """Given a character and a codec, return the Java octal escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\141'
    assert esc.escape_javao('a', '') == exp


# Test escape_javau.
def test_escape_javau():
    """Given a character and a codec, return the Java Unicode escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\u0041'
    assert esc.escape_javau('A', '') == exp


def test_escape_javau_4_byte_character():
    """Given a character and a codec, return the Java Unicode escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility. Characters over U+FFFF have to
    be returned as two characters because Java encodes strings with
    UTF-16.
    """
    exp = r'\ud800\udc00'
    assert esc.escape_javau('\U00010000', '') == exp


# Test escape_js.
def test_escape_js():
    """Given a character and a codec, return the JavaScript escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\n'
    assert esc.escape_js('\u000A', '') == exp


# Test escape_jso.
def test_escape_jso():
    """Given a character and a codec, return the JavaScript octal escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\141'
    assert esc.escape_jso('a', '') == exp


# Test escape_jsu.
def test_escape_jsu():
    """Given a character and a codec, return the JavaScript Unicode
    escape sequence for the character. Note: the codec doesn't do
    anything, it's just here for compatibility.
    """
    exp = r'\u0041'
    assert esc.escape_jsu('A', '') == exp


def test_escape_jsu_4_byte_character():
    """Given a character and a codec, return the JavaScript Unicode
    escape sequence for the character. Note: the codec doesn't do
    anything, it's just here for compatibility.
    """
    exp = r'\u{10000}'
    assert esc.escape_jsu('\U00010000', '') == exp


# Test escape_jscp.
def test_escape_jscp():
    """Given a character and a codec, return the JavaScript code point
    escape sequence for the character. Note: the codec doesn't do
    anything, it's just here for compatibility.
    """
    exp = r'\u{41}'
    assert esc.escape_jscp('A', '') == exp


# Test escape_json.
def test_escape_json():
    """Given a character and a codec, return the JSON escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\n'
    assert esc.escape_json('\u000A', '') == exp


# Test escape_jsonu.
def test_escape_jsonu():
    """Given a character and a codec, return the JSON Unicode escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\u0041'
    assert esc.escape_jsonu('A', '') == exp


def test_escape_jsonu_special():
    """Given a character and a codec, return the JSON Unicode escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\u000a'
    assert esc.escape_jsonu('\n', '') == exp


def test_escape_jsonu_4_byte_character():
    """Given a character and a codec, return the Java Unicode escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility. Characters over U+FFFF have to
    be returned as two characters because Java encodes strings with
    UTF-16.
    """
    exp = r'\ud800\udc00'
    assert esc.escape_jsonu('\U00010000', '') == exp


# Test escape_smol.
def test_escape_smol():
    """Give a character and a codec, return the superscript
    Unicode character version of the given character. Note: the
    codec doesn't do anything. It's just here for compatibility.
    """
    exp = 'ᵃ'
    assert esc.escape_smol('a', '') == exp


# Test escape_sql.
def test_escape_sql():
    """Given a character and a codec, return the SQL escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'\n'
    assert esc.escape_sql('\u000A', '') == exp


# Test escape_sqldq.
def test_escape_sqldq():
    """Given a character and a codec, return the SQL escape
    sequence for the character. Note: the codec doesn't do anything,
    it's just here for compatibility.
    """
    exp = r'""'
    assert esc.escape_sqldq('\u0022', '') == exp


# Test escape_url.
def test_escape_url():
    """Given a character and a codec, return the URL encoding for the
    address of that character.
    """
    exp = '%61'
    assert esc.escape_url('a', 'utf8')


# Tests for get_description.
def test_get_description():
    """Given the key for an escape scheme,
    :func:`charex.escape.get_description` should
    return the first paragraph of the docstring of
    that scheme.
    """
    # Expected value.
    exp = 'Eggs bacon.'

    # Test set up.
    @esc.reg_escape('__test_get_description')
    def escape_spam(char, codec):
        """Eggs bacon.

        Ham and toast.
        """
        return char

    # Run test and determine result.
    assert esc.get_description('__test_get_description') == exp

    # Test clean up.
    del esc.schemes['__test_get_description']


# Tests for get_schemes.
def test_get_schemes():
    """When called, :func:`charex.escape.get_schemes` should return
    the keys of the registered escape schemes as a :class:`tuple`.
    """
    exp = tuple(scheme for scheme in esc.schemes)
    assert esc.get_schemes() == exp
