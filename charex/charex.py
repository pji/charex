"""
charex
~~~~~~

Tools for exploring unicode characters and other character sets.
"""


class Transformer:
    def __init__(self, charset: str = 'utf_8') -> None:
        self.charset = charset

    def bin_to_char(self, bin: str) -> str:
        """Given a binary number as a string, return the code point
        for that string.
        """
        n = int(bin, base=2)
        return chr(n)
