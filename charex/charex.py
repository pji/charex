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
    'rev_nfc': 'rev_nfc.json',
    'rev_nfkc': 'rev_nfkc.json',
    'rev_nfd': 'rev_nfd.json',
    'rev_nfkd': 'rev_nfkd.json',
    'propvals': 'PropertyValueAliases.txt',
    'unicodedata': 'UnicodeData.txt',
}


# Caches.
propvals_cache: dict[str, dict[str, str]] = {}


# Data classes.
@dataclass
class UnicodeDatum:
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


# Utility functions.
def expand_property_value(alias: str, proptype: str) -> str:
    """Translate the short name of a Unicode property value into the
    long name for that property.
    """
    try:
        by_alias = propvals_cache[proptype]

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
    result = {}
    for line in lines:
        fields = line.split(';')
        datum = UnicodeDatum(*fields)
        result['U+' + datum.code_point] = datum
    return result


def read_resource(key: str) -> tuple[str, ...]:
    """Read the data from a resource file within the package."""
    pkg = files('charex.data')
    data_file = pkg / RESOURCES[key]
    fh = data_file.open()
    lines = fh.readlines()
    fh.close()
    return tuple(lines)


# Classes.
class Character:
    """One or more code points representing a character."""
    def __init__(self, value: str) -> None:
        self.__value = value
        self._rev_normal_cache: dict[str, tuple[str, ...]] = {}

    def __repr__(self) -> str:
        return f'{self.code_point} ({self.name})'

    @property
    def category(self) -> str:
        alias = ucd.category(self.value)
        return expand_property_value(alias, 'gc')

    @property
    def code_point(self) -> str:
        x = ord(self.value)
        return f'U+{x:04x}'.upper()

    @property
    def decimal(self) -> int | None:
        return ucd.decimal(self.value, None)

    @property
    def decomposition(self) -> str:
        return ucd.decomposition(self.value)

    @property
    def digit(self) -> int | None:
        return ucd.digit(self.value, None)

    @property
    def name(self) -> str:
        try:
            name = ucd.name(self.value)
        except ValueError:
            lines = read_resource('unicodedata')
            data = parse_unicode_data(lines)
            point = self.code_point
            name = f'<{data[point].unicode_1_name}>'
        return name

    @property
    def numeric(self) -> float | int | None:
        return ucd.numeric(self.value, None)

    @property
    def value(self) -> str:
        return self.__value

    def escape(self, scheme: str, codec: str = 'utf8') -> str:
        scheme = scheme.casefold()
        fn = schemes[scheme]
        return fn(self.value, codec)

    def encode(self, codec: str) -> str:
        b = self.value.encode(codec)
        hexes = [f'{x:02x}'.upper() for x in b]
        return ''.join(x for x in hexes)

    def is_normal(self, form: str) -> bool:
        return ucd.is_normalized(form, self.value)

    def normalize(self, form: str) -> str:
        return ucd.normalize(form, self.value)

    def reverse_normalize(self, form: str) -> tuple[str, ...]:
        source = f'rev_{form}'
        if source not in self._rev_normal_cache:
            lkp = Lookup(source)
            self._rev_normal_cache[source] = lkp.query(self.value)
        return self._rev_normal_cache[source]


class Lookup:
    """A data lookup."""
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
        return self.__data

    @property
    def source(self) -> str:
        return self.__source

    def query(self, key: str) -> tuple[str, ...]:
        """Return the value for the given string from the loaded data."""
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
