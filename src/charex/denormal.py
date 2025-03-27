"""
denormal
~~~~~~~~

Functions for reversing normalization of string.
"""
from collections.abc import Generator, Sequence
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

    Usage
    -----
    To count the number of possible denormalizations for a given string
    and form::

        >>> base = '<->'
        >>> form = 'nfkc'
        >>> count_denormalizations(base, form)
        8

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
    maxdepth: int = 0,
    maxresults: int | None = None,
    random: bool = False,
    seed_: bytes | int | str = ''
) -> tuple[str, ...]:
    """Denormalize a string.

    :param base: The :class:`str` to denormalize.
    :param form: The Unicode normalization form to denormalize from.
        Valid values are: casefold, nfc, nfd, nfkc, nfkd.
    :param maxdepth: (Optional.) How many denormalizations per character
        in the base string to use when denormalizing the base. This is
        used to limit the total number of denormalizations of the overall
        base. If `maxdepth` is zero, the number of denormalizations to
        use per character is not limited.
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

    Usage
    -----
    To denormalize a given string with the given form::

        >>> base = '<>'
        >>> form = 'nfkc'
        >>> denormalize(base, form)
        ('﹤﹥', '﹤＞', '＜﹥', '＜＞')

    The `maxdepth` parameter can be used to limit the number of
    denormalizations per character in the `base` string. This is
    useful when you want just a few denormalizations of a string
    with a very large number of denormalizations::

        >>> base = 'hi'
        >>> form = 'nfkc'
        >>> maxdepth = 2
        >>> denormalize(base, form, maxdepth)
        ('ʰᵢ', 'ʰⁱ', 'ₕᵢ', 'ₕⁱ')

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


def gen_denormalize(
    base: str,
    form: str,
    maxdepth: int = 0
) -> Generator[str, None, None]:
    """Denormalize a string, yielding the results as they are
    generated.

    :param base: The :class:`str` to denormalize.
    :param form: The Unicode normalization form to denormalize from.
        Valid values are: casefold, nfc, nfd, nfkc, nfkd.
    :param maxdepth: (Optional.) How many denormalizations per character
        in the base string to use when denormalizing the base. This is
        used to limit the total number of denormalizations of the overall
        base. If `maxdepth` is zero, the number of denormalizations to
        use per character is not limited.
    :return: A :class:`collections.abc.Generator` that yields the
        denormalization results.
    :rtype: collections.abc.Generator

    Usage
    -----
    To generate denormalizations for a given string with a given form::

        >>> base = '<>'
        >>> form = 'nfkc'
        >>> dngen = gen_denormalize(base, form)
        >>> [result for result in dngen]
        ['﹤﹥', '﹤＞', '＜﹥', '＜＞']

    The `maxdepth` parameter can be used to limit the number of
    denormalizations per character in the `base` string. This is
    useful when you want just a few denormalizations of a string
    with a very large number of denormalizations::

        >>> base = 'hi'
        >>> form = 'nfkc'
        >>> maxdepth = 2
        >>> dngen = gen_denormalize(base, form, maxdepth)
        >>> [result for result in dngen]
        ['ʰᵢ', 'ʰⁱ', 'ₕᵢ', 'ₕⁱ']

    """
    c, rest = base[0], base[1:]
    char = Character(c)
    dechars = char.denormalize(form)
    if not dechars:
        dechars = (char.value,)
    if maxdepth:
        dechars = dechars[:maxdepth]

    if rest:
        for dechar in dechars:
            for tail in gen_denormalize(rest, form, maxdepth):
                yield dechar + tail

    else:
        for dechar in dechars:
            yield dechar


def gen_random_denormalize(
    base: str,
    form: str,
    maxresults: int = 1,
    seed_: bytes | int | str = ''
) -> Generator[str, None, None]:
    """Randomly denormalize a string, yielding the results as they
    are generated. This is useful when returning all results for
    a denormalization is unreasonably large, as can easily happen
    when denormalizing strings containing Latin letters.

    :param base: The :class:`str` to denormalize.
    :param form: The Unicode normalization for to denormalize from.
        Valid values are: NFC, NFD, NFKC, NFKD.
    :param maxresults: (Optional.) The maximum number of results to
        return. The default is to return one.
    :param seed: (Optional.) A seed value for the random number generator.
        Defaults to not seeding the generator.
    :return: A :class:`collections.abc.Generator` that yields the random
        denormalization results.
    :rtype: collections.abc.Generator

    Usage
    -----
    To generate a random denormalization of a given string with a given
    form::

        >>> # The seed parameter seeds the RNG to produce repeatable
        >>> # results for testing. Don't use it unless you want
        >>> # repeatable results.
        >>> seed_ = 'spam'
        >>>
        >>> base = '<script>'
        >>> form = 'nfkc'
        >>> dngrd = gen_random_denormalize(base, form, seed_=seed_)
        >>> [result for result in dngrd]
        ['﹤𝓈ᶜ𝕣𝚒𝙥𝙩＞']

    The `maxresults` parameter tells the generator to return the
    given number of results::

        >>> # The seed parameter seeds the RNG to produce repeatable
        >>> # results for testing. Don't use it unless you want
        >>> # repeatable results.
        >>> seed_ = 'spam'
        >>>
        >>> base = '<script>'
        >>> form = 'nfkc'
        >>> maxresults = 3
        >>> dngrd = gen_random_denormalize(base, form, maxresults, seed_=seed_)
        >>> [result for result in dngrd]
        ['﹤𝓈ᶜ𝕣𝚒𝙥𝙩＞', '＜𝖘ᶜ𝓇𝕚ᵖ𝓉＞', '﹤𝙨𝚌𝑟𝗂𝐩ｔ＞']

    """
    chars = [denormalize(char, form) for char in base]
    if seed_:
        seed(seed_)
    for _ in range(maxresults):
        result = ''.join(choice(char) for char in chars)
        yield result


def random_denormalize(
    base: str,
    form: str,
    maxresults: int | None = None,
    seed_: bytes | int | str = ''
) -> tuple[str, ...]:
    """Randomly denormalize a string. This is useful when returning
    all results for a denormalization is unreasonably large, as can
    easily happen when denormalizing strings containing Latin letters.

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

    Usage
    -----
    To get a random denormalization of the given string using the given
    form::

        >>> # The seed parameter seeds the RNG to produce repeatable
        >>> # results for testing. Don't use it unless you want
        >>> # repeatable results.
        >>> seed_ = 'spam'
        >>>
        >>> base = '<script>'
        >>> form = 'nfkc'
        >>> random_denormalize(base, form,  seed_=seed_)
        ('﹤𝓈ᶜ𝕣𝚒𝙥𝙩＞',)

    The `maxresults` parameter tells the function to return the
    given number of results::

        >>> # The seed parameter seeds the RNG to produce repeatable
        >>> # results for testing. Don't use it unless you want
        >>> # repeatable results.
        >>> seed_ = 'spam'
        >>>
        >>> base = '<script>'
        >>> form = 'nfkc'
        >>> maxresults = 3
        >>> random_denormalize(base, form,  maxresults, seed_=seed_)
        ('﹤𝓈ᶜ𝕣𝚒𝙥𝙩＞', '＜𝖘ᶜ𝓇𝕚ᵖ𝓉＞', '﹤𝙨𝚌𝑟𝗂𝐩ｔ＞')

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
