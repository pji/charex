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


# Database configuration.
PKG_DATA = files('charex.data')
FILE_PATH_MAP = 'path_map.json'
PATH_VALUE_ALIASES = 'propertyvaluealiases'
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


# Data record structures.
@dataclass(repr=True, eq=True)
class PathInfo:
    path: str
    archive: str
    kind: str
    delim: str


@dataclass(repr=True, eq=True)
class UCD:
    """A record from the UnicodeData.txt file for Unicode 14.0.0.

    :param code: The address for the character in Unicode.
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
    code: str
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


@dataclass(repr=True, eq=True)
class ValueAlias:
    property: str
    alias: str
    name: str
    other: tuple[str, ...]


@dataclass(repr=True, eq=True, order=True)
class ValueRange:
    start: int
    stop: int
    value: str


# Common data types.
Content = Sequence[str]
PathMap = dict[str, PathInfo]
Record = tuple[str, ...]
Records = tuple[Record, ...]

# File data structure types.
SingleValue = defaultdict[str, str]
SingleValues = dict[str, SingleValue]
UnicodeData = dict[str, UCD]
ValueAliases = dict[str, dict[str, ValueAlias]]
ValueRanges = tuple[ValueRange, ...]


# Load data file by kind.
def load_value_range(info: PathInfo) -> ValueRanges:
    """Load a data file that contains a list of Unicode ranges."""
    lines = load_from_archive(info)
    lines = strip_comments(lines)
    records = split_fields(lines, info.delim, False)
    data = []
    for rec in records:
        range_, value = rec
        start_code, stop_code = range_.split('..')
        start = int(start_code, 16)
        stop = int(stop_code, 16) + 1
        vr = ValueRange(start, stop, value)
        data.append(vr)
    return tuple(data)


def load_single_value(info: PathInfo) -> SingleValue:
    """Load a data file that contains a simple mapping of code point
    to value.
    """
    lines = load_from_archive(info)
    lines = strip_comments(lines)
    records = split_fields(lines, info.delim)
    data = defaultdict(str)
    for rec in records:
        code, value = rec
        code = code.casefold()
        data[code.strip()] = value.strip()
    return data


def load_unicode_data(info: PathInfo) -> UnicodeData:
    """Load data from a file that is structured like UnicodeData.txt."""
    lines = load_from_archive(info)
    lines = strip_comments(lines)
    records = split_fields(lines, info.delim)
    data = {}
    for i, rec in enumerate(records):
        code, name, *other = rec
        if not name.endswith('First>'):
            key = code.casefold()
            data[key] = UCD(code.upper(), name, *other)
        elif name.endswith('Last>'):
            pass
        else:
            start = int(code, 16)
            stop = int(records[i + 1][0], 16) + 1
            for n in range(start, stop):
                code = f'{n:04x}'.upper()
                key = code.casefold()
                if start in UCD_RANGES:
                    name = UCD_RANGES[start]
                    if name.startswith('HANGUL'):
                        name += build_hangul_name(code)
                    else:
                        name += code
                data[key] = UCD(code, name, *other)
    return data


def load_value_aliases(info: PathInfo) -> ValueAliases:
    """Load a data file that contains information about property
    value aliases.
    """
    lines = load_from_archive(info)
    lines = strip_comments(lines)
    records = split_fields(lines, info.delim)
    data: ValueAliases = {}
    for rec in records:
        prop, alias, long, *other = rec
        va = ValueAlias(prop, alias, long, tuple(other))
        prop = prop.casefold()
        long = long.casefold()
        data.setdefault(prop, dict())
        data[prop][long] = va
    return data


# Basic file reading.
def load_path_map() -> PathMap:
    """Load the map of Unicode data files to the archive they are
    stored in.
    """
    path = PKG_DATA / FILE_PATH_MAP
    fh = path.open()
    json = load(fh)
    fh.close()
    return {key: PathInfo(*json[key]) for key in json}


def load_from_archive(info: PathInfo, codec: str = 'utf8') -> Content:
    """Read data from a zip archive."""
    path = PKG_DATA / info.archive
    with as_file(path) as sh:
        with ZipFile(sh) as zh:
            with zh.open(info.path) as zch:
                blines = zch.readlines()
    lines = [bline.decode(codec) for bline in blines]
    return tuple(line.rstrip() for line in lines)


# Data cross-referencing utilities.
def alias_value(prop: str, long: str) -> str:
    """Return the alias for a property value."""
    alias = long
    try:
        va = cache.value_aliases[prop.casefold()][long.casefold()]
        alias = va.alias
    except KeyError:
        pass
    return alias


def build_hangul_name(code: str) -> str:
    """Build the name for a Hangul syllable."""
    s = int(code, 16)
    parts = decompose_hangul(s)

    data = cache.jamo
    codes = (f'{part:04x}' for part in parts)
    return ''.join(data[code] for code in codes)


# Basic file processing utilities.
def split_fields(
    lines: Content,
    delim: str,
    fill_range: bool = True
) -> Records:
    """Split the data from a delimited text file into records."""
    records = []
    for line in lines:
        split = line.split(delim)
        rec = tuple(s.strip() for s in split)
        if '..' in rec[0] and fill_range:
            for item in split_range(rec):
                records.append(tuple(item))
        else:
            records.append(rec)
    return tuple(records)


def split_range(rec: Record) -> Generator[Record, None, None]:
    """Split a unicode range into individual records."""
    values, *other = rec
    codes = values.split('..')
    start = int(codes[0], 16)
    stop = start + 1
    if len(codes) > 1:
        stop = int(codes[1], 16) + 1
    for n in range(start, stop):
        yield (f'{n:04x}', *other)


def strip_comments(lines: Content) -> Content:
    """Remove comments and blank lines from a file."""
    lines = [line.split('#', 1)[0] for line in lines]
    return tuple(line for line in lines if line)


# Unicode defined algorithms.
def decompose_hangul(s: int) -> tuple[int, int, int]:
    """Given the :class:`int` for a Unicode Hangul code point, return
    the ints resulting from decomposing the original code point. This
    is mainly used for constructing the names for Hangul syllables.
    See the Unicode standard section 3.12 "Conjoining Jamo Behavior."

    https://www.unicode.org/versions/Unicode14.0.0/ch03.pdf
    """
    SBASE = 0xac00
    LBASE = 0x1100
    VBASE = 0x1161
    TBASE = 0x11a7
    LCOUNT = 19
    VCOUNT = 21
    TCOUNT = 28
    NCOUNT = VCOUNT * TCOUNT
    SCOUNT = LCOUNT * NCOUNT

    sindex = s - SBASE
    lindex = sindex // NCOUNT
    vindex = (sindex % NCOUNT) // TCOUNT
    tindex = sindex % TCOUNT

    return (
        LBASE + lindex,
        VBASE + vindex,
        TBASE + tindex,
    )


# File data cache.
class FileCache:
    __path_map = load_path_map()

    def __init__(self) -> None:
        self.__single_value: SingleValues = dict()
        self.__value_aliases: ValueAliases = dict()

    def __getattr__(self, name:str):
        try:
            pi = self.path_map[name]
        except KeyError:
            raise AttributeError(name)

        if pi.kind == 'single_value':
            if name not in self.__single_value:
                pi = self.path_map[name]
                self.__single_value[name] = load_single_value(pi)
            return self.__single_value[name]

    @property
    def path_map(self) -> PathMap:
        return self.__path_map

    @property
    def value_aliases(self) -> ValueAliases:
        if not self.__value_aliases:
            info = self.path_map[PATH_VALUE_ALIASES]
            data = load_value_aliases(info)
            self.__value_aliases.update(data)
        return self.__value_aliases


cache = FileCache()


if __name__ == '__main__':
    # data = cache.jamo
    pi = PathInfo('Blocks.txt', 'UCD.zip', 'value_range', ';')
    data = load_value_range(pi)
