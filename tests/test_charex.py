"""
test_charex
~~~~~~~~~~~
"""
import json

from charex import charex as c


# Test Character.
def test_character_init():
    """Given a string containing one or more codepoints representing
    a character, a :class:`Character` object is initialized.
    """
    exp_value = 'a'
    act = c.Character(exp_value)
    assert act.value == exp_value


def test_character_name():
    """When called, :attr:`Character.name` returns the Unicode name
    for the code point.
    """
    char = c.Character('a')
    assert char.name == 'LATIN SMALL LETTER A'


def test_character_is_normal():
    """When called with a valid normalization form,
    :meth:`Character.is_normal` return whether the value
    is normalized for that form.
    """
    char = c.Character('a')
    assert char.is_normal('NFC')

    char = c.Character('å')
    assert not char.is_normal('NFD')


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


# Test Transformer.
def test_transformer_init():
    """An instance of Transformer can be initialized with default
    values.
    """
    act = c.Transformer()
    assert act.charset == 'utf_8'
    assert act.endian == 'big'


def test_transformer_init_set_charset():
    """When passed a string naming a character set, Transformer is
    initialized with that value.
    """
    act = c.Transformer('cp1252')
    assert act.charset == 'cp1252'


def test_transformer_from_bin_ascii():
    """Given a binary number as a string, :meth:`Transformer.from_bin`
    should return the code point for that binary number.
    """
    exp = 'a'
    tf = c.Transformer()
    b = '01100001'
    act = tf.from_bin(b)
    assert exp == act


def test_transformer_from_bin_change_charset():
    """When :attr:`Transformer.charset` is changed,
    :meth:`Transformer.from_bin` should use the new
    character set when determining the code point.
    """
    tf = c.Transformer('cp1252')
    b = '11101001'
    assert tf.from_bin(b) == 'é'
    tf.charset = 'iso8859_7'
    assert tf.from_bin(b) == 'ι'


def test_transformer_from_bin_less_than_byte():
    """When given a binary string with fewer than four digits,
    :meth:`Transformer.from_bin` still returns the correct
    character.
    """
    tf = c.Transformer()
    b = '10'
    assert tf.from_bin(b) == '\x02'


def test_transformer_from_bin_change_endian():
    """When :attr:`Transformer.endian` is changed,
    :meth:`Transformer.from_bin` should use the new
    endianness when determining the code point.
    """
    tf = c.Transformer()
    b = '01100010'
    assert tf.from_bin(b) == 'b'
    tf.endian = 'little'
    assert tf.from_bin(b) == '\x46'


def test_transformer_from_bin_invalid():
    """When given a binary string that isn't a valid value in the
    current character set, :meth:`Transformer.from_bin` should return
    the Unicode invalid character symbol.
    """
    tf = c.Transformer()
    b = '11100010'
    assert tf.from_bin(b) == '\uFFFD'


def test_transformer_from_hex_ascii():
    """Given a hexadecimal number as a string, :meth:`Transformer.from_hex`
    should return the code point for that hexadecimal number.
    """
    tf = c.Transformer()
    h = '46'
    assert tf.from_hex(h) == 'F'


def test_transformer_from_hex_little_endian():
    """Given a hexadecimal number as a string, :meth:`Transformer.from_hex`
    should return the code point for that hexadecimal number.
    """
    tf = c.Transformer(endian='little')
    h = 'a3c3'
    assert tf.from_hex(h) == 'ã'
