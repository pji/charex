"""
charex
~~~~~~

Tools for exploring unicode characters and other character sets.
"""


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
