"""
util
~~~~

Utility functions for :mod:`charex`.
"""
from importlib.resources import files
from math import log
import unicodedata as ucd


# Constants.
ADDRESS_FORMAT_DOC = '''
Address Formats
---------------
The understood str-based formats for manual input of addresses are:

*   Character: A string with length equal to one.
*   Code Point: The prefix "U+" followed by a hexadecimal number.
*   Binary String: The prefix "0b" followed by a binary number.
*   Hex String: The prefix "0x" followed by a hexadecimal number.

The following formats are available for use through the API:

*   Bytes: A :class:`bytes`.
*   Integer: An :class:`int`.
'''
CHAR_FORMAT_DOC = '''
Character Formats
-----------------
The understood str-based formats available for manual input are (all
formats are big endian unless otherwise stated):

*   Character: A string with length equal to one.
*   Code Point: The prefix "U+" followed by a hexadecimal number.
*   Binary String: The prefix "0b" followed by a binary number.
*   Octal String: The prefix "0o" followed by an octal number.
*   Decimal String: The prefix "0d" followed by a decimal number.
*   Hex String: The prefix "0x" followed by a hexadecimal number.

The following formats are available for use through the API:

*   Bytes: A :class:`bytes` that decodes to a valid UTF-8 character.
*   Integer: An :class:`int` within the range 0x00 <= x <= 0x10FFFF.
'''
DATA_LOC = 'charex.data'
LEN_UNICODE = 0x110000
RESOURCES = {
    # Command help.
    'help_xt': 'help_xt.txt',

    # Package data.
    'sources': 'sources.json',

    # Denormalization lookups.
    'rev_casefold': 'rev_casefold.json',
    'rev_nfc': 'rev_nfc.json',
    'rev_nfkc': 'rev_nfkc.json',
    'rev_nfd': 'rev_nfd.json',
    'rev_nfkd': 'rev_nfkd.json',

    # Unicode data.
    'age': 'DerivedAge.txt',
    'blocks': 'Blocks.txt',
    'blk': 'Blocks.txt',
    'bmg': 'BidiMirroring.txt',
    'ce': 'CompositionExclusions.txt',
    'cf': 'CaseFolding.txt',
    'dnormprops': 'DerivedNormalizationProps.txt',
    'dproplist': 'DerivedCoreProperties.txt',
    'ea': 'EastAsianWidth.txt',
    'emoji': 'emoji-data.txt',
    'equideo': 'EquivalentUnifiedIdeograph.txt',
    'gcb': 'GraphemeBreakProperty.txt',
    'hst': 'HangulSyllableType.txt',
    'inpc': 'IndicPositionalCategory.txt',
    'insc': 'IndicSyllabicCategory.txt',
    'jg': 'DerivedJoiningGroup.txt',
    'jsn': 'Jamo.txt',
    'jt': 'DerivedJoiningType.txt',
    'lb': 'LineBreak.txt',
    'name_alias': 'NameAliases.txt',
    'props': 'PropertyAliases.txt',
    'proplist': 'PropList.txt',
    'propvals': 'PropertyValueAliases.txt',
    'sb': 'SentenceBreakProperty.txt',
    'scripts': 'Scripts.txt',
    'sc': 'Scripts.txt',
    'scf': 'CaseFolding.txt',
    'scriptext': 'ScriptExtensions.txt',
    'scx': 'ScriptExtensions.txt',
    'speccase': 'SpecialCasing.txt',
    'unicodedata': 'UnicodeData.txt',
    'vo': 'VerticalOrientation.txt',
    'wb': 'WordBreakProperty.txt',

    # HTML data.
    'entities': 'entities.json',

    # HTML examples.
    'result': 'result.html',
    'quote': 'quote.html',
}


# Exceptions.
class NotCharacterError(ValueError):
    """The value cannot be used as a character."""


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


def get_description_from_docstring(obj: object) -> str:
    """Get the first paragraph of the docstring from the given object.

    :param obj: An object with a docstring.
    :return: The first paragraph of the object's docstring as a :class:`str`.
    :rtype: str
    """
    doc = obj.__doc__
    if doc:
        paragraphs = doc.split('\n\n')
        descr = paragraphs[0]
        lines = descr.split('\n')
        lines = [line.lstrip() for line in lines]
        return ' '.join(lines)
    return ''


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
        try:
            if ucd.category(char) == 'Cc':
                num = ord(char)
                new = chr(num + 0x2400)
                return new
            return char
        except TypeError as ex:
            print(char)
            raise ex

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
    pkg = files(DATA_LOC)
    data_file = pkg / RESOURCES[key]
    fh = data_file.open(encoding=codec)
    lines = fh.readlines()
    fh.close()
    lines = [line.rstrip() for line in lines]
    return tuple(lines)


def to_bytes(value: bytes | int | str, endian: str = 'big') -> bytes:
    """Transform the given value to :class:`bytes`.

    :param value: The address to transform.
    :param endian: (Optional.) An indicator for the endianness of the
        a number string. Valid values are: big, little. It defaults to
        big.
    :return: A :class:`bytes`.
    :rtype: bytes

    Address Formats
    ---------------
    The primary purpose of this function is to standardize the ways
    a user can input a character address across all of :mod:`charex`.
    The understood formats for manual input are:

    *   Character: A string with length equal to one.
    *   Code Point: The prefix "U+" followed by a hexadecimal number.
    *   Binary String: The prefix "0b" followed by a binary number.
    *   Hex String: The prefix "0x" followed by a hexadecimal number.

    The following formats are available for use through the API:

    *   Bytes: A :class:`bytes`.
    *   Integer: An :class:`int`.
    """
    if isinstance(value, str) and value.startswith('0b'):
        value = bin2bytes(value[2:], endian)
    elif isinstance(value, str) and value.startswith('0x'):
        value = hex2bytes(value[2:], endian)
    elif isinstance(value, str) and (
        value.startswith('U+')
        or value.startswith('u+')
    ):
        n = int(value[2:], 16)
        char = chr(n)
        value = char.encode('utf8')
    elif isinstance(value, str):
        value = value.encode('utf8')
    elif isinstance(value, int):
        value = value.to_bytes((value.bit_length() + 7) // 8)
    return value


def to_char(value: bytes | int | str) -> str:
    """Transform the given value to a one character :class:`str`.

    :param value: The value to transform.
    :return: A :class:`str` of length one.
    :rtype: str

    Character Formats
    -----------------
    The primary purpose of this function is to standardize the ways
    a user can input a character across all of :mod:`charex`. The
    understood formats available for manual input are (all formats
    are big endian unless otherwise stated):

    *   Character: A string with length equal to one.
    *   Code Point: The prefix "U+" followed by a hexadecimal number.
    *   Binary String: The prefix "0b" followed by a binary number.
    *   Octal String: The prefix "0o" followed by an octal number.
    *   Decimal String: The prefix "0d" followed by a decimal number.
    *   Hex String: The prefix "0x" followed by a hexadecimal number.

    The following formats are available for use through the API:

    *   Bytes: A :class:`bytes` that decodes to a valid UTF-8 character.
    *   Integer: An :class:`int` within the range 0x00 <= x <= 0x10FFFF.

    """
    prefixes = {
        '0b': 2,
        '0d': 10,
        '0o': 8,
        '0x': 16,
        'U+': 16,
        'u+': 16,
    }

    if isinstance(value, bytes):
        value = value.decode('utf8')
    elif isinstance(value, int):
        value = chr(value)
    elif value[:2] in prefixes:
        n = int(value[2:], prefixes[value[:2]])
        value = chr(n)
    elif not isinstance(value, str) or len(value) != 1:
        msg = 'Value cannot be made a str with length one.'
        raise NotCharacterError(msg)
    return value
