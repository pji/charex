"""
denormal
~~~~~~~~

Functions for reversing normalization of string.
"""
from collections.abc import Sequence

from charex.charex import Character


def denormalize(s: str, form: str) -> tuple[str, ...]:
    """Denormalize a string."""
    char = Character(s[0])
    dechars = char.reverse_normalize(form)
    if not dechars:
        dechars = (char.value,)

    results = []
    if s[1:]:
        tails = denormalize(s[1:], form)
        for dechar in dechars:
            for tail in tails:
                results.append(dechar + tail)
        return tuple(results)

    else:
        return dechars
