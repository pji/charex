"""
util
~~~~

Utility functions for :mod:`charex`.
"""


def bin2bytes(value: str, endian: str = 'big') -> bytes:
    """Convert a binary string into :class:`bytes`."""
    value = pad_byte(value, endian, bytelen=8)

    parts = []
    while value:
        parts.append(value[:8])
        value = value[8:]
    nums = [int(s, 2) for s in parts]
    octets = [n.to_bytes((n.bit_length() + 7) // 8) for n in nums]
    return b''.join(octets)


def hex2bytes(value: str, endian: str = 'big') -> bytes:
    """Convert a hex string into :class:`bytes`."""
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


def pad_byte(value: str, endian: str = 'big', bytelen: int = 2) -> str:
    """Add a zeros to pad strings shorter than the needed bytelen."""
    if gap := len(value) % bytelen:
        zeros = '0' * (bytelen - gap)
        if endian == 'big':
            return zeros + value
        return value[:-1 * gap] + zeros + value[-1 * gap:]
    return value
