"""
normal
~~~~~~

Functions for normalizing strings.
"""
from collections.abc import Callable
from itertools import permutations
from json import dumps
import unicodedata as ucd

from charex import util


# Registry.
forms = {}


# Registration.
class reg_form:
    """A decorator for registering normalization forms.

    :param key: The name the normalization form is registered under.

    Usage
    -----
    To register a normalization form::

        >>> from charex import *
        >>>
        >>> @reg_form('a')
        ... def form_a(base: str) -> str:
        ...     '''Make all strings into the letter A.'''
        ...     return 'A'
        ...
        >>> # Demonstrate the registration worked.
        >>> 'a' in get_forms()
        True
        >>> normalize('a', 'spam')
        'A'
    """
    def __init__(self, key: str) -> None:
        self.key = key

    def __call__(
        self,
        fn: Callable[[str], str]
    ) -> Callable[[str], str]:
        forms[self.key] = fn
        return fn


# Utility functions.
def build_denormalization_map(formkey: str) -> str:
    """Create a JSON string mapping each Unicode character to the
    other Unicode characters that normalize to it.

    :param formkey: The key for the normalization function.
    :return: The denormalization map as a JSON :class:`str`.
    :rtype: str
    """
    # The denormalization map.
    dn_map: dict[str, set[str]] = {}

    # Process every Unicode character.
    norm_fn = forms[formkey]
    for n in range(util.LEN_UNICODE):
        base = chr(n)

        # If the character normalizes to a different character,
        # add that relationship to the map.
        normal = norm_fn(base)
        if normal and normal != base:
            dn_map.setdefault(normal, set())
            dn_map[normal].add(base)

        # If the character decomposes, add the relationship between
        # the character and its possible decompositions to the map.
        decomp = form_nfd(base)
        if len(decomp) > 1:
            root, marks = decomp[0], decomp[1:]
            for mut in permutations(marks):
                rmut = root + ''.join(mut)
                normal = norm_fn(rmut)
                if normal != rmut:
                    dn_map.setdefault(normal, set())
                    dn_map[normal].add(rmut)

    # Test to ensure decompositions are accurate and not redundant.
    for normal in dn_map:
        for base in dn_map[normal]:
            actual = norm_fn(base)
            assert actual == normal
            assert actual != base
            assert normal != base

    # Return the map as a JSON string.
    listed = {k: list(dn_map[k]) for k in dn_map}
    ordered = {k: sorted(listed[k]) for k in listed}
    return dumps(ordered, indent=4)


def find_max_decomposition() -> tuple[str, int]:
    """Find the longest single character decomposition.

    :return: The character and the number of characters in the
        decomposition as a :class:`tuple`.
    :rtype: tuple
    """
    long_char = ''
    decomp_max = 0
    for n in range(util.LEN_UNICODE):
        char = chr(n)
        decomp_char = form_nfd(char)
        decomp_len = len(decomp_char)
        if decomp_len > decomp_max:
            long_char = char
            decomp_max = decomp_len
    return long_char, decomp_max


def get_description(formkey: str) -> str:
    """Get the description for the normalization form.

    :param formkey: The key for the form in the form registry.
    :return: The description as a :class:`str`.
    :rtype: str
    """
    form = forms[formkey]
    return util.get_description_from_docstring(form)


def get_forms() -> tuple[str, ...]:
    """Return the keys of the registered normalization forms.

    :return: The names of the normalization forms as a :class:`tuple`.
    :rtype: tuple

    Usage
    -----
    To get a tuple of the registered normalization forms::

        >>> get_forms()
        ('casefold', 'nfc', 'nfd', 'nfkc', 'nfkd')

    """
    return tuple(form for form in forms)


# Normalization function.
def normalize(formkey: str, base: str) -> str:
    """Normalize the base string with the form.

    :param formkey: The key of a registered normalization form.
    :param base: The string to normalize.
    :return: The normalized :class:`str`.
    :rtype: str

    Usage
    -----
    To normalize a string using the given form::

        >>> value = 'SPAM'
        >>> form = 'casefold'
        >>> normalize(form, value)
        'spam'

    """
    form = forms[formkey]
    return form(base)


# Normalization forms.
@reg_form('casefold')
def form_casefold(base: str) -> str:
    """Remove all case distinctions from the string.

    :param base: The string to normalize.
    :return: The normalized :class:`str`.
    :rtype: str
    """
    return str.casefold(base)


@reg_form('nfc')
def form_nfc(base: str) -> str:
    """Normalization form composition.

    :param base: The string to normalize.
    :return: The normalized :class:`str`.
    :rtype: str
    """
    return ucd.normalize('NFC', base)


@reg_form('nfd')
def form_nfd(base: str) -> str:
    """Normalization form decomposition.

    :param base: The string to normalize.
    :return: The normalized :class:`str`.
    :rtype: str
    """
    return ucd.normalize('NFD', base)


@reg_form('nfkc')
def form_nfkc(base: str) -> str:
    """Normalization form compatibility composition.

    :param base: The string to normalize.
    :return: The normalized :class:`str`.
    :rtype: str
    """
    return ucd.normalize('NFKC', base)


@reg_form('nfkd')
def form_nfkd(base: str) -> str:
    """Normalization form compatibility decomposition.

    :param base: The string to normalize.
    :return: The normalized :class:`str`.
    :rtype: str
    """
    return ucd.normalize('NFKD', base)
