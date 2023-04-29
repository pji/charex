"""
charsets
~~~~~~~~

Data and functions for working with character sets.
"""
from collections.abc import Iterator
from dataclasses import dataclass
from sys import byteorder


# Data classes.
@dataclass
class CodecDetails:
    size: int = 1
    endian: str = byteorder


# Encoding schemes.',
codecs = {
    'ascii': CodecDetails(),
    'big5': CodecDetails(),
    'big5hkscs': CodecDetails(),
    'cp037': CodecDetails(),
    'cp273': CodecDetails(),
    'cp424': CodecDetails(),
    'cp437': CodecDetails(),
    'cp500': CodecDetails(),
    'cp720': CodecDetails(),
    'cp737': CodecDetails(),
    'cp775': CodecDetails(),
    'cp850': CodecDetails(),
    'cp852': CodecDetails(),
    'cp855': CodecDetails(),
    'cp856': CodecDetails(),
    'cp857': CodecDetails(),
    'cp858': CodecDetails(),
    'cp860': CodecDetails(),
    'cp861': CodecDetails(),
    'cp862': CodecDetails(),
    'cp863': CodecDetails(),
    'cp864': CodecDetails(),
    'cp865': CodecDetails(),
    'cp866': CodecDetails(),
    'cp869': CodecDetails(),
    'cp874': CodecDetails(),
    'cp875': CodecDetails(),
    'cp932': CodecDetails(),
    'cp949': CodecDetails(),
    'cp950': CodecDetails(),
    'cp1006': CodecDetails(),
    'cp1026': CodecDetails(),
    'cp1125': CodecDetails(),
    'cp1140': CodecDetails(),
    'cp1250': CodecDetails(),
    'cp1251': CodecDetails(),
    'cp1252': CodecDetails(),
    'cp1253': CodecDetails(),
    'cp1254': CodecDetails(),
    'cp1255': CodecDetails(),
    'cp1256': CodecDetails(),
    'cp1257': CodecDetails(),
    'cp1258': CodecDetails(),
    'euc_jp': CodecDetails(),
    'euc_jis_2004': CodecDetails(),
    'euc_jisx0213': CodecDetails(),
    'euc_kr': CodecDetails(),
    'gb2312': CodecDetails(),
    'gbk': CodecDetails(),
    'gb18030': CodecDetails(),
    'hz': CodecDetails(),
    'iso2022_jp': CodecDetails(),
    'iso2022_jp_1': CodecDetails(),
    'iso2022_jp_2': CodecDetails(),
    'iso2022_jp_2004': CodecDetails(),
    'iso2022_jp_3': CodecDetails(),
    'iso2022_jp_ext': CodecDetails(),
    'iso2022_kr': CodecDetails(),
    'latin_1': CodecDetails(),
    'iso8859_2': CodecDetails(),
    'iso8859_3': CodecDetails(),
    'iso8859_4': CodecDetails(),
    'iso8859_5': CodecDetails(),
    'iso8859_6': CodecDetails(),
    'iso8859_7': CodecDetails(),
    'iso8859_8': CodecDetails(),
    'iso8859_9': CodecDetails(),
    'iso8859_10': CodecDetails(),
    'iso8859_11': CodecDetails(),
    'iso8859_13': CodecDetails(),
    'iso8859_14': CodecDetails(),
    'iso8859_15': CodecDetails(),
    'iso8859_16': CodecDetails(),
    'johab': CodecDetails(),
    'koi8_r': CodecDetails(),
    'koi8_t': CodecDetails(),
    'koi8_u': CodecDetails(),
    'kz1048': CodecDetails(),
    'mac_cyrillic': CodecDetails(),
    'mac_greek': CodecDetails(),
    'mac_iceland': CodecDetails(),
    'mac_latin2': CodecDetails(),
    'mac_roman': CodecDetails(),
    'mac_turkish': CodecDetails(),
    'ptcp154': CodecDetails(),
    'shift_jis': CodecDetails(2),
    'shift_jis_2004': CodecDetails(2),
    'shift_jisx0213': CodecDetails(2),
    'utf_32': CodecDetails(4),
    'utf_32_be': CodecDetails(4, 'big'),
    'utf_32_le': CodecDetails(4, 'little'),
    'utf_16': CodecDetails(2),
    'utf_16_be': CodecDetails(2, 'big'),
    'utf_16_le': CodecDetails(2, 'little'),
    'utf_7': CodecDetails(),
    'utf_8': CodecDetails(),
    'utf_8_sig': CodecDetails(),
}


# Functions.
def multiencode(x: int | str, codecs_: Iterator[str]) -> dict[str, str]:
    if isinstance(x, str):
        x = int(x, 16)
    b_ = x.to_bytes((x.bit_length() + 7) // 8)

    results = {}
    for codec in codecs_:
        b = b_

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
