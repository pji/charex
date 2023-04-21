"""
test_charex
~~~~~~~~~~~
"""
from charex import charex as c


# Transformer tests.
def test_tranformer_init():
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


def test_tranformer_from_bin_ascii():
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
