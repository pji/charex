"""
charex
~~~~~~

Tools for exploring unicode characters and other character sets.
"""
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from json import loads
import unicodedata as ucd

from charex import util
from charex.escape import schemes


# Exceptions.
class UndefinedCharacterError(ValueError):
    """The character is not defined in Unicode data."""


# Data classes.
@dataclass(order=True)
class ValueRange:
    """The range of characters that have a property value."""
    start: int
    stop: int
    value: str


@dataclass
class Property:
    alias: str
    long: str
    other: tuple[str, ...]


@dataclass
class PropertyValue:
    property: str
    alias: str
    long: str
    other: tuple[str, ...]


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


@dataclass
class UnicodeDatum:
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
    code_point: str
    name: str
    general_category: str
    canonical_combining_class: str
    bidi_class: str
    decomposition_type: str
    decimal: str
    digit: str
    numeric_value: str
    bidi_mirrored: str
    unicode_1_name: str
    iso_comment: str
    simple_uppercase_mapping: str
    simple_lowercase_mapping: str
    simple_titlecase_mapping: str


# Caches.
unicodedata_cache: dict[str, UnicodeDatum] = {}


# Types:
PropListCache = dict[str, defaultdict[str, bool]]
PropsCache = dict[str, Property]
PropValsCache = dict[str, dict[str, PropertyValue]]
MultiValCache = dict[str, defaultdict[str, tuple[str, ...]]]
RangeListCache = dict[str, tuple[ValueRange, ...]]
SingleValCache = dict[str, defaultdict[str, str]]
UnicodeDataCache = dict[str, UCD]


# Classes.
class Cache:
    multis = ('scx',)
    ranges = ('age', 'blk', 'sc',)
    singles = ('hst',)

    def __init__(self) -> None:
        self.__multival: MultiValCache = {}
        self.__proplist: PropListCache = {}
        self.__props: PropsCache = {}
        self.__propvals: PropValsCache = {}
        self.__rangelist: RangeListCache = {}
        self.__singleval: SingleValCache = {}
        self.__unicodedata: UnicodeDataCache = {}

    @property
    def multival(self) -> MultiValCache:
        if not self.__multival:
            self.__multival = {
                key: self.get_multiple_value_property(key)
                for key in self.multis
            }
        return self.__multival

    @property
    def props(self) -> PropsCache:
        if not self.__props:
            self.__props = self.get_properties()
        return self.__props

    @property
    def proplist(self) -> PropListCache:
        if not self.__proplist:
            proplist = self.parse_binary_properties('proplist')
            for prop in proplist:
                alias = alias_property(prop, True)
                alias = alias.casefold()
                self.__proplist[alias] = proplist[prop]
        return self.__proplist

    @property
    def propvals(self) -> PropValsCache:
        if not self.__propvals:
            self.__propvals = self.get_property_values()
        return self.__propvals

    @property
    def rangelist(self) -> RangeListCache:
        if not self.__rangelist:
            self.__rangelist = {
                key: self.get_value_ranges(key)
                for key in self.ranges
            }
        return self.__rangelist

    @property
    def singleval(self) -> SingleValCache:
        if not self.__singleval:
            self.__singleval = {
                key: self.get_single_value_property(key)
                for key in self.singles
            }
        return self.__singleval

    @property
    def unicodedata(self) -> UnicodeDataCache:
        if not self.__unicodedata:
            lines = util.read_resource('unicodedata')
            data: dict[str, UCD] = {}
            for i, line in enumerate(lines):
                fields = line.split(';')
                datum = UCD(*fields)
                n = int(datum.address, 16)
                data[chr(n)] = datum

                if (
                    datum.na.startswith('<')
                    and datum.na.endswith('First>')
                ):
                    nextline = lines[i + 1]
                    next_fields = nextline.split(';')
                    start = int(datum.address, 16)
                    stop = int(next_fields[0], 16) + 1
                    for n in range(start, stop):
                        gap_fields = (f'{n:04x}'.upper(), *fields[1:])
                        datum = UCD(*gap_fields)
                        n = int(datum.address, 16)
                        data[chr(n)] = datum

            self.__unicodedata = data
        return self.__unicodedata

    def alias_property(self, prop: str) -> str:
        prop = prop.casefold()
        return self.props[prop].alias

    def alias_property_value(self, prop: str, value: str) -> str:
        prop = prop.casefold()
        if prop in self.propvals:
            value = self.propvals[prop][value.casefold()].alias
        return value

    def get_multiple_value_property(
        self,
        source: str
    ) -> defaultdict[str, tuple[str, ...]]:
        missing, data = self.parse_with_missing(source)
        mvalue = MissingTuple(tuple(missing.split()))
        values: defaultdict[str, tuple[str, ...]] = defaultdict(mvalue)
        for datum in data:
            points, value = datum
            parts = points.split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            for i in range(start, stop):
                values[chr(i)] = tuple(value.split())
        return values

    def get_properties(self) -> PropsCache:
        data = self.parse('props')
        result: PropsCache = {}
        for datum in data:
            alias, long, *other = datum
            prop = Property(alias, long, tuple(other))
            for name in datum:
                result[name.casefold()] = prop
        return result

    def get_property_values(self) -> PropValsCache:
        data = self.parse('propvals')
        result: PropValsCache = {}
        for datum in data:
            prop, *names = datum
            alias, long, *other = names
            propval = PropertyValue(prop, alias, long, tuple(other))
            prop = prop.casefold()
            result.setdefault(prop, dict())
            for name in names:
                result[prop][name.casefold()] = propval
        return result

    def get_value_ranges(self, src: str) -> tuple[ValueRange, ...]:
        """Get the tuple of derived ages. The derived age of a character
        is the Unicode version where the character was assigned to a code
        point.

        :param src: The source key for the values.
        :return: The possible ages as a :class:`tuple`.
        :rtype: tuple
        """
        results = (ValueRange(*vr) for vr in self.parse_range_for_value(src))
        return tuple(results)

    def get_single_value_property(self, source: str) -> defaultdict[str, str]:
        missing, data = self.parse_with_missing(source)
        missing = self.alias_property_value(source, missing)
        mvalue = MissingValue(missing)
        result = defaultdict(mvalue)
        for datum in data:
            points, value = datum
            parts = points.split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            for i in range(start, stop):
                result[chr(i)] = self.alias_property_value(source, value)
        return result

    def parse(self, source: str) -> tuple[tuple[str, ...], ...]:
        lines = util.read_resource(source)
        lines = self.strip_comments(lines)
        data = self.parse_sdt(lines)
        return data

    def parse_binary_properties(
        self,
        source: str
    ) -> dict[str, defaultdict[str, bool]]:
        data = self.parse(source)
        missing = MissingBool(False)
        result: dict[str, defaultdict[str, bool]] = {}
        for datum in data:
            point, key = datum
            if key not in result:
                result[key] = defaultdict(missing)
            parts = point.split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            for i in range(start, stop):
                result[key][chr(i)] = True

        return result

    def parse_missing(
        self,
        lines: Sequence[str]
    ) -> tuple[tuple[str, ...], ...]:
        prefix = '# @missing: '
        lines = [line[12:] for line in lines if line.startswith(prefix)]
        lines = self.strip_comments(lines)
        return self.parse_sdt(lines)

    def parse_with_missing(
        self,
        source: str
    ) -> tuple[str, tuple[tuple[str, ...], ...]]:
        lines = util.read_resource(source)

        missing_data = self.parse_missing(lines)
        missing = missing_data[0][-1]

        lines = self.strip_comments(lines)
        data = self.parse_sdt(lines)
        return missing, data

    def parse_range_for_value(
        self,
        source: str
    ) -> tuple[tuple[int, int, str], ...]:
        missing, data = self.parse_with_missing(source)
        values = []
        for datum in data:
            parts = datum[0].split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            value = (start, stop, datum[1])
            values.append(value)
        return tuple(fill_gaps(values, missing))

    def parse_sdt(
        self,
        lines: tuple[str, ...]
    ) -> tuple[tuple[str, ...], ...]:
        """Parse semicolon delimited text.

        :param lines: The lines from a semicolon delimited test file.
        :return: The lines split into data fields as a :class:`tuple`.
        :rtype: tuple
        """
        result = []
        for line in lines:
            parts = line.split(';')
            fields = (part.strip() for part in parts)
            result.append(tuple(fields))
        return tuple(result)

    def strip_comments(self, lines: Sequence[str]) -> tuple[str, ...]:
        """Remove the comments and blank lines from a data file.

        :param lines: The lines from a Unicode data file.
        :return: The lines with comments removed as a :class:`tuple`.
        :rtype: tuple
        """
        lines = [line.split('#')[0] for line in lines]
        return tuple([
            line for line in lines
            if line.strip() and not line.startswith('#')
        ])


class Character:
    cache = Cache()

    def __init__(self, value: bytes | int | str) -> None:
        value = util.to_char(value)
        self.__value = value
        self._rev_normal_cache: dict[str, tuple[str, ...]] = {}

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        name = name.casefold()

        if name in UCD.__annotations__:
            data = self.cache.unicodedata
            return getattr(data[self.value], name)

        if name in self.cache.proplist:
            return self.cache.proplist[name][self.value]

        if name in self.cache.ranges:
            rangelist = self.cache.rangelist[name]
            vr = bintree(
                rangelist,
                ord(self.value),
                len(rangelist) // 2,
                0,
                len(rangelist)
            )
            return vr.value

        if name in self.cache.multis:
            multival = self.cache.multival[name]
            value = multival[self.value]
            value = self._handle_dynamic_value(name, value)
            return value

        if name in self.cache.singles:
            singleval = self.cache.singleval[name]
            value = singleval[self.value]
            return value

        raise AttributeError(name)

    def __repr__(self) -> str:
        name = self.na
        if name == '<control>':
            name = f'<{self.na1}>'
        return f'{self.code_point} ({name})'

    # Private methods.
    def _handle_dynamic_value(
        self,
        prop: str,
        values: Sequence[str]
    ) -> tuple[str, ...]:
        result = []
        for value in values:
            if value.startswith('<') and value.endswith('>'):
                attr = self.cache.alias_property(value[1:-1])
                value = getattr(self, attr.casefold())
            result.append(value)
        return tuple(result)

    # Properties.
    @property
    def code_point(self) -> str:
        """The address for the character in the Unicode database."""
        x = ord(self.value)
        return f'U+{x:04x}'.upper()

    @property
    def value(self) -> str:
        """The code point as a string."""
        return self.__value

    # Public methods.
    def denormalize(self, form: str) -> tuple[str, ...]:
        """Return the characters that normalize to the character using
        the given form.

        :param form: The normalization form to check against.
        :return: The denormalization results in a :class:`tuple`.
        :rtype: tuple

        Usage
        -----
        To denormalize the character for the given form::

            >>> # Create the character object.
            >>> value = '<'
            >>> char = Character(value)
            >>>
            >>> # Get the denormalizations for the character.
            >>> form = 'nfkc'
            >>> char.denormalize(form)
            ('﹤', '＜')

        """
        source = f'rev_{form}'
        if source not in self._rev_normal_cache:
            lkp = Lookup(source)
            self._rev_normal_cache[source] = lkp.query(self.value)
        return self._rev_normal_cache[source]

    def escape(self, scheme: str, codec: str = 'utf8') -> str:
        """The escaped version of the character.

        :param scheme: The escape scheme to use.
        :param codec: The codec to use when escaping to a hexadecimal
            string.
        :return: A :class:`str` with the escaped character.
        :rtype: str

        Usage
        -----
        To escape the character with the given form::

            >>> value = '<'
            >>> char = Character(value)
            >>>
            >>> scheme = 'html'
            >>> char.escape(scheme)
            '&lt;'

        """
        scheme = scheme.casefold()
        fn = schemes[scheme]
        return fn(self.value, codec)

    def encode(self, codec: str) -> str:
        """The hexadecimal value for the character in the given
        character set.

        :param codec: The codec to use when encoding to a hexadecimal
            string.
        :return: A :class:`str` with the encoded character.
        :rtype: str

        Usage
        -----
        To encode the character with the given character set::

            >>> value = 'å'
            >>> char = Character(value)
            >>>
            >>> codec = 'utf8'
            >>> char.encode(codec)
            'C3 A5'

        """
        b = self.value.encode(codec)
        hexes = [f'{x:02x}'.upper() for x in b]
        return ' '.join(x for x in hexes)

    def is_normal(self, form: str) -> bool:
        """Is the character normalized to the given form?

        :param form: The normalization form to check against.
        :return: A :class:`bool` indicating whether the character is
            normalized.
        :rtype: bool

        Usage
        -----
        To determine whether the character is already normalized for
        the given scheme.

            >>> value = 'å'
            >>> char = Character(value)
            >>>
            >>> form = 'nfc'
            >>> char.is_normal(form)
            True

        """
        return ucd.is_normalized(form.upper(), self.value)

    def normalize(self, form: str) -> str:
        """Normalize the character using the given form.

        :param form: The normalization form to check against.
        :return: The normalization result as a :class:`str`.
        :rtype: str

        Usage
        -----
        To normalize the character for the given form::

            >>> value = '＜'
            >>> char = Character(value)
            >>>
            >>> form = 'nfkc'
            >>> char.normalize(form)
            '<'

        """
        return ucd.normalize(form.upper(), self.value)

    def summarize(self) -> str:
        """Return a summary of the character's information.

        :return: The character information as a :class:`str`.
        :rtype: str

        Usage
        -----
        To summarize the character::

            >>> value = 'å'
            >>> char = Character(value)
            >>>
            >>> char.summarize()
            'å U+00E5 (LATIN SMALL LETTER A WITH RING ABOVE)'
        """
        value = util.neutralize_control_characters(self.value)
        return f'{value} {self!r}'


class Lookup:
    """A data lookup.

    :param source: The key for the data source in the RESOURCES
        dictionary.
    """
    def __init__(self, source: str) -> None:
        self.__source = source
        lines = util.read_resource(source)
        json = '\n'.join(lines)
        data = loads(json)
        self.__data = {k: tuple(data[k]) for k in data}

    @property
    def data(self) -> dict[str, tuple[str, ...]]:
        """The data loaded from the data source."""
        return self.__data

    @property
    def source(self) -> str:
        """The key of the loaded data in the RESOURCES dictionary."""
        return self.__source

    def query(self, key: str) -> tuple[str, ...]:
        """Return the value for the given string from the loaded data.

        :param key: The key to lookup in the data.
        :return: The data returned in a :class:`tuple`.
        :rtype: tuple
        """
        try:
            answer = self.data[key]
        except KeyError:
            answer = tuple()
        return answer


class MissingBool:
    def __init__(self, value: bool) -> None:
        self.value = value

    def __call__(self) -> bool:
        return self.value


class MissingTuple:
    def __init__(self, value: tuple[str, ...]) -> None:
        self.value = value

    def __call__(self) -> tuple[str, ...]:
        return self.value


class MissingValue:
    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self) -> str:
        return self.value


# Utility functions.
def alias_property(longname: str, space: bool = True) -> str:
    if space:
        longname = longname.replace(' ', '_')
    return Character.cache.props[longname.casefold()].alias


def bintree(
    vranges: Sequence[ValueRange],
    address: int,
    index: int,
    min_: int,
    max_: int
) -> ValueRange:
    """Find the range of a Unicode character using a binary
    tree search.

    :param vranges: The possible ranges for Unicode characters.
    :param address: The code point of the character an an :class:`int`.
    :param index: The current location of the search cursor.
    :param min_: The minimum possible index within ages that hasn't been
        excluded by the search.
    :param max_: The maximum possible index within ages that hasn't been
        excluded by the search.
    :return: The range of the character as a
        :class:`charex.charex.ValueRange`.
    :rtype: charex.charex.ValueRange
    """
    vr = vranges[index]
    if address < vr.start:
        max_ = index
        index = min_ + (max_ - min_) // 2
        vr = bintree(vranges, address, index, min_, max_)
    elif address >= vr.stop:
        min_ = index
        index = min_ + (max_ - min_) // 2
        vr = bintree(vranges, address, index, min_, max_)
    return vr


def expand_property(prop: str) -> str:
    """Translate the short name of a Unicode property into the long
    name for that property.

    :param prop: The short name of the property.
    :return: The long name as a :class:`str`.
    :rtype: str

    Usage
    -----
    To get the long name of a Unicode property.

        >>> prop = 'cf'
        >>> expand_property(prop)
        'Case Folding'

    """
    long = Character.cache.props[prop.casefold()].long
    long = long.replace('_', ' ')
    return long


def expand_property_value(prop: str, alias: str) -> str:
    """Translate the short name of a Unicode property value into the
    long name for that property.

    :param prop: The type of property.
    :param alias: The short name to translate.
    :return: The long name of the property as a :class:`str`.
    :rtype: str

    Usage
    -----
    To get the long name for a property value::

        >>> alias = 'Cc'
        >>> prop = 'gc'
        >>> expand_property_value(prop, alias)
        'Control'

    """
    prop = prop.casefold()
    alias = alias.casefold()
    long = Character.cache.propvals[prop][alias].long
    return long.replace('_', ' ')


def fill_gaps(
    values: Sequence[tuple[int, int, str]],
    missing: str
) -> tuple[tuple[int, int, str], ...]:
    """Fill gaps in the given values."""
    values = sorted(values)
    filled = []
    for i in range(len(values) - 1):
        filled.append(values[i])
        _, stop, _ = values[i]
        nstart, _, _ = values[i + 1]
        if stop != nstart:
            gap = (stop, nstart, missing)
            filled.append(gap)
    filled.append(values[-1])
    if filled[-1][1] != util.LEN_UNICODE:
        gap = (filled[-1][1], util.LEN_UNICODE, missing)
        filled.append(gap)
    return tuple(filled)


def filter_by_property(
    prop: str,
    value: str,
    chars: Sequence[Character] | None = None
) -> tuple[Character, ...]:
    """Return all the characters with the given property value."""
    if not chars:
        chars = [Character(n) for n in range(util.LEN_UNICODE)]
    hits = [char for char in chars if getattr(char, prop) == value]
    return tuple(hits)


def get_category_members(category: str) -> tuple[Character, ...]:
    """Get all characters that are members of the given category."""
    ulen = 0x10FFFF
    members = (
        Character(n) for n in range(ulen)
        if ucd.category(chr(n)) == category
    )
    return tuple(members)


def get_properties() -> tuple[str, ...]:
    """Get the valid Unicode properties.

    :return: The properties as a :class:`tuple`.
    :rtype: tuple

    Usage
    -----
    To get the list of Unicode properties::

        >>> get_properties()                    # doctest: +ELLIPSIS
        ('cjkAccountingNumeric', 'cjkOtherNumeric',... 'XO_NFKD')

    """
    props = Character.cache.props
    result = []
    for key in props:
        if props[key] not in result:
            result.append(props[key])
    return tuple(prop.alias for prop in result)


def get_property_values(prop: str) -> tuple[str, ...]:
    """Get the valid property value aliases for a property.

    :param prop: The short name of the property.
    :return: The valid values for the property as a :class:`tuple`.
    :rtype: tuple

    Usage
    -----
    To get the valid property values::

        >>> prop = 'gc'
        >>> get_property_values(prop)           # doctest: +ELLIPSIS
        ('C', 'Cc', 'Cf', 'Cn', 'Co', 'Cs', 'L',... 'Zs')

    """
    propvals = Character.cache.propvals[prop]
    result = []
    for key in propvals:
        if propvals[key] not in result:
            result.append(propvals[key])
    return tuple(val.alias for val in result)


def get_unicode_data() -> dict[str, UnicodeDatum]:
    """Get the core Unicode data."""
    if not unicodedata_cache:
        lines = util.read_resource('unicodedata')
        data = parse_unicode_data(lines)
    return unicodedata_cache


# Data parsing functions.
def parse_unicode_data(lines: Sequence[str]) -> dict[str, UnicodeDatum]:
    """Parse the Unicode data file.

    :param lines: The contents of the Unicode data file.
    :return: The Unicode data as a :class:`dict`.
    :rtype: dict
    """
    if not unicodedata_cache:
        for i, line in enumerate(lines):
            fields = line.split(';')
            datum = UnicodeDatum(*fields)
            unicodedata_cache['U+' + datum.code_point] = datum

            if datum.name.startswith('<') and datum.name.endswith('First>'):
                nextline = lines[i + 1]
                next_fields = nextline.split(';')
                start = int(datum.code_point, 16)
                stop = int(next_fields[0], 16) + 1
                for n in range(start, stop):
                    gap_fields = (f'{n:04x}'.upper(), *fields[1:])
                    datum = UnicodeDatum(*gap_fields)
                    unicodedata_cache['U+' + datum.code_point] = datum

    return unicodedata_cache


if __name__ == '__main__':
    name = 'wspace'
    cache = Cache()
    proplist = cache.proplist
    assert name in proplist
