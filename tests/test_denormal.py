"""
test_denormal
~~~~~~~~~~~~~

Unit tests for :mod:`charex.denormal`.
"""
from charex import denormal as d


def test_denormalize():
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


def test_denormalize_maxdepth():
    """When given a string, a normalization form, and a maximum depth,
    :func:`charex.denormal.denormal` returns a tuple of strings that
    will normalize to the given string, limiting the recursion by the
    maximum depth.
    """
    exp = (
        '\ufe64\ufe63\ufe65',
    )
    act = d.denormalize('<->', 'nfkc', 1)
    assert exp == act


def test_count_denormalizations():
    """Given a string and a normalization form,
    :func:`charex.denormal.count_denormalizations`
    returns the number of strings that will normalize
    to the given string.
    """
    assert d.count_denormalizations('<->', 'nfkc') == 8


def test_count_denormalizations_maxdepth():
    """When given a string, a normalization form, and a maximum depth,
    :func:`charex.denormal.count_denormalizations` returns the number
    of strings that will normalize to the given string, limiting the
    recursion by the maximum depth.
    """
    assert d.count_denormalizations('<->', 'nfkc', 1) == 1
