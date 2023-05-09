"""
util
~~~~

Utility functions for :mod:`charex`.
"""
from importlib.resources import files
from math import log
import unicodedata as ucd


# Constants.
RESOURCES = {
    # Command help.
    'help_cd': 'help_cd.txt',
    'help_ce': 'help_ce.txt',
    'help_cl': 'help_cl.txt',
    'help_count': 'help_count.txt',
    'help_dn': 'help_dn.txt',
    'help_dt': 'help_dt.txt',
    'help_es': 'help_es.txt',
    'help_rd': 'help_rd.txt',
    'help_xt': 'help_xt.txt',

    # Denormalization lookups.
    'rev_nfc': 'rev_nfc.json',
    'rev_nfkc': 'rev_nfkc.json',
    'rev_nfd': 'rev_nfd.json',
    'rev_nfkd': 'rev_nfkd.json',

    # Unicode data.
    'propvals': 'PropertyValueAliases.txt',
    'unicodedata': 'UnicodeData.txt',

    # HTML examples.
    'result': 'result.html',
    'quote': 'quote.html',
}


# Functions
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


def neutralize_control_characters(value: str) -> str:
    """Transform control characters in a string into the Unicode
    symbol for those characters.

    :param value: The :class:`str` to neutralize.
    :return: The neutralized :class:`str`.
    :rtype: str
    """
    def neutralize(char: str) -> str:
        if ucd.category(char) == 'Cc':
            num = ord(char)
            new = chr(num + 0x2400)
            return new
        return char

    return ''.join(neutralize(char) for char in value)


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


def read_resource(key: str, codec: str = 'utf_8') -> tuple[str, ...]:
    """Read the data from a resource file within the package.

    :param key: The key for the file in the RESOURCES constant.
    :return: The contents of the file as a :class:`tuple`.
    :rtype: tuple
    """
    pkg = files('charex.data')
    data_file = pkg / RESOURCES[key]
    fh = data_file.open(encoding=codec)
    lines = fh.readlines()
    fh.close()
    return tuple(lines)
