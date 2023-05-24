"""
test_charsets
~~~~~~~~~~~~~

Unit tests for :mod:`charex.charsets`.
"""
from charex import charsets as cs


# Tests for get_codecs.
def test_get_codecs():
    """WHen called, return a tuple of registered codecs."""
    exp = tuple(codec for codec in cs.codecs.keys())
    assert cs.get_codecs() == exp


# Test get_codec_description.
def test_get_description():
    """Given the name of a character set codec, return the description
    of that codec.
    """
    codec = 'ascii'
    info = cs.codecs[codec]
    exp = info.description
    assert cs.get_description(codec) == exp


# Tests for multidecode.
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


def test_multidecode_int():
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
    act = cs.multidecode('0xe9', codecs)
    assert exp == act


def test_multidecode_str_and_no_codecs(mocker):
    """Given a hex string, :func:`charex.charsets.multiencode` returns
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
    mocker.patch(
        'charex.charsets.get_codecs',
        return_value=tuple(codec for codec in exp)
    )
    act = cs.multidecode('0xe9')
    assert exp == act


# Tests for multiencode.
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


def test_multiencode_codecs_none(mocker):
    """Given a code point, return the :class:`bytes` for that code point
    in each character set as a :class:`dict`.
    """
    exp = {
        'ascii': b'',
        'cp1252': b'\x93',
        'mac_roman': b'\xd2',
        'utf_8': b'\xe2\x80\x9c',
    }
    mocker.patch(
        'charex.charsets.get_codecs',
        return_value=tuple(codec for codec in exp)
    )
    act = cs.multiencode('“')
    assert exp == act


def test_multiencode_codecs_tuple():
    """Given a code point and a :class:`tuple` of character sets, return
    the :class:`bytes` for that code point in each character set as a
    :class:`dict`.
    """
    exp = {
        'ascii': b'',
        'cp1252': b'\x93',
        'mac_roman': b'\xd2',
        'utf_8': b'\xe2\x80\x9c',
    }
    codecs = tuple(codec for codec in exp)
    act = cs.multiencode('“', codecs)
    assert exp == act


def test_multiencode_unicode():
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
    act = cs.multiencode('U+201c', codecs)
    assert exp == act
