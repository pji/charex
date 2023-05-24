"""
test_charex
~~~~~~~~~~~
"""
import json

from charex import charex as c


# Test Character.
def test_character_init():
    """Given a string containing a character, a :class:`Character`
    object is initialized.
    """
    exp_value = 'a'
    act = c.Character(exp_value)
    assert act.value == exp_value


def test_character_init_with_hex():
    """Given a string containing a hexadecimal number starting with
    "0x", a :class:`Character` object is initialized with the character
    at that address.
    """
    exp_value = 'a'
    act = c.Character('0x0061')
    assert act.value == exp_value


def test_character_init_with_code_point():
    """Given a string containing a unicode code point starting with
    "U+", a :class:`Character` object is initialized with the character
    at that address.
    """
    exp_value = 'a'
    act = c.Character('U+0061')
    assert act.value == exp_value


def test_character_category():
    """When called, :attr:`Character.category` returns the Unicode
    category for the character.
    """
    char = c.Character('a')
    assert char.category == 'Lowercase Letter'


def test_character_code_point():
    """When called, :attr:`Character.code_point` returns the Unicode
    code point for the character.
    """
    char = c.Character('<')
    assert char.code_point == 'U+003C'


def test_character_decimal():
    """When called, :attr:`Character.decimal` gives the numeric value of
    the character if it has one. If the character does not have a
    numeric value, return None.
    """
    char = c.Character('2')
    assert char.decimal == 2

    char = c.Character('a')
    assert char.decimal is None


def test_character_decomposition():
    """When called, :attr:`Character.decomposition` returns the Unicode
    decomposition for the character.
    """
    char = c.Character('å')
    assert char.decomposition == '0061 030A'


def test_character_digit():
    """When called, :attr:`Character.digit` gives the numeric value of
    the character if it has one. If the character does not have a
    numeric value, return None.
    """
    char = c.Character('2')
    assert char.digit == 2

    char = c.Character('a')
    assert char.digit is None


def test_character_encode():
    """When called with a valid character encoding,
    :meth:`Character.is_normal` returns a hexadecimal string
    of the encoded form of the character.
    """
    char = c.Character('å')
    assert char.encode('utf8') == 'C3 A5'


def test_character_escape_url():
    """When called with a valid character escaping scheme,
    :meth:`Character.escape` returns a string of the escaped
    form of the character.
    """
    # Percent encoding for URLs.
    char = c.Character('å')
    assert char.escape('url', 'utf8') == '%C3%A5'


def test_character_escape_html():
    """When called with a valid character escaping scheme,
    :meth:`Character.escape` returns a string of the escaped
    form of the character.
    """
    # Percent encoding for URLs.
    char = c.Character('å')
    assert char.escape('html') == '&aring;'


def test_character_is_normal():
    """When called with a valid normalization form,
    :meth:`Character.is_normal` returns whether the value
    is normalized for that form.
    """
    char = c.Character('a')
    assert char.is_normal('NFC')

    char = c.Character('å')
    assert not char.is_normal('NFD')


def test_character_name():
    """When called, :attr:`Character.name` returns the Unicode name
    for the code point.
    """
    char = c.Character('a')
    assert char.name == 'LATIN SMALL LETTER A'


def test_character_name_null():
    """When called, :attr:`Character.name` returns the Unicode name
    for the code point.
    """
    char = c.Character('\u0000')
    assert char.name == '<NULL>'


def test_character_name_private_use():
    """When called, :attr:`Character.name` returns the Unicode name
    for the code point.
    """
    char = c.Character('\ue90a')
    assert char.name == 'PRIVATE USE CHARACTER'


def test_character_numeric():
    """When called, :attr:`Character.numeric` gives the numeric value of
    the character if it has one. If the character does not have a
    numeric value, return None.
    """
    char = c.Character('2')
    assert char.numeric == 2

    char = c.Character('a')
    assert char.numeric is None


def test_character_normalize():
    """When given a normalization form, :meth:`Character.normalize` should
    return the normalized form of the character.
    """
    char = c.Character('å')
    assert char.normalize('NFD') == b'a\xcc\x8a'.decode('utf8')


def test_character_repr():
    """When called, :meth:`Character.__repr__` returns the Unicode code
    point and name for the code point.
    """
    char = c.Character('a')
    assert repr(char) == 'U+0061 (LATIN SMALL LETTER A)'


def test_character_denormalize():
    """When given a normalization form, :meth:`Character.reverse_normalize`
    should return the normalized form of the character.
    """
    exp = ("\uf907", "\uf908", "\uface")
    char = c.Character('\u9f9c')
    assert char.denormalize('nfc') == exp


def test_character_summarize():
    """When called, :meth:`Character.summarize` returns a summary of the
    character's information as a :class:`str`.
    """
    exp = 'a U+0061 (LATIN SMALL LETTER A)'
    char = c.Character('a')
    assert char.summarize() == exp


def test_character_summarize_control():
    """When called, :meth:`Character.summarize` returns a summary of the
    character's information as a :class:`str`.
    """
    exp = '\u240a U+000A (<LINE FEED (LF)>)'
    char = c.Character('\n')
    assert char.summarize() == exp


# Test Lookup.
def test_lookup_init_set_source():
    """Given a key for a data file, an instance of Lookup should be
    created with the data file loaded.
    """
    exp_source = 'rev_nfc'
    with open(f'charex/data/{exp_source}.json') as fh:
        data = json.load(fh)
        exp_data = {k: tuple(data[k]) for k in data}
    act = c.Lookup(exp_source)
    assert act.source == exp_source
    assert act.data == exp_data


def test_lookup_query():
    """Given a string, :meth:`Lookup.query` should return the value
    for that string from the loaded data.
    """
    exp = ("\uf907", "\uf908", "\uface")
    key = '\u9f9c'
    lkp = c.Lookup('rev_nfc')
    act = lkp.query(key)
    assert act == exp

    # If key is not present in the data, return an empty tuple.
    key = 'a'
    assert lkp.query(key) == ()
