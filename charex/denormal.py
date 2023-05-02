"""
denormal
~~~~~~~~

Functions for reversing normalization of string.
"""
from collections.abc import Sequence
from math import prod

from charex.charex import Character


# Functions.
def count_denormalizations(
    base: str,
    form: str,
    maxdepth: int | None = None
) -> int:
    """Determine the number of denormalizations exist for the string.

    :param base: The :class:`str` to denormalize.
    :param form: The Unicode normalization for to denormalize from.
        Valid values are: NFC, NFD, NFKC, NFKD.
    :param maxdepth: How many individual characters to use when
        denormalizing the base. This is used to limit the total
        number of denormalizations of the overall base.
    :return: The number of denormalizations as a :class:`int`.
    :rtype: int
    """
    chars = (Character(c) for c in base)
    counts = []
    for char in chars:
        count = len(char.reverse_normalize(form))
        if count == 0:
            count = 1
        if maxdepth and count > maxdepth:
            count = maxdepth
        counts.append(count)
    return int(prod(counts))


def denormalize(
    base: str,
    form: str,
    maxdepth: int | None = None
) -> tuple[str, ...]:
    """Denormalize a string.

    :param base: The :class:`str` to denormalize.
    :param form: The Unicode normalization for to denormalize from.
        Valid values are: NFC, NFD, NFKC, NFKD.
    :param maxdepth: How many individual characters to use when
        denormalizing the base. This is used to limit the total
        number of denormalizations of the overall base.
    :return: The denormalizations as a :class:`tuple`.
    :rtype: tuple
    """
    char = Character(base[0])
    dechars = char.reverse_normalize(form)
    if not dechars:
        dechars = (char.value,)
    if maxdepth and len(dechars) > maxdepth:
        dechars = dechars[:maxdepth]

    results = []
    if base[1:]:
        tails = denormalize(base[1:], form, maxdepth)
        for dechar in dechars:
            for tail in tails:
                results.append(dechar + tail)
        return tuple(results)

    else:
        return dechars
