"""
test_db
~~~~~~~

Unit tests for :mod:`charex.db`.
"""
from charex import db


# Test alias_value.
def test_alias_value():
    """Given a property alias and the long name for a value of that
    property, return the alias of that property if it exists. If
    it doesn't exist, return the long name.
    """
    assert db.alias_value('gc', 'Letter') == 'L'
    assert db.alias_value('spam', 'eggs') == 'eggs'


# Test build_hangul_name.
def test_build_hangul_name():
    """When given a code point for a Hangul syllable,
    :func:`charex.db.build_jame_name` should return the Jamo
    name for that code point.
    """
    assert db.build_hangul_name('d4db') == 'PWILH'


# Test load_from_archive.
def test_load_from_archive():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, return the lines contained in the file as a :class:`tuple`.
    """
    pi = db.PathInfo('Jamo.txt', 'UCD.zip', 'single_value', ';')
    lines = db.load_from_archive(pi)
    assert lines[0] == '# Jamo-14.0.0.txt'
    assert lines[-1] == '# EOF'


# Test load_path_map.
def test_load_path_map():
    """When called, :func:`charex.db.load_path_map` should return a
    :class:`dict` that allows mapping of a Unicode file name to the
    archive that contains it.
    """
    exp = 'UCD.zip'
    path = 'unicodedata'
    pm = db.load_path_map()
    pi = pm[path]
    assert pi.archive == exp


# Test load_value_range.
def test_value_range():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, :func:`charex.db.load_value_range` should return the data
    contained within the path as a :class:`tuple`.
    """
    pi = db.PathInfo('Blocks.txt', 'UCD.zip', 'value_range', ';')
    data = db.load_value_range(pi)
    assert data[0] == db.ValueRange(0x0000, 0x0080, 'Basic Latin')
    assert data[-1] == db.ValueRange(
        0x100000, 0x110000, 'Supplementary Private Use Area-B'
    )


# Test load_single_value.
def test_load_single_value():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, :func:`charex.db.load_single_value` should return the data
    contained within the path as a :class:`collections.defaultdict`.
    """
    pi = db.PathInfo('Jamo.txt', 'UCD.zip', 'single_value', ';')
    data = db.load_single_value(pi)
    assert data['1100'] == 'G'
    assert data['11c2'] == 'H'
    assert data['0041'] == ''


# Test load_unicode_data.
def test_load_unicode_data():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, :func:`charex.db.load_unicode_data` should return the data
    contained within the path as a :class:`dict`.
    """
    pi = db.PathInfo('UnicodeData.txt', 'UCD.zip', 'unicode_data', ';')
    data = db.load_unicode_data(pi)
    assert data['0000'].code == '0000'
    assert data['10fffd'].code == '10FFFD'
    assert data['2a701'].na == 'CJK UNIFIED IDEOGRAPH-2A701'
    assert data['d4db'].na == 'HANGUL SYLLABLE PWILH'


# Test load_value_aliases.
def test_load_value_aliases():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, :func:`charex.db.load_value_aliases` should return the data
    contained within the path as a :class:`collections.dict`.
    """
    pi = db.PathInfo('PropertyValueAliases.txt', 'UCD.zip', '', ';')
    data = db.load_value_aliases(pi)
    assert data['ahex']['no'].alias == 'N'
    assert data['xids']['no'].alias == 'N'
