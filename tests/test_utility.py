"""
test_util
~~~~~~~~~

Unit test for :mod:`charex.util`.
"""
import pytest

from charex import util


# Test cases.
# Tests for to_bytes.
def test_to_bytes():
    """Given a :class:`str` containing a representation of a binary
    number, return that number as :class:`bytes`.
    """
    exp = b'\xe9'
    value = '0b11101001'
    act = util.to_bytes(value)
    assert act == exp


def test_to_bytes_bin_len_not_multiple_of_eight():
    """Given a :class:`str` containing a representation of a binary
    number, return that number as :class:`bytes`. If the length of the
    :class:`str` is not a multiple of eight, prepend enough zeros to
    make it a multiple of eight.
    """
    exp = b'\x29\xe9'
    value = '0b10100111101001'
    act = util.to_bytes(value)
    assert act == exp


def test_to_bytes_len_not_multiple_of_eight_little_endian():
    """Given a :class:`str` containing a representation of a binary
    number, return that number as :class:`bytes`. If the length of
    the :class:`str` is not a multiple of eight and the string is
    little endian, prepend enough zeros to the last byte to make it
    a multiple of eight.
    """
    exp = b'\xa7\x29'
    value = '0b10100111101001'
    act = util.to_bytes(value, endian='little')
    assert act == exp


def test_to_bytes_bytes():
    """Given a :class:`bytes`, :func:`charex.util.bytes` should return
    the given :class:`bytes`.
    """
    exp = b'\x00\x61'
    assert util.to_bytes(exp) == exp


def test_to_bytes_hex():
    """Given a :class:`str` containing a representation of a hexadecimal
    number, return that number as :class:`bytes`.
    """
    exp = b'\xbe\xef\xca\x5e'
    value = '0xbeefca5e'
    act = util.to_bytes(value)
    assert act == exp


def test_hex2bytes_hex_odd_length():
    """Given a :class:`str` containing a representation of a hexadecimal
    number, return that number as :class:`bytes`. If the :class:`str` has
    an odd number of characters, prepend a zero to the string before
    converting it to bytes.
    """
    exp = b'\x0e\xef\xca\x5e'
    value = '0xeefca5e'
    act = util.to_bytes(value)
    assert act == exp


def test_hex2bytes_hex_odd_length_little_endian():
    """Given a :class:`str` containing a representation of a hexadecimal
    number, return that number as :class:`bytes`. If the :class:`str` has
    an odd number of characters and endian is "little" add a zero before
    the last character of the string.
    """
    exp = b'\xbe\xef\xca\x0e'
    value = '0xbeefcae'
    act = util.to_bytes(value, endian='little')
    assert act == exp


def test_to_bytes_int():
    """Given a :class:`int`, :func:`charex.util.bytes` should that
    number as :class:`bytes`.
    """
    exp = b'\x61'
    value = 0x61
    assert util.to_bytes(value) == exp


def test_to_bytes_str():
    """Given a :class:`str`, return that :class:`str` as an UTF-8
    encoded :class:`bytes`.
    """
    exp = b'\xc3\xa9'
    value = 'é'
    act = util.to_bytes(value)
    assert act == exp


def test_to_bytes_unicode():
    """Given a :class:`str` containing a Unicode code point, return that
    code point as an UTF-8 encoded :class:`bytes`.
    """
    exp = b'\x61'
    value = 'U+0061'
    act = util.to_bytes(value)
    assert act == exp


def test_to_bytes_unicode_lowercase_u():
    """Given a :class:`str` containing a Unicode code point, return that
    code point as an UTF-8 encoded :class:`bytes`. The code point can
    start with a lowercase u.
    """
    exp = b'\x61'
    value = 'u+0061'
    act = util.to_bytes(value)
    assert act == exp


# Tests for to_char.
def to_char():
    """Given a :class:`str` with length one, return that :class:`str`."""
    exp = 'a'
    assert util.to_char(exp) == exp


def test_sto_char_binary():
    """Given an binary string, return a one character :class:`str` using
    the given binary string as the unicode code point.
    """
    exp = 'a'
    value = '0b01100001'
    assert util.to_char(value) == exp


def test_to_char_bytes():
    """Given :class:`bytes`, return a one character :class:`str` using
    the given bytes as a UTF-8 encoded value.
    """
    exp = '\U0001f600'
    value = b'\xf0\x9f\x98\x80'
    assert util.to_char(value) == exp


def test_sto_char_decimal():
    """Given an decimal string, return a one character :class:`str` using
    the given decimal string as the unicode code point.
    """
    exp = 'a'
    value = '0d97'
    assert util.to_char(value) == exp


def test_sto_char_hex():
    """Given a hex string, return a one character :class:`str` using
    the given hex string as the unicode code point.
    """
    exp = 'a'
    value = '0x61'
    assert util.to_char(value) == exp


def test_to_char_int():
    """Given an :class:`int`, return a one character :class:`str` using
    the given :class:`int` as the Unicode code point.
    """
    exp = 'a'
    value = 0x61
    assert util.to_char(value) == exp


def test_sto_char_octal():
    """Given an octal string, return a one character :class:`str` using
    the given octal string as the unicode code point.
    """
    exp = 'a'
    value = '0o141'
    assert util.to_char(value) == exp


def test_to_char_str_too_long():
    """Given a :class:`str` with more than one character that isn't a
    hex string or a code point, :func:`charex.util.to_char` should
    raise :class:`charex.util.NotCharacterError`.
    """
    exp = util.NotCharacterError
    value = 'spam'
    with pytest.raises(exp):
        util.to_char(value)


def test_to_char_unicode():
    """Given a Unicode code point string, return a one character
    :class:`str` of the unicode code point.
    """
    exp = 'a'
    value = 'U+0061'
    assert util.to_char(value) == exp


def test_to_char_unicode_lowercase_u():
    """Given a Unicode code point string, return a one character
    :class:`str` of the unicode code point. The code point can start
    with a lowercase letter u.
    """
    exp = 'a'
    value = 'u+0061'
    assert util.to_char(value) == exp
