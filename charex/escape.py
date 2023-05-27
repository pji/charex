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

    Usage
    -----
    To register a new escape scheme::

        >>> @reg_escape('double')
        ... def double(char: str, codec: str) -> str:
        ...     '''Double the character.'''
        ...     return char + char
        ...
        >>> # Demonstrate the registration worked.
        >>> 'double' in get_schemes()
        True
        >>> escape_text('spam', 'double')
        'ssppaamm'

    """
    def __init__(self, key: str) -> None:
        self.key = key

    def __call__(
        self,
        fn: Callable[[str, str], str]
    ) -> Callable[[str, str], str]:
        schemes[self.key] = fn
        return fn


# Exceptions.
class EscapeError(ValueError):
    """The escape scheme could not escape the character."""


# Utility functions.
def get_named_entity(char: str) -> str:
    """Get a named entity from the HTML entity data."""
    lines = util.read_resource('entities')
    json = ''.join(lines)
    data = loads(json)
    by_char = {data[key]['characters']: key for key in data}
    try:
        cached_entities[char] = by_char[char]
    except KeyError:
        cached_entities[char] = escape_htmldec(char, '')
    return cached_entities[char]


def get_description(schemekey: str) -> str:
    """Get the description for the scheme.

    :param schemekey: The key for the scheme in the scheme registry.
    :return: The description as a :class:`str`.
    :rtype: str
    """
    scheme = schemes[schemekey]
    return util.get_description_from_docstring(scheme)


def get_schemes() -> tuple[str, ...]:
    """Return the keys of the registered escape schemes.

    :return: The scheme keys as a :class:`tuple`.
    :rtype: tuple
    """
    return tuple(scheme for scheme in schemes)


def hex_byte_escape(char: str) -> str:
    """Perform the common single hexadecimal byte escape on the
    character.

    :param char: The character to escape.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    n = ord(char)
    if n > 0xFF:
        raise EscapeError('Cannot escape characters over 0xFF.')
    return f'\\x{n:02x}'


def lookup_escape(char: str, table: dict[str, str]) -> str:
    """Perform a table lookup to escape the character.

    :param char: The character to escape.
    :param table: The table for the lookup.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        return table[char]
    except KeyError:
        raise EscapeError('Character not in table.')


def octal_escape(char: str) -> str:
    """Perform the common octal escape on the character.

    :param char: The character to escape.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    n = ord(char)
    if n > 0o377:
        raise EscapeError('Cannot escape characters over 0o377.')
    return f'\\{n:o}'


def unicode_2_byte_escape(char: str) -> str:
    """Perform the common Unicode two byte escape on the
    character.

    :param char: The character to escape.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    n = ord(char)
    if n > 0xFFFF:
        raise EscapeError('Cannot escape characters over 0xFFFF.')
    return f'\\u{n:04x}'


def unicode_utf16_escape(char: str) -> str:
    """Perform the common Unicode UTF-16 escape on the character.

    :param char: The character to escape.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        return unicode_2_byte_escape(char)
    except EscapeError:
        b = char.encode('utf_16_be')
        result = ''
        for i in range(0, len(b), 2):
            result += '\\u'
            result += f'{b[i]:02x}'
            result += f'{b[i + 1]:02x}'
        return result


# Escape schemes.
@reg_escape('c')
def escape_c(char: str, codec: str) -> str:
    """Escape scheme for C escape sequences as defined by C17.

    This is derived from the Wikipedia list, since I don't have access
    to the C17 specification.

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
        # '\u001b': r'\e',    # Non-standard, supported by gcc, clang, tcc.
        '\u0027': r"\'",
        '\u0022': r'\"',
        '\u003f': r'\?',
        '\u005c': r'\\',
    }
    try:
        return lookup_escape(char, table)
    except EscapeError:
        return escape_co(char, codec)


@reg_escape('co')
def escape_co(char: str, codec: str) -> str:
    """Escape scheme for C octal escape sequences as defined by C17.

    This is derived from the Wikipedia list, since I don't have access
    to the C17 specification.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        return octal_escape(char)
    except EscapeError:
        return escape_cu(char, codec)


@reg_escape('cu')
def escape_cu(char: str, codec: str) -> str:
    """Escape scheme for C Unicode escape sequences as defined by C17.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        return unicode_2_byte_escape(char)
    except EscapeError:
        return escape_culong(char, codec)


@reg_escape('culong')
def escape_culong(char: str, codec: str) -> str:
    """Escape scheme for four byte C Unicode escape sequences as
    defined by C17.

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    x = ord(char)
    return f'\\U{x:08x}'


@reg_escape('html')
def escape_html(char: str, codec: str) -> str:
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


@reg_escape('htmldec')
def escape_htmldec(char: str, codec: str) -> str:
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


@reg_escape('java')
def escape_java(char: str, codec: str) -> str:
    """Escape scheme for Java encoding, based on the Java SE
    Specification.

    The specification can be found `here.`_

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
    try:
        return lookup_escape(char, table)
    except EscapeError:
        return escape_javao(char, codec)


@reg_escape('javao')
def escape_javao(char: str, codec: str) -> str:
    """Escape scheme for Java octal encoding, based on the Java SE
    Specification.

    The specification can be found `here.`_

    .. _here: https://docs.oracle.com/javase/specs/jls/se20/html/jls-3.html

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        return octal_escape(char)
    except EscapeError:
        return escape_javau(char, codec)


@reg_escape('javau')
def escape_javau(char: str, codec: str) -> str:
    """Escape scheme for Java Unicode encoding, based on the Java SE
    Specification.

    The specification can be found `here.`_

    .. _here: https://docs.oracle.com/javase/specs/jls/se20/html/jls-3.html

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    return unicode_utf16_escape(char)


@reg_escape('js')
def escape_js(char: str, codec: str) -> str:
    """Escape scheme for JavaScript encoding, based on the ECMA-262
    Specification.

    The specification can be found `here.`_

    .. _here: https://262.ecma-international.org/13.0/\
#sec-literals-string-literals

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    table = {
        '\u0008': r'\b',
        '\u0009': r'\t',
        '\u000a': r'\n',
        '\u000b': r'\v',
        '\u000c': r'\f',
        '\u000d': r'\r',
        '\u0022': r'\"',
        '\u005c': r'\\',
    }
    try:
        return lookup_escape(char, table)
    except EscapeError:
        return escape_jso(char, codec)


@reg_escape('jso')
def escape_jso(char: str, codec: str) -> str:
    """Escape scheme for JavaScript octal encoding, based on the
    ECMA-262 Specification.

    The specification can be found `here.`_

    .. _here: https://262.ecma-international.org/13.0/\
#sec-literals-string-literals

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        return octal_escape(char)
    except EscapeError:
        return escape_jsu(char, codec)


@reg_escape('jsu')
def escape_jsu(char: str, codec: str) -> str:
    """Escape scheme for JavaScript unicode encoding, based on the
    ECMA-262 Specification.

    The specification can be found `here.`_

    .. _here: https://262.ecma-international.org/13.0/\
#sec-literals-string-literals

    :param char: The character to escape.
    :param codec: Unused.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    try:
        return unicode_2_byte_escape(char)
    except EscapeError:
        return escape_jscp(char, codec)


@reg_escape('jscp')
def escape_jscp(char: str, codec: str) -> str:
    """Escape scheme for JavaScript code point encoding, based on the
    ECMA-262 Specification.

    The specification can be found `here.`_

    .. _here: https://262.ecma-international.org/13.0/\
#sec-literals-string-literals

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    x = ord(char)
    return f'\\u{{{x:x}}}'


@reg_escape('json')
def escape_json(char: str, codec: str) -> str:
    """Escape scheme for JSON encoding, based on the ECMA-404
    Specification.

    The specification can be found `here.`_

    .. _here: https://www.ecma-international.org/publications-and-standards/\
standards/ecma-404/ECMA-404_2nd_edition_december_2017.pdf

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    table = {
        '\u0022': r'\"',
        '\u005c': r'\\',
        '\u002f': r'\/',
        '\u0008': r'\b',
        '\u000c': r'\f',
        '\u000a': r'\n',
        '\u000d': r'\r',
        '\u0009': r'\t',
    }
    if char in table:
        return table[char]
    return escape_jsonu(char, codec)


@reg_escape('jsonu')
def escape_jsonu(char: str, codec: str) -> str:
    """Escape scheme for JSON Unicode encoding, based on the ECMA-404
    Specification.

    The specification can be found `here.`_

    .. _here: https://www.ecma-international.org/publications-and-standards/\
standards/ecma-404/ECMA-404_2nd_edition_december_2017.pdf

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    return unicode_utf16_escape(char)


@reg_escape('smol')
def escape_smol(char: str, codec: str) -> str:
    """Escape scheme for smol characters, based loosely on the
    Unicode superscript characters.

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    norms = 'abcdefghijklmnopqrstuvwxyz'
    smol = 'ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᑫʳˢᵗᵘᵛʷˣʸᶻ'
    table = {k: v for k, v in zip(norms, smol)}
    try:
        return lookup_escape(char, table)
    except EscapeError:
        return char


@reg_escape('sql')
def escape_sql(char: str, codec: str) -> str:
    """Escape scheme for MySQL encoding, based on the MySQL
    Specification.

    The specification can be found `here.`_

    .. _here: https://dev.mysql.com/doc/refman/8.0/en/string-literals.html

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    table = {
        '\u0000': r'\0',
        '\u0027': r"\'",
        '\u0022': r'\"',
        '\u0008': r'\b',
        '\u000a': r'\n',
        '\u000d': r'\r',
        '\u0009': r'\t',
        '\u0026': r'\Z',
        '\u005c': r'\\',
        '\u0025': r'\%',
        '\u005f': r'\_',
    }
    try:
        return lookup_escape(char, table)
    except EscapeError:
        return char


@reg_escape('sqldq')
def escape_sqldq(char: str, codec: str) -> str:
    """Escape scheme for MySQL encoding, based on the MySQL
    Specification. This escapes qoutes by doubling them rather
    than using a backslash.

    The specification can be found `here.`_

    .. _here: https://dev.mysql.com/doc/refman/8.0/en/string-literals.html

    :param char: The character to escape.
    :param codec: The character set to use when encoding the character.
    :return: The escaped character as a :class:`str`.
    :rtype: str
    """
    table = {
        '\u0000': r'\0',
        '\u0027': r"''",
        '\u0022': r'""',
        '\u0008': r'\b',
        '\u000a': r'\n',
        '\u000d': r'\r',
        '\u0009': r'\t',
        '\u0026': r'\Z',
        '\u005c': r'\\',
        '\u0025': r'\%',
        '\u005f': r'\_',
    }
    try:
        return lookup_escape(char, table)
    except EscapeError:
        return char


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
    """Escape the string with the scheme.

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
