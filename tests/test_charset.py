"""
test_charsets
~~~~~~~~~~~~~

Unit tests for :mod:`charex.charsets`.
"""
from charex import charsets as cs


# Unit tests.
def test_multiencode():
    """Given an integer and a sequence of strings that reference
    decoding codecs, :func:`charex.charsets.multiencode` returns
    the code point for each given codec as a :class:`dict`.
    """
    exp = {
        'ascii': '',
        'cp1252': 'é',
        'iso8859_7': 'ι',
    }
    codecs = exp.keys()
    act = cs.multiencode(0xe9, codecs)
    assert exp == act
