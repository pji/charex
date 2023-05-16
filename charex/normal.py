"""
normal
~~~~~~

Functions for normalizing strings.
"""
from collections.abc import Callable
from json import dumps
import unicodedata as ucd

from charex import util


# Registry.
forms = {}


# Registration.
class reg_form:
    """A decorator for registering normalization forms.

    :param key: The name the normalization form is registered under.
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
def build_denormalization_map(norm_fn: Callable[[str], str]) -> str:
    """Create a JSON string mapping each Unicode character to the
    other Unicode characters that normalize to it.

    :param norm_fn: The normalization function.
    :return: The denormalization map as a JSON :class:`str`.
    :rtype: str
    """
    dn_map: dict[str, list[str]] = {}
    for n in range(0x10FFFF):
        base = chr(n)
        normal = norm_fn(base)
        if normal and normal != base:
            dn_map.setdefault(normal, list())
            dn_map[normal].append(base)
    return dumps(dn_map, indent=4)


def get_description(formkey: str) -> str:
    """Get the description for the normalization form.

    :param formkey: The key for the form in the form registry.
    :return: The description as a :class:`str`.
    :rtype: str
    """
    form = forms[formkey]
    return util.get_description_from_docstring(form)


def get_forms() -> tuple[str, ...]:
    """Return the names of the registered normalization forms.

    :return: The names of the normalization forms as a :class:`tuple`.
    :rtype: tuple
    """
    return tuple(form for form in forms)


# Normalization function.
def normalize(formkey: str, base: str) -> str:
    """Normalize the base string with the form.

    :param formkey: The key of a registered normalization form.
    :param base: The string to normalize.
    :return: The normalized :class:`str`.
    :rtype: str
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
