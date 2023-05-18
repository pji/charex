"""
denormal
~~~~~~~~

Functions for reversing normalization of string.
"""
from collections.abc import Sequence
from math import prod
from random import choice, seed

from charex.charex import Character


# Functions.
def count_denormalizations(
    base: str,
    form: str,
    maxdepth: int | None = None
) -> int:
    """Determine the number of denormalizations that exist for the string.

    :param base: The :class:`str` to denormalize.
    :param form: The Unicode normalization form to denormalize from.
        Valid values are: casefold, nfc, nfd, nfkc, nfkd.
    :param maxdepth: (Optional.) How many individual characters to use
        when denormalizing the base. This is used to limit the total
        number of denormalizations of the overall base.
    :return: The number of denormalizations as an :class:`int`.
    :rtype: int
    """
    chars = (Character(c) for c in base)
    counts = []
    for char in chars:
        count = len(char.denormalize(form))
        if count == 0:
            count = 1
        if maxdepth and count > maxdepth:
            count = maxdepth
        counts.append(count)
    return int(prod(counts))


def denormalize(
    base: str,
    form: str,
    maxdepth: int | None = None,
    maxresults: int | None = None,
    random: bool = False,
    seed_: bytes | int | str = ''
) -> tuple[str, ...]:
    """Denormalize a string.

    :param base: The :class:`str` to denormalize.
    :param form: The Unicode normalization form to denormalize from.
        Valid values are: casefold, nfc, nfd, nfkc, nfkd.
    :param maxdepth: (Optional.) How many individual characters to use
        when denormalizing the base. This is used to limit the total
        number of denormalizations of the overall base.
    :param maxresults: (Optional.) The maximum number of results to
        return. Default behavior varies based on the `random` parameter.
        If `random` is `False`, default is to return all possible
        denormalizattions. Otherwise, the default is to return one.
    :param random: (Optional.) Whether to pick randomly from the
        possible denormalization results. Defaults to false.
    :param seed: (Optional.) A seed value for the random number generator.
        Defaults to not seeding the generator.
    :return: The denormalizations as a :class:`tuple`.
    :rtype: tuple
    """
    if random:
        return random_denormalize(base, form, maxresults, seed_)

    # Get the denormalized forms of the first character.
    char = Character(base[0])
    dechars = list(char.denormalize(form))

    # If there are no denormalized forms, then it is the denormalized form.
    if not dechars:
        dechars = [char.value,]

    # Limit the number of permutations by limiting the number of
    # denormalized forms we are looking at.
    if maxdepth and len(dechars) > maxdepth:
        dechars = dechars[:maxdepth]

    # If there are more characters left, use recursion to get the
    # permutations for those characters, then get the permutations
    # with this character.
    if base[1:]:
        results = []
        tails = denormalize(base[1:], form, maxdepth, maxresults)
        for dechar in dechars:
            for tail in tails:
                results.append(dechar + tail)

    # If there are no characters left, then the permutations are just
    # the denormalized forms of the character.
    else:
        results = dechars

    # Truncate to the maximum results and return.
    if maxresults:
        results = results[:maxresults]
    return tuple(results)


def random_denormalize(
    base: str,
    form: str,
    maxresults: int | None = None,
    seed_: bytes | int | str = ''
) -> tuple[str, ...]:
    """Randomly denormalize a string.

    :param base: The :class:`str` to denormalize.
    :param form: The Unicode normalization for to denormalize from.
        Valid values are: NFC, NFD, NFKC, NFKD.
    :param maxresults: (Optional.) The maximum number of results to
        return. Default behavior varies based on the `random` parameter.
        If `random` is `False`, default is to return all possible
        denormalizattions. Otherwise, the default is to return one.
    :param seed: (Optional.) A seed value for the random number generator.
        Defaults to not seeding the generator.
    :return: The denormalizations as a :class:`tuple`.
    :rtype: tuple
    """
    # Ensure at least one result is returned.
    if not maxresults:
        maxresults = 1

    # Seeding the RNG allows for repeatability in testing.
    if seed_:
        seed(seed_)

    # Get the denormalized forms for all the characters in the string.
    chars = [
        denormalize(char, form)
        for char in base
    ]

    # Randomly pick from the possible denormalizations for each character
    # when creating the denormalized strings, then return the results.
    results = []
    for _ in range(maxresults):
        result = ''.join(choice(char) for char in chars)
        results.append(result)
    return tuple(results)
