"""
charex
~~~~~~

Tools for exploring unicode characters and other character sets.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from json import load
from importlib.resources import files
import unicodedata as ucd

from charex.escape import schemes

# Constants.
RESOURCES = {
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


# Data classes.
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
propvals_cache: dict[str, dict[str, str]] = {}
unicodedata_cache: dict[str, UnicodeDatum] = {}


# Utility functions.
def expand_property_value(alias: str, proptype: str) -> str:
    """Translate the short name of a Unicode property value into the
    long name for that property.

    :param alias: The short name to translate.
    :param proptype: The type of property.
    :return: The long name of the property as a :class:`str`.
    :rtype: str
    """
    # Look it up in the cache, to avoid having to reload the file
    # multiple times.
    try:
        by_alias = propvals_cache[proptype]

    # If it's not in the cache, then we have to load the data from
    # file.
    except KeyError:
        lines = read_resource('propvals')
        by_alias = parse_property_values(lines, proptype)
        propvals_cache[proptype] = by_alias

    # Return the expanded alias.
    return by_alias[alias]


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


# Classes.
class Character:
    """One or more code points representing a character.

    :param value: The character to gather data for.
    :return: None.
    :rtype: NoneType
    """
    def __init__(self, value: str) -> None:
        self.__value = value
        self._rev_normal_cache: dict[str, tuple[str, ...]] = {}

    def __repr__(self) -> str:
        return f'{self.code_point} ({self.name})'

    @property
    def category(self) -> str:
        """The Unicode general category for the character."""
        alias = ucd.category(self.value)
        return expand_property_value(alias, 'gc')

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
            if not unicodedata_cache:
                lines = read_resource('unicodedata')
                data = parse_unicode_data(lines)
            else:
                data = unicodedata_cache
            point = self.code_point
            name = f'<{data[point].unicode_1_name}>'
        return name

    @property
    def numeric(self) -> float | int | None:
        """The Unicode defined numeric value for the character."""
        return ucd.numeric(self.value, None)

    @property
    def value(self) -> str:
        """The code point as a string."""
        return self.__value

    def escape(self, scheme: str, codec: str = 'utf8') -> str:
        """The escaped version of the character.

        :param scheme: The escape scheme to use.
        :param codec: The codec to use when escaping to a hexadecimal
            string.
        :return: A :class:`str` with the escaped character.
        :rtype: str
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
        """
        b = self.value.encode(codec)
        hexes = [f'{x:02x}'.upper() for x in b]
        return ''.join(x for x in hexes)

    def is_normal(self, form: str) -> bool:
        """Is the character normalized to the given form?

        :param form: The normalization form to check against.
        :return: A :class:`bool` indicating whether the character is
            normalized.
        :rtype: bool
        """
        return ucd.is_normalized(form, self.value)

    def normalize(self, form: str) -> str:
        """Normalize the character using the given form.

        :param form: The normalization form to check against.
        :return: The normalization result as a :class:`str`.
        :rtype: str
        """
        return ucd.normalize(form, self.value)

    def reverse_normalize(self, form: str) -> tuple[str, ...]:
        """Return the characters that normalize to the character using
        the given form.

        :param form: The normalization form to check against.
        :return: The denormalization results in a :class:`tuple`.
        :rtype: tuple
        """
        source = f'rev_{form}'
        if source not in self._rev_normal_cache:
            lkp = Lookup(source)
            self._rev_normal_cache[source] = lkp.query(self.value)
        return self._rev_normal_cache[source]


class Lookup:
    """A data lookup.

    :param source: The key for the data source in the RESOURCES
        dictionary.
    """
    def __init__(self, source: str) -> None:
        self.__source = source
        pkg = files('charex.data')
        data_file = pkg / RESOURCES[source]
        fh = data_file.open()
        data = load(fh)
        self.__data = {k: tuple(data[k]) for k in data}
        fh.close()

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


class Transformer:
    def __init__(
        self,
        charset: str = 'utf_8',
        endian: str = 'big'
    ) -> None:
        self.charset = charset
        self.endian = endian

    def from_bin(self, s: str) -> str:
        """Given a binary number as a string, return the code point
        for that string.
        """
        if self.endian == 'little':
            s = s[::-1]
        x = int(s, base=2)
        return self.from_int(x)

    def from_hex(self, s: str) -> str:
        """Given a hexadecimal number as a string, return the code
        point for that string.
        """
        if self.endian == 'little':
            new = ''
            while s:
                new = new + s[-2:]
                s = s[:-2]
            s = new
        x = int(s, 16)
        return self.from_int(x)

    def from_int(self, x: int) -> str:
        """Given an integer, return the code point for that integer."""
        b = x.to_bytes((x.bit_length() + 7) // 8)
        return b.decode(self.charset, errors='replace')
