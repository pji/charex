"""
charex
~~~~~~

Tools for exploring unicode characters and other character sets.
"""
from collections.abc import Generator, Sequence
import re
import unicodedata as ucd

from charex import db
from charex import util
from charex.escape import schemes


# Classes.
class Character:
    """A Unicode character.

    :param value: A character address string for the Unicode
        character. See below.
    :return: The character as a :class:`charex.Character`.
    :rtype: charex.Character

    Address Formats
    ---------------
    The understood str-based formats for manual input of addresses are:

    *   Character: A string with length equal to one.
    *   Code Point: The prefix "U+" followed by a hexadecimal number.
    *   Binary String: The prefix "0b" followed by a binary number.
    *   Hex String: The prefix "0x" followed by a hexadecimal number.

    The following formats are available for use through the API:

    *   Bytes: A :class:`bytes`.
    *   Integer: An :class:`int`.

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

    Beyond the declared properties and methods described below, most
    Unicode properties for the character are available by calling
    their alias as a property of :class:`charex.Character`::

        >>> value = 'a'
        >>> char = Character(value)
        >>> char.na
        'LATIN SMALL LETTER A'
        >>> char.blk
        'Basic Latin'
        >>> char.sc
        'Latn'
        >>> char.suc
        '0041'

    """
    cache = db.cache

    def __init__(self, value: bytes | int | str) -> None:
        value = util.to_char(value)
        self.__value = value
        self._rev_normal_cache: dict[str, tuple[str, ...]] = {}

    def __getattr__(self, name):
        name = name.casefold()
        code = self.code_point[2:].casefold()
        return db.get_value_for_code(name, code)

    def __repr__(self) -> str:
        name = self.na
        if name == '<control>':
            name = f'<{self.na1}>'
        return f'{self.code_point} ({name})'

    # Derived properties.
    @property
    def bpb(self) -> str:
        """For an opening bracket, the code point of the matching
        closing bracket. For a closing bracket, the code point of
        the matching opening bracket. This property is used in the
        implementation of parenthesis matching. See Unicode Standard
        Annex #9, "Unicode Bidirectional Algorithm" [UAX9].
        """
        bpb = '<none>'
        if self.bpt != 'n':
            bpb = self.bmg
        return bpb

    @property
    def bpt(self) -> str:
        """Type of a paired bracket, either opening or closing. This
        property is used in the implementation of parenthesis matching.
        See Unicode Standard Annex #9, "Unicode Bidirectional Algorithm"
        [UAX9].
        """
        bpt = 'n'
        if self.bc == 'ON' and self.bidi_m == 'Y':
            if self.gc == 'Ps':
                bpt = 'o'
            elif self.gc == 'Pe':
                bpt = 'c'
        return bpt

    @property
    def name_alias(self) -> str:
        return ' '.join(f'{a}' for a in self.cache.namealias[self.value])

    @property
    def code_point(self) -> str:
        """The address for the character in the Unicode database."""
        x = ord(self.value)
        return f'U+{x:04x}'.upper()

    @property
    def value(self) -> str:
        """The Unicode character as a string."""
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
        prop = f'rev_{form}'
        code = self.code_point[2:].casefold()
        return db.get_denormal_map_for_code(prop, code)

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
            '&nvlt;'

        """
        try:
            scheme = scheme.casefold()
            fn = schemes[scheme]
            return fn(self.value, codec)

        # UTF-16 surrogates will error when anything tries to
        # encode them as UTF-8.
        except UnicodeEncodeError:
            return ''

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
        try:
            b = self.value.encode(codec)
            hexes = [f'{x:02x}'.upper() for x in b]
            return ' '.join(x for x in hexes)

        # UTF-16 surrogates will error when anything tries to
        # encode them as UTF-8.
        except UnicodeEncodeError:
            return ''

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


# Utility functions.
def alias_property(longname: str, space: bool = True) -> str:
    if space:
        longname = longname.replace(' ', '_')
    return Character.cache.props[longname.casefold()].alias


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
    long = Character.cache.property_name[prop.casefold()].name
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
    long = Character.cache.value_name[prop][alias].name
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
    chars: Sequence[Character] | None = None,
    insensitive: bool = False,
    regex: bool = False
) -> Generator[Character, None, None]:
    """Return all the characters with the given property value.

    :param prop: The property to filter on.
    :param value: The pattern to filter on.
    :param chars: (Optional.) The characters to filter. Defaults
        to filtering all Unicode characters.
    :param insensitive: (Optional.) Whether the matching should
        be case insensitive. Defaults to false.
    :param regex: (Optional.) Whether the value should be used as a
        regular expression for the matching. Defaults to false.
    :return: the filtered characters as a
        :class:`collections.abc.Generator`.
    :rtype: collections.abc.Generator

    Usage
    -----
    To get a generator that produces the Emoji modifiers::

        >>> prop = 'emod'
        >>> value = 'Y'
        >>> gen = filter_by_property(prop, value)
        >>> for char in gen:
        ...     print(char.summarize())
        ...
        🏻 U+1F3FB (EMOJI MODIFIER FITZPATRICK TYPE-1-2)
        🏼 U+1F3FC (EMOJI MODIFIER FITZPATRICK TYPE-3)
        🏽 U+1F3FD (EMOJI MODIFIER FITZPATRICK TYPE-4)
        🏾 U+1F3FE (EMOJI MODIFIER FITZPATRICK TYPE-5)
        🏿 U+1F3FF (EMOJI MODIFIER FITZPATRICK TYPE-6)

    You can limit the number of characters being searched with the
    `chars` parameter::

        >>> prop = 'gc'
        >>> value = 'Cc'
        >>> chars = [Character(chr(n)) for n in range(128)]
        >>> gen = filter_by_property(prop, value, chars)
        >>> for char in gen:
        ...     print(char.summarize())
        ...
        ␀ U+0000 (<NULL>)
        ␁ U+0001 (<START OF HEADING>)
        ␂ U+0002 (<START OF TEXT>)
        ␃ U+0003 (<END OF TEXT>)
        ␄ U+0004 (<END OF TRANSMISSION>)
        ␅ U+0005 (<ENQUIRY>)
        ␆ U+0006 (<ACKNOWLEDGE>)
        ␇ U+0007 (<BELL>)
        ␈ U+0008 (<BACKSPACE>)
        ␉ U+0009 (<CHARACTER TABULATION>)
        ␊ U+000A (<LINE FEED (LF)>)
        ␋ U+000B (<LINE TABULATION>)
        ␌ U+000C (<FORM FEED (FF)>)
        ␍ U+000D (<CARRIAGE RETURN (CR)>)
        ␎ U+000E (<SHIFT OUT>)
        ␏ U+000F (<SHIFT IN>)
        ␐ U+0010 (<DATA LINK ESCAPE>)
        ␑ U+0011 (<DEVICE CONTROL ONE>)
        ␒ U+0012 (<DEVICE CONTROL TWO>)
        ␓ U+0013 (<DEVICE CONTROL THREE>)
        ␔ U+0014 (<DEVICE CONTROL FOUR>)
        ␕ U+0015 (<NEGATIVE ACKNOWLEDGE>)
        ␖ U+0016 (<SYNCHRONOUS IDLE>)
        ␗ U+0017 (<END OF TRANSMISSION BLOCK>)
        ␘ U+0018 (<CANCEL>)
        ␙ U+0019 (<END OF MEDIUM>)
        ␚ U+001A (<SUBSTITUTE>)
        ␛ U+001B (<ESCAPE>)
        ␜ U+001C (<INFORMATION SEPARATOR FOUR>)
        ␝ U+001D (<INFORMATION SEPARATOR THREE>)
        ␞ U+001E (<INFORMATION SEPARATOR TWO>)
        ␟ U+001F (<INFORMATION SEPARATOR ONE>)
        ⑿ U+007F (<DELETE>)

    You can set the `insensitive` parameter to do case insensitive
    matching::

        >>> prop = 'emod'
        >>> value = 'y'
        >>> insensitive = True
        >>> gen = filter_by_property(prop, value, insensitive=insensitive)
        >>> for char in gen:
        ...     print(char.summarize())
        ...
        🏻 U+1F3FB (EMOJI MODIFIER FITZPATRICK TYPE-1-2)
        🏼 U+1F3FC (EMOJI MODIFIER FITZPATRICK TYPE-3)
        🏽 U+1F3FD (EMOJI MODIFIER FITZPATRICK TYPE-4)
        🏾 U+1F3FE (EMOJI MODIFIER FITZPATRICK TYPE-5)
        🏿 U+1F3FF (EMOJI MODIFIER FITZPATRICK TYPE-6)

    If you set the `regex` parameter, you can search using regular
    expressions::

        >>> prop = 'na'
        >>> value = '.*EYE$'
        >>> regex = True
        >>> gen = filter_by_property(prop, value, regex=regex)
        >>> for char in gen:
        ...     print(char.summarize())
        ...
        ◉ U+25C9 (FISHEYE)
        ◎ U+25CE (BULLSEYE)
        ⺫ U+2EAB (CJK RADICAL EYE)
        ⽬ U+2F6C (KANGXI RADICAL EYE)
        👁 U+1F441 (EYE)
        😜 U+1F61C (FACE WITH STUCK-OUT TONGUE AND WINKING EYE)
        🤪 U+1F92A (GRINNING FACE WITH ONE LARGE AND ONE SMALL EYE)
        🫣 U+1FAE3 (FACE WITH PEEKING EYE)

    .. _warning:
        If you don't limit the characters you are doing the filter on,
        this will be a single-threaded regular expression comparison
        on 1,114,111 characters. In other words, it's not the speediest
        thing in the world.
    """
    # Default to searching the full set of Unicode code points.
    if not chars:
        chars = [Character(n) for n in range(util.LEN_UNICODE)]

    # Regular expression matching.
    if regex:
        flags = 0
        if insensitive:
            flags = re.IGNORECASE
        pattern = re.compile(value, flags=flags)
        for char in chars:
            try:
                if pattern.match(getattr(char, prop)):
                    yield char
            except KeyError:
                continue

    # Case-insensitive string matching.
    elif insensitive:
        value = value.casefold()
        for char in chars:
            try:
                if getattr(char, prop).casefold() == value:
                    yield char
            except KeyError:
                continue

    # String matching.
    else:
        for char in chars:
            try:
                if getattr(char, prop) == value:
                    yield char
            except KeyError:
                continue


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
        ('age', 'ahex',... 'xo_nfkd')

    """
    props = Character.cache.property_alias
    result = []
    for key in props:
        if props[key] not in result:
            result.append(props[key])
    aliases = tuple(prop.alias for prop in result)
    saliases = sorted(alias.casefold() for alias in aliases)
    return tuple(saliases)


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
    propvals = Character.cache.value_aliases[prop]
    result = []
    for key in propvals:
        if propvals[key] not in result:
            result.append(propvals[key])
    return tuple(val.alias for val in result)


if __name__ == '__main__':
    pass
