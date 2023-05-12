"""
escape
~~~~~~

Character escape schemes.
"""
from collections.abc import Callable
from json import loads

from charex import util


# Registry.
schemes: dict[str, Callable[[str, str], str]] = {}


# Registration.
class reg_escape:
    """A decorator for registering escape schemes.

    :param key: The name the escape sequence is registered under.
    """
    def __init__(self, key: str) -> None:
        self.key = key

    def __call__(
        self,
        fn: Callable[[str, str], str]
    ) -> Callable[[str, str], str]:
        schemes[self.key] = fn
        return fn


# Caches.
cached_entities: dict[str, str] = {}


# Load data.
def get_named_entity(char: str) -> str:
    """Get a named entity from the HTML entity data."""
    lines = util.read_resource('entities')
    json = ''.join(lines)
    data = loads(json)
    by_char = {data[key]['characters']: key for key in data}
    try:
        cached_entities[char] = by_char[char]
    except KeyError:
        cached_entities[char] = escape_html(char, '')
    return cached_entities[char]


# Escape schemes.
@reg_escape('cu')
def escape_cu(char: str, codec: str) -> str:
    """Escape scheme for C/C++ Unicode escape sequences.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        x = ord(char)
        return f'\\u{x:04x}'
    except TypeError as ex:
        b = char.encode('unicode_escape')
        s = b.decode('ascii')
        return f'\\U{s[2:]:>08}'

@reg_escape('culong')
def escape_culong(char: str, codec: str) -> str:
    """Escape scheme for four byte C/C++ Unicode escape sequences.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        x = ord(char)
        return f'\\U{x:08x}'
    except TypeError as ex:
        b = char.encode('unicode_escape')
        s = b.decode('ascii')
        x = s[2:]
        return f'\\U{s[2:]:>08}'


@reg_escape('html')
def escape_html(char: str, codec: str) -> str:
    """Escape scheme for HTML decimal numeric character references.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    n = ord(char)
    return f'&#{n};'


@reg_escape('htmlhex')
def escape_htmlhex(char: str, codec: str) -> str:
    """Escape scheme for HTML hexadecimal numeric character references.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    n = ord(char)
    h = hex(n)
    return f'&#x{h[2:]};'


@reg_escape('htmlnamed')
def escape_htmlnamed(char: str, codec: str) -> str:
    """Escape scheme for HTML named character references. It will return
    the decimal numeric character references if no named entity exists.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        return cached_entities[char]
    except KeyError:
        return get_named_entity(char)


@reg_escape('url')
def escape_url(char: str, codec: str) -> str:
    """Escape scheme for URL percent encoding.

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    b = char.encode(codec)
    octets = [f'%{x:02x}'.upper() for x in b]
    return ''.join(x for x in octets)


# Bulk escape.
def escape(s: str, schemekey: str, codec: str = 'utf8') -> str:
    """Escape the string wit the scheme.

    :param s: The string to escape.
    :param scheme: The key in the `schemes` :class:`dict` to use for
        the escaping.
    :param codec: The character set codec to use when escaping the
        characters.
    :return: The escaped :class:`str`.
    :rtype: str
    """
    scheme = schemes[schemekey]
    return ''.join(scheme(char, codec) for char in s)


def get_schemes() -> tuple[str, ...]:
    """Return the names of the registered escape schemes."""
    return tuple(scheme for scheme in schemes)
