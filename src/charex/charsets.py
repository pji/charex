"""
charsets
~~~~~~~~

Data and functions for working with character sets.
"""
from collections.abc import Iterator
from dataclasses import dataclass
from sys import byteorder

from charex import util


# Data classes.
@dataclass
class CodecDetails:
    """Information for working with the specific codec.

    :param size: (Optional.) The number of bytes used to address
        characters with the given character set.
    :param endian: (Optional.) The byte order used by the codec.
    """
    size: int = 1
    endian: str = byteorder
    description: str = ''


# Encoding schemes.
codecs = {
    'ascii': CodecDetails(
        description=(
            'RFC20 The ASCII format for Network Interchange.'
        )
    ),
    'big5': CodecDetails(
        description=(
            'The Big5 encoding method for traditional Chinese characters '
            'developed by the Institute for Information Industry of Taiwan '
            'in 1984.'
        )
    ),
    'big5hkscs': CodecDetails(
        description=(
            'Hong Kong Supplementary Character Set to the Big5 traditional '
            'Chinese character set.'
        )
    ),
    'cp037': CodecDetails(
        description=(
            'EBCDIC code page 37, USA/Canada Country Extended Code Page.'
        )
    ),
    'cp273': CodecDetails(
        description=(
            'EBCDIC code page 273, Germany/Austria.'
        )
    ),
    'cp424': CodecDetails(
        description=(
            'EBCDIC code page 424, Israel with supprt for Hebrew.'
        )
    ),
    'cp437': CodecDetails(
        description=(
            'Code page 424, default character set for the IBM PC.'
        )
    ),
    'cp500': CodecDetails(
        description=(
            'EBCDIC code page 500, full support of the Latin-1 character set.'
        )
    ),
    'cp720': CodecDetails(
        description=(
            'Code page 720, Arabic support for DOS.'
        )
    ),
    'cp737': CodecDetails(
        description=(
            'Code page 720, Greek support for DOS.'
        )
    ),
    'cp775': CodecDetails(
        description=(
            'Code page 775, Baltic language support for DOS.'
        )
    ),
    'cp850': CodecDetails(
        description=(
            'Code page 850, Western European language support for DOS.'
        )
    ),
    'cp852': CodecDetails(
        description=(
            'Code page 852, Central European language support for DOS.'
        )
    ),
    'cp855': CodecDetails(
        description=(
            'Code page 855, Cyrillic support for DOS.'
        )
    ),
    'cp856': CodecDetails(
        description=(
            'Code page 856, Hebrew language support for DOS.'
        )
    ),
    'cp857': CodecDetails(
        description=(
            'Code page 857, Turkish language support for DOS.'
        )
    ),
    'cp858': CodecDetails(
        description=(
            'Code page 858, Western European language support for DOS, '
            'modifying code page 850 by adding the Euro symbol.'
        )
    ),
    'cp860': CodecDetails(
        description=(
            'Code page 860, Portugese language support for DOS.'
        )
    ),
    'cp861': CodecDetails(
        description=(
            'Code page 861, Icelandic language support for DOS.'
        )
    ),
    'cp862': CodecDetails(
        description=(
            'Code page 862, Hebrew language support for DOS.'
        )
    ),
    'cp863': CodecDetails(
        description=(
            'Code page 863, Canadian French language support for DOS.'
        )
    ),
    'cp864': CodecDetails(
        description=(
            'Code page 864, Hebrew language support for DOS.'
        )
    ),
    'cp865': CodecDetails(
        description=(
            'Code page 865, Arabic language support for DOS.'
        )
    ),
    'cp866': CodecDetails(
        description=(
            'Code page 866, Nordic language support for DOS.'
        )
    ),
    'cp869': CodecDetails(
        description=(
            'Code page 869, Greek language support for DOS.'
        )
    ),
    'cp874': CodecDetails(
        description=(
            'Code page 874, Thai language support for DOS.'
        )
    ),
    'cp875': CodecDetails(
        description=(
            'EBCDIC code page 875, Greek.'
        )
    ),
    'cp932': CodecDetails(
        description=(
            'Code page 932, Japanese language support for Windows.'
        )
    ),
    'cp949': CodecDetails(
        description=(
            'Code page 949, Korean language support by IBM.'
        )
    ),
    'cp950': CodecDetails(
        description=(
            'Code page 932, Traditional Chinese language support for Windows.'
        )
    ),
    'cp1006': CodecDetails(
        description=(
            'Code page 1006, Urdu language support for AIX.'
        )
    ),
    'cp1026': CodecDetails(
        description=(
            'EBCDIC code page 1026, Turkish.'
        )
    ),
    'cp1125': CodecDetails(
        description=(
            'IBM code page 1125, Ukraine.'
        )
    ),
    'cp1140': CodecDetails(
        description=(
            'EBCDIC code page 1140, USA/Canada with Euro character.'
        )
    ),
    'cp1250': CodecDetails(
        description=(
            'Code page 1250, Central European language support for Windows.'
        )
    ),
    'cp1251': CodecDetails(
        description=(
            'Code page 1251, Cyrillic support for Windows.'
        )
    ),
    'cp1252': CodecDetails(
        description=(
            'Code page 1252, Latin-1 character set for Windows.'
        )
    ),
    'cp1253': CodecDetails(
        description=(
            'Code page 1253, Greek support for Windows.'
        )
    ),
    'cp1254': CodecDetails(
        description=(
            'Code page 1254, Turkish support for Windows.'
        )
    ),
    'cp1255': CodecDetails(
        description=(
            'Code page 1255, Hebrew support for Windows.'
        )
    ),
    'cp1256': CodecDetails(
        description=(
            'Code page 1256, Arabic support for Windows.'
        )
    ),
    'cp1257': CodecDetails(
        description=(
            'Code page 1257, Baltic language support for Windows.'
        )
    ),
    'cp1258': CodecDetails(
        description=(
            'Code page 1258, Vietamese support for Windows.'
        )
    ),
    'euc_jp': CodecDetails(
        description=(
            'Extended Unix Code Japanese.'
        )
    ),
    'euc_jis_2004': CodecDetails(
        description=(
            'Extended Unix Code Japanese Industrial Standard 2004.'
        )
    ),
    'euc_jisx0213': CodecDetails(
        description=(
            'Extended Unix Code Japanese Industrial Standard X 213.'
        )
    ),
    'euc_kr': CodecDetails(
        description=(
            'Extended Unix Code Korean.'
        )
    ),
    'gb2312': CodecDetails(
        description=(
            'Extended Unix Code Simplified Chinese.'
        )
    ),
    'gbk': CodecDetails(
        description=(
            'Extended Unix Code Simplified Chinese extended to include '
            'all unified CJK characters.'
        )
    ),
    'gb18030': CodecDetails(
        description=(
            'Chinese National Standard GB 18030-2005: Information '
            'Technology—Chinese coded character set.'
        )
    ),
    'hz': CodecDetails(
        description=(
            'Extended Unix Code Simplified Chinese for email.'
        )
    ),
    'iso2022_jp': CodecDetails(
        description=(
            'ISO 2022 standard for Japanese.'
        )
    ),
    'iso2022_jp_1': CodecDetails(
        description=(
            'ISO 2022 standard for Japanese, extension 1.'
        )
    ),
    'iso2022_jp_2': CodecDetails(
        description=(
            'ISO 2022 standard for Japanese, extension 2.'
        )
    ),
    'iso2022_jp_2004': CodecDetails(
        description=(
            'ISO 2022 standard for Japanese, extension 2004.'
        )
    ),
    'iso2022_jp_3': CodecDetails(
        description=(
            'ISO 2022 standard for Japanese, extension 3.'
        )
    ),
    'iso2022_jp_ext': CodecDetails(
        description=(
            'ISO 2022 standard for Japanese, extension.'
        )
    ),
    'iso2022_kr': CodecDetails(
        description=(
            'RFC1557 Korean Character Encoding for Internet Messages.'
        )
    ),
    'latin_1': CodecDetails(
        description=(
            'ISO-8859-1, Latin alphabet number 1 for western Europe.'
        )
    ),
    'iso8859_2': CodecDetails(
        description=(
            'ISO-8859-2, Latin alphabet number 2 for central Europe.'
        )
    ),
    'iso8859_3': CodecDetails(
        description=(
            'ISO-8859-3, Latin alphabet number 3 for southern Europe.'
        )
    ),
    'iso8859_4': CodecDetails(
        description=(
            'ISO-8859-4, Latin alphabet number 4 for northern Europe.'
        )
    ),
    'iso8859_5': CodecDetails(
        description=(
            'ISO-8859-5, Latin/Cyrillic alphabet.'
        )
    ),
    'iso8859_6': CodecDetails(
        description=(
            'ISO-8859-6, Latin/Arabic alphabet.'
        )
    ),
    'iso8859_7': CodecDetails(
        description=(
            'ISO-8859-7, Latin/Greek alphabet.'
        )
    ),
    'iso8859_8': CodecDetails(
        description=(
            'ISO-8859-8, Latin/Herbrew alphabet.'
        )
    ),
    'iso8859_9': CodecDetails(
        description=(
            'ISO-8859-9, Latin alphabet number 5 for Turkish.'
        )
    ),
    'iso8859_10': CodecDetails(
        description=(
            'ISO-8859-10, Latin alphabet number 6 for Nordic languages.'
        )
    ),
    'iso8859_11': CodecDetails(
        description=(
            'ISO-8859-11, Latin/Thai alphabet.'
        )
    ),
    'iso8859_13': CodecDetails(
        description=(
            'ISO-8859-13, Latin alphabet number 7 for Baltic Rim languages.'
        )
    ),
    'iso8859_14': CodecDetails(
        description=(
            'ISO-8859-14, Latin alphabet number 8 for Celtic languages.'
        )
    ),
    'iso8859_15': CodecDetails(
        description=(
            'ISO-8859-15, Latin alphabet number 9 for Western European '
            'languages, including the Euro symbol.'
        )
    ),
    'iso8859_16': CodecDetails(
        description=(
            'ISO-8859-16, Latin alphabet number 10 for south-eastern Europe.'
        )
    ),
    'johab': CodecDetails(
        description=(
            'KS X 1001 alternative character set for South Korean Hangul '
            'and Hanja.'
        )
    ),
    'koi8_r': CodecDetails(
        description=(
            'Kod Obmena Informatsiey, 8 bit, for Russian and Bulgarian.'
        )
    ),
    'koi8_t': CodecDetails(
        description=(
            'Kod Obmena Informatsiey, 8 bit, for Tajik Cyrillic.'
        )
    ),
    'koi8_u': CodecDetails(
        description=(
            'RFC2319 Ukrainian Character Set KOI8-U.'
        )
    ),
    'kz1048': CodecDetails(
        description=(
            'Windows-1251 variant for Kazakh.'
        )
    ),
    'mac_cyrillic': CodecDetails(
        description=(
            'Mac OS Cyrillic.'
        )
    ),
    'mac_greek': CodecDetails(
        description=(
            'Mac OS Greek.'
        )
    ),
    'mac_iceland': CodecDetails(
        description=(
            'Mac OS Icelandic.'
        )
    ),
    'mac_latin2': CodecDetails(
        description=(
            'Mac OS Central European, Microsoft code page 10029.'
        )
    ),
    'mac_roman': CodecDetails(
        description=(
            'Mac OS Western Europe.'
        )
    ),
    'mac_turkish': CodecDetails(
        description=(
            'Mac OS Turkish.'
        )
    ),
    'ptcp154': CodecDetails(
        description=(
            'Cyrillic-Asian.'
        )
    ),
    'shift_jis': CodecDetails(
        2,
        description=(
            'Japanese Industrial Standard with shifted first bytes.'
        )
    ),
    'shift_jis_2004': CodecDetails(
        2,
        description=(
            'Superset of Japanese Industrial Standard with shifted '
            'first bytes.'
        )
    ),
    'shift_jisx0213': CodecDetails(
        2,
        description=(
            'Superset of Japanese Industrial Standard with shifted '
            'first bytes.'
        )
    ),
    'utf_32': CodecDetails(
        4,
        description=(
            '32-bit Unicode Transformation format.'
        )
    ),
    'utf_32_be': CodecDetails(
        4,
        'big',
        description=(
            '32-bit Unicode Transformation format, big endian.'
        )
    ),
    'utf_32_le': CodecDetails(
        4,
        'little',
        description=(
            '32-bit Unicode Transformation format, little endian.'
        )
    ),
    'utf_16': CodecDetails(
        2,
        description=(
            '16-bit Unicode Transformation format.'
        )
    ),
    'utf_16_be': CodecDetails(
        2,
        'big',
        description=(
            '16-bit Unicode Transformation format, big endian.'
        )
    ),
    'utf_16_le': CodecDetails(
        2,
        'little',
        description=(
            '16-bit Unicode Transformation format, little endian.'
        )
    ),
    'utf_7': CodecDetails(
        description=(
            '7-bit Unicode Transformation format.'
        )
    ),
    'utf_8': CodecDetails(
        description=(
            '8-bit Unicode Transformation format.'
        )
    ),
    'utf_8_sig': CodecDetails(
        description=(
            '8-bit Unicode Transformation format, treating the BOM '
            'as metadata.'
        )
    ),
}


# Functions.
def get_codecs() -> tuple[str, ...]:
    """Return the keys of the registered codecs.

    :return: The keys of the codecs as a :class:`tuple`.
    :rtype: tuple

    Usage
    -----
    To get a tuple containing the keys of the registered codecs::

        >>> get_codecs()                        # +ELLIPSIS
        ('ascii', 'big5', 'big5hkscs', 'cp037'... 'utf_8', 'utf_8_sig')
    """
    return tuple(codec for codec in codecs)


def get_description(codeckey: str) -> str:
    """Provide the description for the given codec.

    :param codeckey: The key for the codec.
    :return: The description of the codec as a :class:`str`.
    :rtype: str

    Usage
    -----
    To get the description for the given codec key::

        >>> get_description('ascii')
        'RFC20 The ASCII format for Network Interchange.'

    """
    info = codecs[codeckey]
    return info.description


def multidecode(
    value: int | str | bytes,
    codecs_: Iterator[str] | None = None
) -> dict[str, str]:
    """Provide the character for the given address for each of the
    given character sets.

    :param value: The address to decode.
    :param codec_: The codecs to decode to.
    :return: The decoded value for each character set as a :class:`dict`.
    :rtype: dict

    Address Formats
    ---------------
    The understood :class:`str` formats for manual input are:

    *   Character: A string with length equal to one.
    *   Code Point: The prefix "U+" followed by a hexadecimal number.
    *   Binary String: The prefix "0b" followed by a binary number.
    *   Hex String: The prefix "0x" followed by a hexadecimal number.

    The following formats are available for use through the API:

    *   Bytes: A :class:`bytes`.
    *   Integer: An :class:`int`.

    Usage
    -----
    To get the character for the given address for each of the registered
    codecs::

        >>> address = '0x61'
        >>> multidecode(address)                # +ELLIPSIS
        {'ascii': 'a', 'big5': 'a'... 'utf_8_sig': 'a'}

    If you just want the UTF-8 character::

        >>> value = 'a'
        >>> codecs_ = ('utf_8',)
        >>> multidecode(value, codecs_)
        {'utf_8': 'a',}

    """
    # Coerce the given value into bytes.
    value = util.to_bytes(value)

    # Decode the value into the character sets.
    results = {}
    if codecs_ is None:
        codecs_ = (codec for codec in get_codecs())
    for codec in codecs_:
        b = value

        # Pad for 2 or 4 byte codecs.
        while len(b) < codecs[codec].size:
            if codecs[codec].endian == 'little':
                b = b + b'\x00'
            else:
                b = b'\x00' + b

        # Decode.
        try:
            results[codec] = b.decode(codec)
        except UnicodeDecodeError:
            results[codec] = ''
    return results


def multiencode(
    value: bytes | int | str,
    codecs_: Iterator[str] | None = None
) -> dict[str, bytes]:
    """Provide the address for the given character for each of the
    given character sets.

    :param value: The character to encode.
    :param codecs_: The codecs to encode to.
    :return: The encoded value for each character set as a :class:`dict`.
    :rtype: dict

    Character Formats
    -----------------
    The understood :class:`str` formats available for manual input are
    (all formats are big endian unless otherwise stated):

    *   Character: A string with length equal to one.
    *   Code Point: The prefix "U+" followed by a hexadecimal number.
    *   Binary String: The prefix "0b" followed by a binary number.
    *   Octal String: The prefix "0o" followed by an octal number.
    *   Decimal String: The prefix "0d" followed by a decimal number.
    *   Hex String: The prefix "0x" followed by a hexadecimal number.

    The following formats are available for use through the API:

    *   Bytes: A :class:`bytes` that decodes to a valid UTF-8 character.
    *   Integer: An :class:`int` within the range 0x00 <= x <= 0x10FFFF.

    Usage
    -----
    To encode a one character :class:`str` with all registered codecs::

        >>> value = 'a'
        >>> multiencode(value)                  # +ELLIPSIS
        {'ascii': b'a', 'big5': b'a'... 'utf_8_sig': b'\xef\xbb\xbfa'}

    If you just want the UTF-8 address::

        >>> value = 'a'
        >>> codecs_ = ('utf_8',)
        >>> multiencode(value, codecs_)
        {'utf_8': b'a',}

    """
    value = util.to_char(value)
    if codecs_ is None:
        codecs_ = (codec for codec in get_codecs())
    results = {}
    for codec in codecs_:
        try:
            results[codec] = value.encode(codec)
        except UnicodeEncodeError:
            results[codec] = b''
    return results
