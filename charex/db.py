"""
db
~~

Tools for reading the Unicode database and related information.
"""
from collections import defaultdict
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from importlib.resources import as_file, files
from json import load
from zipfile import ZipFile


PKG_DATA = files('charex.data')
FILE_SOURCES = 'props.json'
MISSING_PREFIX = '# @missing: '
MISSING_DELIM = ';'
UCD_RANGES = defaultdict(str, {
    0x3400: 'CJK UNIFIED IDEOGRAPH-',
    0x4e00: 'CJK UNIFIED IDEOGRAPH-',
    0xac00: 'HANGUL SYLLABLE ',
    0xf900: 'CJK UNIFIED IDEOGRAPH-',
    0xfa70: 'CJK UNIFIED IDEOGRAPH-',
    0x17000: 'TANGUT IDEOGRAPH-',
    0x18d00: 'TANGUT IDEOGRAPH-',
    0x18b00: 'KHITAN SMALL SCRIPT CHARACTER-',
    0x1b170: 'NUSHU CHARACTER-',
    0x20000: 'CJK UNIFIED IDEOGRAPH-',
    0x2a700: 'CJK UNIFIED IDEOGRAPH-',
    0x2b740: 'CJK UNIFIED IDEOGRAPH-',
    0x2b820: 'CJK UNIFIED IDEOGRAPH-',
    0x2ceb0: 'CJK UNIFIED IDEOGRAPH-',
    0x2f800: 'CJK UNIFIED IDEOGRAPH-',
    0x30000: 'CJK UNIFIED IDEOGRAPH-',
})



# Data records.
@dataclass
class PropSource:
    file: str
    path: str
    kind: str
    delim: str


@dataclass
class UCD:
    """A record from the UnicodeData.txt file for Unicode 14.0.0.

    :param code_point: The address for the character in Unicode.
    :param name: The name for the code point.
    :param category: The type of code point, such as "control" or
        "lower case letter."
    :param canonical_combining_class: The combining class of the code point,
        largely used for CJK languages.
    :param bidi_class: Unknown.
    :param decomposition_type: Whether and how the character can be
        decomposed.
    :param decimal: If the character is a decimal digit, this is its
        numeric value.
    :param digit: If the character is a digit, this is its numeric
        value.
    :param numeric: If the character is a number, this is its numeric
        value.
    :param bidi_mirrored: Unknown.
    :param unicode_1_name: The name of the character used in Unicode
        version 1. This is mainly needed to give names to control
        characters.
    :param iso_comment: Unknown.
    :param simple_uppercase_mapping: The code point for the upper case
        version of the code point.
    :param simple_lowercase_mapping: The code point for the lower case
        version of the code point.
    :param simple titlecase_mapping: The code point for the title case
        version of the code point.
    """
    address: str
    na: str
    gc: str
    ccc: str
    bc: str
    dt: str
    decimal: str
    digit: str
    nv: str
    bidi_m: str
    na1: str
    isc: str
    suc: str
    slc: str
    stc: str


# Types for Unicode files.
UnicodeData = dict[str, UCD]


# Generic types.
Lines = tuple[str, ...]
PropSources = dict[str, PropSource]
Record = tuple[str, ...]
Records = tuple[Record, ...]


# Read the Unicode data files.
def get_unicode_data(src: PropSource) -> UnicodeData:
    """Get the data from UnicodeData.txt."""
    def fill_range(
        start: int, stop: int, fields: Record
    ) -> Generator[UCD, None, None]:
        prefix = UCD_RANGES[start]
        for n in range(start, stop):
            code = f'{n:04x}'
            name = prefix
#             if name.startswith('HANGUL'):
#                 name += get_jamo_name(n)
            if name:
                name += code
            yield UCD(code, name, *fields[2:])

    records, _ = get_source(src)
    data: UnicodeData = {}
    for i, fields in enumerate(records):
        code, name, *_ = fields
        if name.endswith('Last>'):
            pass
        elif not name.endswith('First>'):
            data[code.casefold()] = UCD(*fields)
        else:
            start = int(code, 16)
            stop = int(records[i + 1][0], 16) + 1
            for ud in fill_range(start, stop, fields):
                data[ud.address.casefold()] = ud
    return data


# File parsing utilities.
def get_source(src: PropSource) -> tuple[Records, Records]:
    """Read a data source and parse the contents inro records."""
    lines = read_resource(src)
    missing = parse_missing(lines)
    lines = strip_comments(lines)
    records = split_fields(lines, src.delim)
    return records, missing


def parse_missing(lines: Sequence[str]) -> Records:
    """Parse the missing value from a document."""
    pfw = len(MISSING_PREFIX)
    lines = [line[pfw:] for line in lines if line.startswith(MISSING_PREFIX)]
    lines = strip_comments(lines)
    src = MISSING_DELIM
    return split_fields(lines, src)


def parse_range(field: str) -> range:
    values = field.split('..')
    start = int(values[0], 16)
    stop = start + 1
    if len(values) == 2:
        stop = int(values[1], 16) + 1
    return range(start, stop)


def split_fields(lines: Sequence[str], delim: str) -> Records:
    """Split lines into fields."""
    split = [line.split(delim) for line in lines]
    records = []
    for record in split:
        record = [field.strip() for field in record]
        records.append(tuple(record))
    return tuple(records)


def strip_comments(lines: Sequence[str]) -> Lines:
    """Remove the comments and blank lines from file contents."""
    done = []
    for line in lines:
        if not line:
            continue
        if line.startswith('#'):
            continue
        line = line.split('#', 1)[0]
        done.append(line.rstrip())
    return tuple(done)


# File reading.
def load_props_file() -> PropSources:
    """Load the map of Unicode character properties to their location
    in the Unicode data files.
    """
    path = PKG_DATA / FILE_SOURCES
    fh = path.open()
    json = load(fh)
    fh.close()
    return {key: PropSource(*json[key]) for key in json}


def read_resource(src: PropSource, codec: str = 'utf8') -> Lines:
    """Read the data in from the given source of property information."""
    path = PKG_DATA / src.file
    with as_file(path) as sh:
        with ZipFile(sh) as zh:
            with zh.open(src.path) as zch:
                blines = zch.readlines()
    lines = [bline.decode(codec) for bline in blines]
    return tuple(line.rstrip() for line in lines)


if __name__ == '__main__':
    sources = load_props_file()
    # lines = read_resource(sources['blk'])
    # lines = strip_comments(lines)
    # records = split_fields(lines, sources['age'])
    # vrange = parse_range(records[-1][0])
    # missing = parse_missing(lines)
    # data = get_unicode_data(sources['na'])
    data = get_single_values(sources['jsn'])
    for item in data:
        print(item, ucds[item])
