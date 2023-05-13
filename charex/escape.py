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


# Caches.
cached_entities: dict[str, str] = {}


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
@reg_escape('c')
def escape_c(char: str, codec: str) -> str:
    """Escape scheme for C/C++ escape sequences. This is derived from
    the Wikipedia list, since I don't have access to the C17
    specification.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    table = {
        '\u0007': r'\a',
        '\u0008': r'\b',
        '\u000c': r'\f',
        '\u000a': r'\n',
        '\u000d': r'\r',
        '\u0009': r'\t',
        '\u000b': r'\v',
        '\u001b': r'\e',    # Non-standard, supported by gcc, clang, tcc.
        '\u0027': r"\'",
        '\u0022': r'\"',
        '\u003f': r'\?',
        '\u005c': r'\\',
    }
    if char in table:
        return table[char]
    return char


@reg_escape('co')
def escape_co(char: str, codec: str) -> str:
    """Escape scheme for C/C++ octal escape sequences. This is derived
    from the Wikipedia list, since I don't have access to the C17
    specification.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    n = ord(char)
    if n > 0o777:
        return escape_cu(char, codec)
    return f'\\{n:o}'


@reg_escape('cu')
def escape_cu(char: str, codec: str) -> str:
    """Escape scheme for C/C++ Unicode escape sequences.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    x = ord(char)
    if x > 0xFFFF:
        return escape_culong(char, codec)
    return f'\\u{x:04x}'


@reg_escape('culong')
def escape_culong(char: str, codec: str) -> str:
    """Escape scheme for four byte C/C++ Unicode escape sequences.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    x = ord(char)
    return f'\\U{x:08x}'


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
    return f'&#x{n:x};'


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


@reg_escape('java')
def escape_java(char: str, codec: str) -> str:
    """Escape scheme for Java encoding, based on the Java SE
    Specification `here.`_

    .. _here: https://docs.oracle.com/javase/specs/jls/se20/html/jls-3.html

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    table = {
        '\u0008': r'\b',
        '\u0020': r'\s',
        '\u000c': r'\f',
        '\u000a': r'\n',
        '\u000d': r'\r',
        '\u0009': r'\t',
        '\u0027': r"\'",
        '\u0022': r'\"',
        '\u005c': r'\\',
    }
    if char in table:
        return table[char]
    return escape_javao(char, codec)


@reg_escape('javao')
def escape_javao(char: str, codec: str) -> str:
    """Escape scheme for Java octal encoding, based on the Java SE
    Specification `here.`_

    .. _here: https://docs.oracle.com/javase/specs/jls/se20/html/jls-3.html

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    n = ord(char)
    if n > 0o377:
        return escape_javau(char, codec)
    return f'\\{n:o}'


@reg_escape('javau')
def escape_javau(char: str, codec: str) -> str:
    """Escape scheme for Java Unicode encoding, based on the Java SE
    Specification `here.`_

    .. _here: https://docs.oracle.com/javase/specs/jls/se20/html/jls-3.html

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    b = char.encode('utf_16_be')
    result = ''
    for i in range(0, len(b), 2):
        result += '\\u'
        result += f'{b[i]:02x}'
        result += f'{b[i + 1]:02x}'
    return result


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
