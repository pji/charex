"""
test_denormal
~~~~~~~~~~~~~

Unit tests for :mod:`charex.denormal`.
"""
from charex import denormal as d


def test_simple_string():
    """When given a string and a normalization form,
    :func:`charex.denormal.denormal` returns a tuple of
    strings that will normalize to the given string.
    """
    exp = (
        '\ufe64\ufe63\ufe65',
        '\ufe64\ufe63\uff1e',
        '\ufe64\uff0d\ufe65',
        '\ufe64\uff0d\uff1e',
        '\uff1c\ufe63\ufe65',
        '\uff1c\ufe63\uff1e',
        '\uff1c\uff0d\ufe65',
        '\uff1c\uff0d\uff1e',
    )
    act = d.denormalize('<->', 'nfkc')
    assert exp == act
