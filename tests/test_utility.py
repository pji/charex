"""
test_util
~~~~~~~~~

Unit test for :mod:`charex.util`.
"""
from charex import util


# Test cases.
# Tests for bin2bytes.
def test_bin2bytes():
    """Given a :class:`str` containing a representation of a binary
    number, return that number as :class:`bytes`.
    """
    exp = b'\xe9'
    value = '11101001'
    act = util.bin2bytes(value)
    assert act == exp


def test_bin2bytes_len_not_multiple_of_eight():
    """Given a :class:`str` containing a representation of a binary
    number, return that number as :class:`bytes`. If the length of the
    :class:`str` is not a multiple of eight, prepend enough zeros to
    make it a multiple of eight.
    """
    exp = b'\x29\xe9'
    value = '10100111101001'
    act = util.bin2bytes(value)
    assert act == exp


def test_bin2bytes_len_not_multiple_of_eight_little_endian():
    """Given a :class:`str` containing a representation of a binary
    number, return that number as :class:`bytes`. If the length of
    the :class:`str` is not a multiple of eight and the string is
    little endian, prepend enough zeros to the last byte to make it
    a multiple of eight.
    """
    exp = b'\xa7\x29'
    value = '10100111101001'
    act = util.bin2bytes(value, endian='little')
    assert act == exp


# Tests for hex2bytes.
def test_hex2bytes():
    """Given a :class:`str` containing a representation of a hexadecimal
    number, return that number as :class:`bytes`.
    """
    exp = b'\xbe\xef\xca\x5e'
    value = 'beefca5e'
    act = util.hex2bytes(value)
    assert act == exp


def test_hex2bytes_odd_length():
    """Given a :class:`str` containing a representation of a hexadecimal
    number, return that number as :class:`bytes`. If the :class:`str` has
    an odd number of characters, prepend a zero to the string before
    converting it to bytes.
    """
    exp = b'\x0e\xef\xca\x5e'
    value = 'eefca5e'
    act = util.hex2bytes(value)
    assert act == exp


def test_hex2bytes_odd_length_little_endian():
    """Given a :class:`str` containing a representation of a hexadecimal
    number, return that number as :class:`bytes`. If the :class:`str` has
    an odd number of characters and endian is "little" add a zero before
    the last character of the string.
    """
    exp = b'\xbe\xef\xca\x0e'
    value = 'beefcae'
    act = util.hex2bytes(value, endian='little')
    assert act == exp
