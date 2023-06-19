"""
db
~~

Tools for reading the Unicode database and related information.
"""
from bisect import bisect
from collections import defaultdict
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from importlib.resources import as_file, files
from json import load
from zipfile import ZipFile

from charex import util


# Database configuration.
PKG_DATA = files('charex.data')
FILE_PATH_MAP = 'path_map.json'
FILE_PROP_MAP = 'prop_map.json'
PATH_PROPERTY_ALIASES = 'propertyaliases'
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
class PropertyAlias:
    alias: str
    name: str
    other: tuple[str, ...]


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


@dataclass(eq=True, order=True)
class ValueRange:
    start: int
    stop: int
    value: str

    def __repr__(self):
        cls = self.__class__.__name__
        start = f'0x{self.start:04x}'
        stop = f'0x{self.stop:04x}'
        return f'{cls}({start}, {stop}, {self.value!r})'


# Common data types.
Content = Sequence[str]
PathMap = dict[str, PathInfo]
PropMap = dict[str, str]
Record = tuple[str, ...]
Records = tuple[Record, ...]

# File data structure types.
PropertyAliases = dict[str, PropertyAlias]
SingleValue = defaultdict[str, str]
SingleValues = dict[str, SingleValue]
SimpleList = set[str]
SimpleLists = dict[str, SimpleList]
UnicodeData = dict[str, UCD]
ValueAliases = dict[str, dict[str, ValueAlias]]
ValueRanges = tuple[ValueRange, ...]


# Default value handler for defaultdicts.
class Default:
    """Set the default value for a defaultdict."""
    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self) -> str:
        return self.value


# Query data.
def get_value_for_code(prop: str, code: str) -> str:
    """Retrieve the value of a property for a character."""
    alias = alias_property(prop).casefold()
    key = cache.prop_map[alias]
    kind = cache.path_map[key].kind

    by_kind = {
        'derived_normal': get_derived_normal,
        'prop_list': get_prop_list,
        'simple_list': get_simple_list_by_code,
        'single_value': get_single_value_by_code,
        'unicode_data': get_unicode_data_by_code,
        'value_range': get_value_range_by_code,
    }
    value = by_kind[kind](prop, code, key)
    return alias_value(prop, value)


def get_derived_normal(prop: str, code: str, key: str) -> str:
    """Get the value of a property stored in a `derived_normal` file
    for the given code point.
    """
    single, simple = getattr(cache, key)
    if prop in single:
        return single[prop][code]
    if code in simple[prop]:
        return 'Y'
    return 'N'


def get_prop_list(prop: str, code: str, key: str) -> str:
    """Get the value of a property stored in a `prop_list` file
    for the given code point.
    """
    simple_list = getattr(cache, key)
    if code in simple_list[prop]:
        return 'Y'
    return 'N'


def get_simple_list_by_code(prop: str, code: str, key: str) -> str:
    """Get the value of a property stored in a `simple_list` file
    for the given code point.
    """
    simple_list = getattr(cache, key)
    if code in simple_list:
        return 'Y'
    return 'N'


def get_single_value_by_code(prop: str, code: str, key: str) -> str:
    """Get the value of a property stored in a `single_value` file
    for the given code point.
    """
    single_value = getattr(cache, key)
    value = single_value[code]

    if value == '<script>':
        value = get_value_for_code('sc', code)

    return value


def get_unicode_data_by_code(prop: str, code: str, key: str) -> str:
    """Get the value of a property stored in a `unicode_data` file
    for the given code point.
    """
    unicode_data = getattr(cache, key)
    ucd = unicode_data[code]
    return getattr(ucd, prop)


def get_value_range_by_code(prop: str, code: str, key: str) -> str:
    """Get the value of a property stored in a `value_range` file
    for the given code point.
    """
    vrs = getattr(cache, key)
    n = int(code, 16)
    starts = tuple(vr.start for vr in vrs)
    index = bisect(starts, n)
    return vrs[index - 1].value


# Load data file by kind.
def load_derived_normal(info: PathInfo) -> tuple[SingleValues, SimpleLists]:
    """Load a data file with derived normalization properties."""
    docs: list[list[str]] = []
    doc: list[str] = []
    lines = load_from_archive(info)
    for line in lines:
        if 'Property:' in line:
            docs.append(doc)
            doc = list()
        doc.append(line)
    else:
        docs.append(doc)

    singles: SingleValues = {}
    simples: SimpleLists = {}
    for doc in docs:
        records, missing = parse(doc, True)
        missing = missing.split(';')[-1]
        if not records:
            continue

        prop = records[0][1]
        prop = alias_property(prop).casefold()
        num_fields = len(records[0])
        if num_fields == 2:
            simples.setdefault(prop, set())
            for rec in records:
                code, _ = rec
                simples[prop].add(code)

        elif num_fields == 3:
            singles.setdefault(prop, defaultdict(Default(missing)))
            for rec in records:
                code, _, value = rec
                singles[prop][code.casefold()] = value

        else:
            raise ValueError(f'{prop} has {num_fields} fields.')

    return singles, simples


def load_prop_list(info: PathInfo) -> SimpleLists:
    """Load a data file with simple list for multiple properties."""
    records, _ = parse(info, True)
    data: SimpleLists = {}
    for rec in records:
        code, long = rec
        prop = alias_property(long)
        prop = prop.casefold()
        data.setdefault(prop, set())
        data[prop].add(code.casefold())
    return data


def load_property_alias(info: PathInfo) -> PropertyAliases:
    """Load a data file that contains property aliases."""
    records, _ = parse(info)
    data: PropertyAliases = {}
    for rec in records:
        alias, name, *other = rec
        key = name.casefold()
        data[key] = PropertyAlias(alias, name, tuple(other))
    return data


def load_simple_list(info: PathInfo) -> SimpleList:
    """Load a simple list of values from Unicode data."""
    records, _ = parse(info)
    return {rec[0].casefold() for rec in records}


def load_single_value(info: PathInfo) -> SingleValue:
    """Load a data file that contains a simple mapping of code point
    to value.
    """
    records, missing = parse(info, True)
    data = defaultdict(Default(missing))
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


def load_value_range(info: PathInfo) -> ValueRanges:
    """Load a data file that contains a list of Unicode ranges."""
    records, missing = parse(info)
    data = []
    last_stop = 0x0000
    for rec in records:
        range_, value = rec
        start, stop = [int(n, 16) for n in range_.split('..')]
        stop += 1
        if last_stop != start:
            data.append(ValueRange(last_stop, start, missing))
        data.append(ValueRange(start, stop, value))
        last_stop = stop
    if last_stop != util.LEN_UNICODE:
        data.append(ValueRange(last_stop, util.LEN_UNICODE, missing))
    return tuple(data)


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


def load_prop_map() -> PropMap:
    """Load the map of Unicode properties to the key for the archive they
    are stored in.
    """
    path = PKG_DATA / FILE_PROP_MAP
    fh = path.open()
    map = load(fh)
    fh.close()
    return map


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
def alias_property(long: str) -> str:
    """Return the alias for a property."""
    alias = long
    try:
        pa = cache.property_alias[long.casefold()]
        alias = pa.alias
    except KeyError:
        pass
    return alias


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
def parse(file: PathInfo | Content, split=False) -> tuple[Records, str]:
    """Perform basic parsing on a Unicode data file."""
    if isinstance(file, PathInfo):
        lines = load_from_archive(file)
        delim = file.delim
    else:
        lines = file
        delim = ';'

    missing = ''
    missing_vrs = parse_missing(lines)
    if missing_vrs:
        missing = missing_vrs[0].value

    lines = strip_comments(lines)
    records = split_fields(lines, delim, split)
    return records, missing


def parse_missing(lines: Content) -> ValueRanges:
    """Parse Unicode missing values from data files."""
    data = []
    lines = [line[12:] for line in lines if line.startswith('# @missing: ')]
    records = split_fields(lines, ';', False)
    for rec in records:
        range_, value, *other = rec
        start, stop = [int(n, 16) for n in range_.split('..')]
        stop += 1
        value = ';'.join((value, *other))
        data.append(ValueRange(start, stop, value))
    return tuple(data)


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


# Miscellaneous functions for manual testing of loaded data.
def find_gap_in_value_ranges(vrs: ValueRanges) -> int | None:
    """Find the index of the first gap in the value ranges."""
    last_stop = 0x0000
    for i, vr in enumerate(vrs):
        if vr.start != last_stop:
            return i
        last_stop = vr.stop
    if last_stop != util.LEN_UNICODE:
        return i + 1
    return None


# File data cache.
class FileCache:
    __path_map = load_path_map()
    __prop_map = load_prop_map()

    def __init__(self) -> None:
        self.__derived_normal: tuple[SingleValues, SimpleLists] = (
            dict(), dict(),
        )
        self.__property_alias: PropertyAliases = dict()
        self.__prop_list: SimpleLists = dict()
        self.__simple_list: SimpleLists = dict()
        self.__single_value: SingleValues = dict()
        self.__unicode_data: UnicodeData = dict()
        self.__value_aliases: ValueAliases = dict()
        self.__value_range: dict[str, ValueRanges] = dict()

    def __getattr__(self, name:str):
        try:
            pi = self.path_map[name]
        except KeyError:
            raise AttributeError(name)

        if pi.kind == 'unicode_data':
            if not self.__unicode_data:
                unicode_data = load_unicode_data(pi)
                self.__unicode_data.update(unicode_data)
            return self.__unicode_data

        elif pi.kind == 'prop_list':
            if name not in self.__prop_list:
                prop_list = load_prop_list(pi)
                self.__prop_list.update(prop_list)
            return self.__prop_list

        elif pi.kind == 'simple_list':
            if name not in self.__simple_list:
                self.__simple_list[name] = load_simple_list(pi)
            return self.__simple_list[name]

        elif pi.kind == 'single_value':
            if name not in self.__single_value:
                self.__single_value[name] = load_single_value(pi)
            return self.__single_value[name]

        elif pi.kind == 'value_range':
            if name not in self.__value_range:
                self.__value_range[name] = load_value_range(pi)
            return self.__value_range[name]

        elif pi.kind == 'derived_normal':
            if not any(self.__derived_normal):
                single, simple = load_derived_normal(pi)
                self.__derived_normal[0].update(single)
                self.__derived_normal[1].update(simple)
            return self.__derived_normal

    @property
    def path_map(self) -> PathMap:
        return self.__path_map

    @property
    def prop_map(self) -> PropMap:
        return self.__prop_map

    @property
    def property_alias(self) -> PropertyAliases:
        if not self.__property_alias:
            info = self.path_map[PATH_PROPERTY_ALIASES]
            data = load_property_alias(info)
            self.__property_alias.update(data)
        return self.__property_alias

    @property
    def value_aliases(self) -> ValueAliases:
        if not self.__value_aliases:
            info = self.path_map[PATH_VALUE_ALIASES]
            data = load_value_aliases(info)
            self.__value_aliases.update(data)
        return self.__value_aliases


cache = FileCache()


if __name__ == '__main__':
    value = get_value_for_code('emoji', '1f600')
    print(value)

