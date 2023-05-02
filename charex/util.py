"""
util
~~~~

Utility functions for :mod:`charex`.
"""
from math import log


def bin2bytes(value: str, endian: str = 'big') -> bytes:
    """Convert a binary string into :class:`bytes`.

    :param value: A :class:`str` containing the representation of
        a binary number.
    :param endian: (Optional.) An indicator for the endianness of the
        binary number. Valid values are: big, little. It defaults to
        big.
    :return: The binary number as :class:`bytes`.
    :rtype: bytes
    """
    value = pad_byte(value, endian, base=2)

    parts = []
    while value:
        parts.append(value[:8])
        value = value[8:]
    nums = [int(s, 2) for s in parts]
    octets = [n.to_bytes((n.bit_length() + 7) // 8) for n in nums]
    return b''.join(octets)


def hex2bytes(value: str, endian: str = 'big') -> bytes:
    """Convert a hex string into :class:`bytes`.

    :param value: A :class:`str` containing the representation of
        a hexadecimal number.
    :param endian: (Optional.) An indicator for the endianness of the
        hexadecimal number. Valid values are: big, little. It defaults
        to big.
    :return: The hexadecimal number as :class:`bytes`.
    :rtype: bytes
    """
    # Since a byte is two characters, pad strings that have an
    # odd length.
    value = pad_byte(value, endian)

    # Convert the string to bytes.
    parts = []
    while value:
        parts.append(value[:2])
        value = value[2:]
    nums = [int(s, 16) for s in parts]
    octets = [n.to_bytes((n.bit_length() + 7) // 8) for n in nums]
    return b''.join(octets)


def pad_byte(value: str, endian: str = 'big', base: int = 16) -> str:
    """Add a zeros to pad strings shorter than the needed bytelen.

    :param value: A :class:`str` containing the representation of
        a number.
    :param endian: (Optional.) An indicator for the endianness of the
        number. Valid values are: big, little. It defaults to big.
    :param base: (Optional.) The base of the number. It defaults to
        hexadecimal (16).
    :return: The number padded with leading zeros to be a full byte
        as a :class:`str`.
    :rtype: str
    """
    # Determine the number of digits needed in a byte.
    bytelen = int(log(256, base))

    # Pad the number.
    if gap := len(value) % bytelen:
        zeros = '0' * (bytelen - gap)
        if endian == 'big':
            return zeros + value
        return value[:-1 * gap] + zeros + value[-1 * gap:]
    return value
