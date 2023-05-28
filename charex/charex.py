"""
charex
~~~~~~

Tools for exploring unicode characters and other character sets.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from json import loads
import unicodedata as ucd

from charex import util
from charex.escape import schemes


# Data classes.
@dataclass(order=True)
class DerivedAge:
    """A record from the DerivedAge.txt file for Unicode 14.0.0.

    :param start: The first code point in the range.
    :param stop: The last code point in the range.
    :param version: The version the range was introduced.
    """
    start: int
    stop: int
    version: str


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
age_cache: tuple[DerivedAge, ...] = tuple()
prop_cache: dict[str, str] = {}
propvals_cache: dict[str, dict[str, str]] = {}
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

    def __repr__(self) -> str:
        return f'{self.code_point} ({self.name})'

    @property
    def age(self) -> str:
        """The version the character was added in."""
        ages = get_derived_age()
        address = ord(self.__value)
        max_ = len(ages)
        index = max_ // 2
        age = bintree(ages, address, index, 0, max_)
        return age.version

    @property
    def category(self) -> str:
        """The Unicode general category for the character."""
        alias = ucd.category(self.value)
        return expand_property_value('gc', alias)

    @property
    def code_point(self) -> str:
        """The address for the character in the Unicode database."""
        x = ord(self.value)
        return f'U+{x:04x}'.upper()

    @property
    def decimal(self) -> int | None:
        """The decimal value of the character."""
        return ucd.decimal(self.value, None)

    @property
    def decomposition(self) -> str:
        """The Unicode defined decompositions of the character."""
        return ucd.decomposition(self.value)

    @property
    def digit(self) -> int | None:
        """The numerical value of the character as a digit."""
        return ucd.digit(self.value, None)

    @property
    def name(self) -> str:
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
                if not unicodedata_cache:
                    lines = util.read_resource('unicodedata')
                    data = parse_unicode_data(lines)
                else:
                    data = unicodedata_cache
                point = self.code_point
                name = f'<{data[point].unicode_1_name}>'

            # Private use characters.
            elif cat == 'Co':
                name = 'PRIVATE USE CHARACTER'

            # Fall back if there are more code points without names.
            else:
                name = '?? UNKNOWN ??'

        return name

    @property
    def numeric(self) -> float | int | None:
        """The Unicode defined numeric value for the character."""
        return ucd.numeric(self.value, None)

    @property
    def value(self) -> str:
        """The code point as a string."""
        return self.__value

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


# Utility functions.
def bintree(
    ages: Sequence[DerivedAge],
    address: int,
    index: int,
    min_: int,
    max_: int
) -> DerivedAge:
    """Find the derived age of a Unicode character using a binary
    tree search.

    :param ages: The possible ages for Unicode characters.
    :param address: The code point of the character an an :class:`int`.
    :param index: The current location of the search cursor.
    :param min_: The minimum possible index within ages that hasn't been
        excluded by the search.
    :param max_: The maximum possible index within ages that hasn't been
        excluded by the search.
    :return: The age of the character as a :class:`charex.charex.DerivedAge`.
    :rtype: charex.charex.DerivedAge
    """
    age = ages[index]
    if address < age.start:
        max_ = index
        index = min_ + (max_ - min_) // 2
        age = bintree(ages, address, index, min_, max_)
    elif address >= age.stop:
        min_ = index
        index = min_ + (max_ - min_) // 2
        age = bintree(ages, address, index, min_, max_)
    return age


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


def get_category_members(category: str) -> tuple[Character, ...]:
    """Get all characters that are members of the given category."""
    ulen = 0x10FFFF
    members = (
        Character(n) for n in range(ulen)
        if ucd.category(chr(n)) == category
    )
    return tuple(members)


def get_derived_age() -> tuple[DerivedAge, ...]:
    """Get the tuple of derived ages. The derived age of a character
    is the Unicode version where the character was assigned to a code
    point.

    :return: The possible ages as a :class:`tuple`.
    :rtype: tuple
    """
    # Since ages are stored as a tuple rather than a dict, we need
    # to pull the cache into this namespace in case we need to make
    # changes to it.
    global age_cache

    # Populate the cache.
    if not age_cache:
        # Read the source file.
        lines = util.read_resource('age')

        # Get the default value for unassigned characters.
        missing_data = parse_missing(lines)
        missing = missing_data[0][-1]

        # Parse the ages from the file.
        lines = strip_comments(lines)
        data = parse_sdt(lines)
        ages = []
        for datum in data:
            parts = datum[0].split('..')
            start = int(parts[0], 16)
            stop = start + 1
            if len(parts) > 1:
                stop = int(parts[1], 16) + 1
            age = DerivedAge(start, stop, datum[1])
            ages.append(age)

        # Sort the ages so they can be searched.
        ages = sorted(ages)

        # Fill in the gaps for the unassigned characters with the
        # default value.
        no_gaps = []
        index = 0
        while index + 1 < len(ages):
            age = ages[index]
            next = ages[index + 1]
            no_gaps.append(age)
            if age.stop != next.start:
                gap = DerivedAge(age.stop, next.start, missing)
                no_gaps.append(gap)
            index += 1
        if not no_gaps[-1].stop == util.LEN_UNICODE:
            age = DerivedAge(no_gaps[-1].stop, util.LEN_UNICODE, missing)
            no_gaps.append(age)
        age_cache = tuple(no_gaps)

    # Return the cached ages.
    return age_cache


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


# Data parsing functions.
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
        for line in lines:
            fields = line.split(';')
            datum = UnicodeDatum(*fields)
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


if __name__ == '__main__':
    for num in range(util.LEN_UNICODE):
        c = chr(num)
        char = Character(c)
        try:
            name = char.category
        except Exception as ex:
            print(char.code_point, type(ex))
