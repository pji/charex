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
    numeric: str
    bidi_mirrored: str
    unicode_1_name: str
    iso_comment: str
    simple_uppercase_mapping: str
    simple_lowercase_mapping: str
    simple_titlecase_mapping: str


# Caches.
hst_cache: defaultdict[str, str] | None = None
prop_cache: dict[str, str] = {}
proplist_cache: dict[str, defaultdict[str, bool]] = {}
propvals_cache: dict[str, dict[str, str]] = {}
range_cache: dict[str, tuple[ValueRange, ...]] = {}
script_extensions_cache: defaultdict[str, str] | None = None
unicodedata_cache: dict[str, UnicodeDatum] = {}


# Classes.
class Character:
    """One or more code points representing a character.

    :param value: The character to gather data for. See below for the
        formats the value can be passed in.
    :return: None.
    :rtype: NoneType

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
    To create a :class:`charex.Character` object for a single
    character string::

        >>> value = 'a'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for a Unicode code
    point::

        >>> value = 'U+0061'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for a binary string::

        >>> value = '0b01100001'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for an octal string::

        >>> value = '0o141'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for a decimal string::

        >>> value = '0d97'
        >>> char = Character(value)
        >>> char.value
        'a'

    To create a :class:`charex.Character` object for a hex string::

        >>> value = '0x61'
        >>> char = Character(value)
        >>> char.value
        'a'

    """
    def __init__(self, value: bytes | int | str) -> None:
        value = util.to_char(value)
        self.__value = value
        self._rev_normal_cache: dict[str, tuple[str, ...]] = {}

        # Check if the character is a defined character.
        data = get_unicode_data()
        if self.code_point.upper() not in data:
            raise UndefinedCharacterError(f'{self.code_point}')

    def __repr__(self) -> str:
        return f'{self.code_point} ({self.name})'

    @property
    def age(self) -> str:
        """The version the character was added in."""
        return get_value_from_range('age', self.value)

    @property
    def alpha(self) -> bool:
        """Characters with the Alphabetic property. For more information,
        see Chapter 4, Character Properties in Unicode.
        """
        if self.gc in ('Lt', 'Lm', 'Lo', 'Nl'):
            return True
        elif self.lower or self.upper or self.oalpha:
            return True
        return False

    @property
    def lower(self) -> bool:
        if self.gc == 'Ll' or self.olower:
            return True
        return False

    @property
    def olower(self) -> bool:
        proplist = get_proplist()
        return proplist['Other_Lowercase'][self.value]

    @property
    def upper(self) -> bool:
        if self.gc == 'Lu' or self.oupper:
            return True
        return False

    @property
    def oupper(self) -> bool:
        proplist = get_proplist()
        return proplist['Other_Uppercase'][self.value]

    @property
    def oalpha(self) -> bool:
        proplist = get_proplist()
        return proplist['Other_Alphabetic'][self.value]

    @property
    def bc(self) -> str:
        """The categories required by the Unicode Bidirectional Algorithm."""
        data = get_unicode_data()
        datum = data[self.code_point]
        alias = datum.bidi_class
        return expand_property_value('bc', alias)

    @property
    def bidi_class(self) -> str:
        """The categories required by the Unicode Bidirectional Algorithm."""
        return self.bc

    @property
    def bidi_m(self) -> bool:
        """Whether the character is a "mirrored" character in
        bidirectional text.
        """
        data = get_unicode_data()
        datum = data[self.code_point]
        alias = datum.bidi_mirrored
        if alias == 'Y':
            return True
        return False

    @property
    def bidi_mirrored(self) -> bool:
        """Whether the character is a "mirrored" character in
        bidirectional text.
        """
        return self.bidi_m

    @property
    def blk(self) -> str:
        """The Unicode block for the character."""
        return get_value_from_range('blocks', self.value)

    @property
    def block(self) -> str:
        """The Unicode block for the character."""
        return self.blk

    @property
    def canonical_combining_class(self) -> str:
        """The Canonical Ordering Algorithm class for the character."""
        return self.ccc

    @property
    def category(self) -> str:
        """The Unicode general category for the character."""
        alias = self.gc
        return expand_property_value('gc', alias)

    @property
    def ccc(self) -> str:
        """The Canonical Ordering Algorithm class for the character."""
        data = get_unicode_data()
        datum = data[self.code_point]
        return datum.canonical_combining_class

    @property
    def code_point(self) -> str:
        """The address for the character in the Unicode database."""
        x = ord(self.value)
        return f'U+{x:04x}'.upper()

    @property
    def decomposition_type(self) -> str:
        return self.dt

    @property
    def decimal(self) -> int | None:
        """The decimal value of the character."""
        return ucd.decimal(self.value, None)

    @property
    def decomposition(self) -> str:
        """The Unicode defined decompositions of the character."""
        return self.dm

    @property
    def digit(self) -> int | None:
        """The numerical value of the character as a digit."""
        return ucd.digit(self.value, None)

    @property
    def dm(self) -> str:
        """The Unicode defined decompositions of the character."""
        return ucd.decomposition(self.value)

    @property
    def dt(self) -> str:
        decomp = ucd.decomposition(self.value)
        if not decomp:
            return decomp
        elif not decomp.startswith('<'):
            return 'canonical'
        else:
            decomp_type, _ = decomp.split('>')
            return decomp_type[1:]

    @property
    def gc(self) -> str:
        """The Unicode general category for the character."""
        return ucd.category(self.value)

    @property
    def hst(self) -> str:
        """The Hangul syllable type for the character."""
        hst = get_hangul_syllable_type()
        return hst[self.value]

    @property
    def isc(self) -> str:
        """ISO 10646 comment field. It was used for notes that appeared
        in parentheses in the 10646 names list, or contained an asterisk
        to mark an Annex P note.

        As of Unicode 5.2.0, this field no longer contains any non-null
        values.
        """
        data = get_unicode_data()
        datum = data[self.code_point]
        if datum.iso_comment:
            return datum.iso_comment
        return ''

    @property
    def iso_comment(self) -> str:
        """ISO 10646 comment field. It was used for notes that appeared
        in parentheses in the 10646 names list, or contained an asterisk
        to mark an Annex P note.

        As of Unicode 5.2.0, this field no longer contains any non-null
        values.
        """
        return self.isc

    @property
    def na(self) -> str:
        """The Unicode name for the character."""
        try:
            name = ucd.name(self.value)

        # Control characters don't have assigned names in Unicode
        # 14.0.0. So, we have to look up the Unicode 1 names for
        # them, which are in the 14.0.0 UnicodeData.txt file.
        except ValueError:
            cat = ucd.category(self.value)

            # Control characters.
            if cat == 'Cc':
                name = f'<{self.na1}>'

            # Private use characters.
            elif cat == 'Co':
                name = 'PRIVATE USE CHARACTER'

            # Fall back if there are more code points without names.
            else:
                name = '?? UNKNOWN ??'

        return name

    @property
    def na1(self) -> str:
        """Old name as published in Unicode 1.0 or ISO 6429 names for
        control functions. This field is empty unless it is significantly
        different from the current name for the character.
        """
        data = get_unicode_data()
        datum = data[self.code_point]
        if datum.unicode_1_name:
            return datum.unicode_1_name
        return ''

    @property
    def name(self) -> str:
        """The Unicode name for the character."""
        return self.na

    @property
    def numeric(self) -> float | int | None:
        """The Unicode defined numeric value for the character."""
        return self.nv

    @property
    def nv(self) -> float | int | None:
        """The Unicode defined numeric value for the character."""
        return ucd.numeric(self.value, None)

    @property
    def sc(self) -> str:
        """The Unicode script for the character."""
        return get_value_from_range('scripts', self.value)

    @property
    def scx(self) -> str:
        """The Unicode script extensions for the character."""
        value = get_script_extensions()[self.value]
        if value == '<script>':
            return self.script
        return value

    @property
    def script(self) -> str:
        """The Unicode script for the character."""
        return self.sc

    @property
    def script_extensions(self) -> str:
        """The Unicode script extensions for the character."""
        return self.scx

    @property
    def simple_uppercase_mapping(self) -> str:
        """Simple uppercase mapping (single character result). If a
        character is part of an alphabet with case distinctions, and
        has a simple uppercase equivalent, then the uppercase equivalent
        is in this field. The simple mappings have a single character
        result, where the full mappings may have multi-character results.
        For more information, see Case and Case Mapping.
        """
        return self.suc

    @property
    def simple_lowercase_mapping(self) -> str:
        """Simple lowercase mapping (single character result)."""
        return self.slc

    @property
    def simple_titlecase_mapping(self) -> str:
        """Simple titlecase mapping (single character result).

        Note: If this field is null, then the Simple_Titlecase_Mapping
        is the same as the Simple_Uppercase_Mapping for this character.
        """
        return self.stc

    @property
    def slc(self) -> str:
        """Simple lowercase mapping (single character result)."""
        data = get_unicode_data()
        datum = data[self.code_point]
        if datum.simple_lowercase_mapping:
            return datum.simple_lowercase_mapping
        return ''

    @property
    def stc(self) -> str:
        """Simple titlecase mapping (single character result).

        Note: If this field is null, then the Simple_Titlecase_Mapping
        is the same as the Simple_Uppercase_Mapping for this character.
        """
        data = get_unicode_data()
        datum = data[self.code_point]
        if datum.simple_titlecase_mapping:
            return datum.simple_titlecase_mapping
        return ''

    @property
    def suc(self) -> str:
        """Simple uppercase mapping (single character result). If a
        character is part of an alphabet with case distinctions, and
        has a simple uppercase equivalent, then the uppercase equivalent
        is in this field. The simple mappings have a single character
        result, where the full mappings may have multi-character results.
        For more information, see Case and Case Mapping.
        """
        data = get_unicode_data()
        datum = data[self.code_point]
        if datum.simple_uppercase_mapping:
            return datum.simple_uppercase_mapping
        return ''

    @property
    def unicode_1_name(self) -> str:
        """Old name as published in Unicode 1.0 or ISO 6429 names for
        control functions. This field is empty unless it is significantly
        different from the current name for the character.
        """
        return self.na1

    @property
    def value(self) -> str:
        """The code point as a string."""
        return self.__value

    @property
    def wspace(self) -> bool:
        """Spaces, separator characters and other control characters
        which should be treated by programming languages as "white space"
        for the purpose of parsing elements. See also Line_Break,
        Grapheme_Cluster_Break, Sentence_Break, and Word_Break, which
        classify space characters and related controls somewhat
        differently for particular text segmentation contexts.
        """
        proplist = get_proplist()
        return proplist['White_Space'][self.value]

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


class MissingValue:
    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self) -> str:
        return self.value


# Utility functions.
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
    try:
        result = prop_cache[prop]

    except KeyError:
        lines = util.read_resource('props')
        by_proptype = parse_properties(lines)
        result = by_proptype[prop]

    return result


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
    # Look it up in the cache, to avoid having to reload the file
    # multiple times.
    try:
        by_alias = propvals_cache[prop]

    # If it's not in the cache, then we have to load the data from
    # file.
    except KeyError:
        lines = util.read_resource('propvals')
        by_alias = parse_property_values(lines, prop)
        propvals_cache[prop] = by_alias

    # Return the expanded alias.
    return by_alias[alias]


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


def get_hangul_syllable_type() -> defaultdict[str, str]:
    global hst_cache
    if hst_cache is None:
        hst_cache = parse_single_property('hst', 'hst')
    return hst_cache


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
    if not prop_cache:
        lines = util.read_resource('props')
        parse_properties(lines)

    return tuple(key for key in prop_cache)


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
    if prop not in propvals_cache:
        lines = util.read_resource('propvals')
        by_alias = parse_property_values(lines, prop)
        propvals_cache[prop] = {}
        for alias in by_alias:
            propvals_cache[prop][alias] = by_alias[alias]

    return tuple(key for key in propvals_cache[prop])


def get_proplist() -> dict[str, defaultdict[str, bool]]:
    if not proplist_cache:
        proplist = parse_binary_properties('proplist')
        for key in proplist:
            proplist_cache[key] = proplist[key]
    return proplist_cache


def get_script_extensions() -> defaultdict[str, str]:
    """Get the script extensions data."""
    global script_extensions_cache
    if script_extensions_cache is None:
        script_extensions_cache = parse_script_extensions()
    return script_extensions_cache


def get_unicode_data() -> dict[str, UnicodeDatum]:
    """Get the core Unicode data."""
    if not unicodedata_cache:
        lines = util.read_resource('unicodedata')
        data = parse_unicode_data(lines)
    return unicodedata_cache


def get_value_from_range(src: str, char: str) -> str:
    """Given a data source and a character, return the value from
    the data source of that character.
    """
    if src not in range_cache:
        range_cache[src] = get_value_ranges(src)
    vranges = range_cache[src]
    address = ord(char)
    max_ = len(vranges)
    index = max_ // 2
    vr = bintree(vranges, address, index, 0, max_)
    return vr.value


def get_value_ranges(src: str) -> tuple[ValueRange, ...]:
    """Get the tuple of derived ages. The derived age of a character
    is the Unicode version where the character was assigned to a code
    point.

    :param src: The source key for the values.
    :return: The possible ages as a :class:`tuple`.
    :rtype: tuple
    """
    results = (ValueRange(*vr) for vr in parse_range_for_value(src))
    return tuple(results)


# Data parsing functions.
def parse_binary_properties(source: str) -> dict[str, defaultdict[str, bool]]:
    lines = util.read_resource(source)
    missing = MissingBool(False)

    lines = strip_comments(lines)
    data = parse_sdt(lines)
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


def parse_missing(lines: Sequence[str]) -> tuple[tuple[str, ...], ...]:
    """Parse the default values from a unicode data file.

    :param lines: The lines from a unicode data file. The lines must
        still contain the comments.
    :return: The default values as a :class:`tuple`.
    :rtype: tuple
    """
    prefix = '# @missing: '
    lines = [line[12:] for line in lines if line.startswith(prefix)]
    lines = strip_comments(lines)
    return parse_sdt(lines)


def parse_properties(lines: Sequence[str]) -> dict[str, str]:
    """Parse the contents of the properties file and return the
    translation map for the properties.
    """
    lines = [
        line for line in lines
        if line.strip() and not line.startswith('#')
    ]
    for line in lines:
        fields = line.split(';')
        key = fields[0].strip()
        try:
            value = fields[1].strip()
        except IndexError as ex:
            print(line)
            raise ex
        value = value.replace('_', ' ')
        prop_cache[key] = value
    return prop_cache


def parse_property_values(
    lines: Sequence[str],
    proptype: str
) -> dict[str, str]:
    """Parse the contents of the property values file and return the
    translation map for the given property type.

    :param lines: The contents of the property values file.
    :param proptype: The type of properties to extract from the file.
    :return: The entries for the given property type as a :class:`dict`.
    :rtype: dict
    """
    lines = [line for line in lines if line.startswith(proptype)]
    by_alias = {}
    for line in lines:
        line = line.split('#', 1)[0]
        fields = line.split(';')
        key = fields[1].strip()
        value = fields[2].strip()
        value = value.replace('_', ' ')
        by_alias[key] = value
    return by_alias


def parse_range_for_value(source: str) -> tuple[tuple[int, int, str], ...]:
    # Read the source file.
    lines = util.read_resource(source)

    # Get the default value for unassigned characters.
    missing_data = parse_missing(lines)
    missing = missing_data[0][-1]

    # Parse the data from the file.
    lines = strip_comments(lines)
    data = parse_sdt(lines)
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


def parse_single_property(source: str, prop: str) -> defaultdict[str, str]:
    # Read the file.
    lines = util.read_resource(source)

    # Get the default value
    missing_data = parse_missing(lines)
    missing_str = missing_data[0][-1]
    propvals = get_property_values(prop)
    if missing_str not in propvals:
        missing_str = missing_str.replace('_', ' ')
        valprops = {expand_property_value(prop, k): k for k in propvals}
        missing_str = valprops[missing_str]
    missing = MissingValue(missing_str)

    # Parse the data.
    lines = strip_comments(lines)
    data = parse_sdt(lines)
    result = defaultdict(missing)
    for datum in data:
        points, value = datum
        parts = points.split('..')
        start = int(parts[0], 16)
        stop = start + 1
        if len(parts) > 1:
            stop = int(parts[1], 16) + 1
        for i in range(start, stop):
            result[chr(i)] = value
    return result


def parse_script_extensions() -> defaultdict[str, str]:
    lines = util.read_resource('scriptext')

    missing_data = parse_missing(lines)
    missing = missing_data[0][-1]
    missingval = MissingValue(missing)

    lines = strip_comments(lines)
    data = parse_sdt(lines)
    values: defaultdict[str, str] = defaultdict(missingval)
    for datum in data:
        points, value = datum
        parts = points.split('..')
        start = int(parts[0], 16)
        stop = start + 1
        if len(parts) > 1:
            stop = int(parts[1], 16) + 1
        for i in range(start, stop):
            values[chr(i)] = value
    return values


def parse_sdt(lines: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
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


def strip_comments(lines: Sequence[str]) -> tuple[str, ...]:
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
