"""
test_charsets
~~~~~~~~~~~~~

Unit tests for :mod:`charex.charsets`.
"""
from charex import charsets as cs


# Unit tests.
def test_multiencode():
    """Given a code point and a list of character sets, return the
    :class:`bytes` for that code point in each character set as a
    :class:`dict`.
    """
    exp = {
        'ascii': b'',
        'cp1252': b'\x93',
        'mac_roman': b'\xd2',
        'utf_8': b'\xe2\x80\x9c',
    }
    codecs = exp.keys()
    act = cs.multiencode('“', codecs)
    assert exp == act


def test_multiencode():
    """Given an integer and a sequence of strings that reference
    decoding codecs, :func:`charex.charsets.multiencode` returns
    the code point for each given codec as a :class:`dict`.
    """
    exp = {
        'ascii': '',
        'cp1252': 'é',
        'iso8859_7': 'ι',
        'utf_16_be': 'é',
        'utf_16_le': 'é',
        'utf_16': 'é',
    }
    codecs = exp.keys()
    act = cs.multidecode(0xe9, codecs)
    assert exp == act


def test_multidecode_bytes():
    """Given bytes and a sequence of strings that reference
    decoding codecs, :func:`charex.charsets.multiencode` returns
    the code point for each given codec as a :class:`dict`.
    """
    exp = {
        'ascii': '',
        'cp1252': 'é',
        'iso8859_7': 'ι',
        'utf_16_be': 'é',
        'utf_16_le': 'é',
        'utf_16': 'é',
    }
    codecs = exp.keys()
    act = cs.multidecode(b'\xe9', codecs)
    assert exp == act


def test_multidecode_str():
    """Given a hex string and a sequence of strings that reference
    decoding codecs, :func:`charex.charsets.multiencode` returns
    the code point for each given codec as a :class:`dict`.
    """
    exp = {
        'ascii': '',
        'cp1252': 'é',
        'iso8859_7': 'ι',
        'utf_16_be': 'é',
        'utf_16_le': 'é',
        'utf_16': 'é',
    }
    codecs = exp.keys()
    act = cs.multidecode('e9', codecs)
    assert exp == act
