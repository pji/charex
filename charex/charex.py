"""
charex
~~~~~~

Tools for exploring unicode characters and other character sets.
"""
from json import load
from importlib.resources import files
import unicodedata as ucd


# Data.
DATA = {
    'rev_nfc': 'rev_nfc.json',
    'rev_nfkc': 'rev_nfkc.json',
    'rev_nfd': 'rev_nfd.json',
    'rev_nfkd': 'rev_nfkd.json',
}


# Classes.
class Character:
    """One or more code points representing a character."""
    def __init__(self, value: str) -> None:
        self.__value = value
        self._rev_normal_cache = {}

    @property
    def category(self) -> str:
        return ucd.category(self.value)

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
        return ucd.name(self.value)

    @property
    def numeric(self) -> int | None:
        return ucd.numeric(self.value, None)

    @property
    def value(self) -> str:
        return self.__value

    def is_normal(self, form: str) -> bool:
        return ucd.is_normalized(form, self.value)

    def normalize(self, form: str) -> str:
        return ucd.normalize(form, self.value)

    def reverse_normalize(self, form: str) -> str:
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
        data_file = pkg / DATA[source]
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
        return self.data[key]


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
