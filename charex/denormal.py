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
    """Determine the number of denormalizations exist for the string."""
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
    """Denormalize a string."""
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
