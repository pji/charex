"""
test_db
~~~~~~~

Unit tests for :mod:`charex.db`.
"""
import pytest

from charex import db


# Test alias_property.
def test_alias_property():
    """Given the long name for a property, return the alias of that
    property if it exists. If it doesn't exist, return the long name.
    """
    assert db.alias_property('General_Category') == 'gc'
    assert db.alias_property('spam') == 'spam'


def test_alias_value():
    """Given a property alias and the long name for a value of that
    property, return the alias of that value if it exists. If
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


# Test cache.
def test_cache():
    """When called, an attribute of :class:`FileCache` should return
    the data for the file tied to that attribute.
    """
    assert db.cache.blocks[0].start == 0x0000
    assert '0958' in db.cache.compositionexclusions
    assert '0340' in db.cache.derivednormalizationprops[1]['comp_ex']
    assert db.cache.jamo['1100'] == 'G'
    assert '0009' in db.cache.proplist['wspace']
    assert db.cache.unicodedata['0020'].na == 'SPACE'


# Test get_value_for_code.
def test_get_value_for_code():
    """Given a property and a code point,
    :func:`charex.db.get_value_for_code` should
    return the value for that property for the
    code point.
    """
    code = '0020'
    assert db.get_value_for_code('na', code) == 'SPACE'
    assert db.get_value_for_code('scx', code) == 'Zyyy'


# Test load_derived_normal.
def test_load_derived_normal():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, :func:`charex.db.load_derived_normal` should return the data
    contained within the path as a :class:`tuple`.
    """
    pi = db.PathInfo(
        'DerivedNormalizationProps.txt', 'UCD.zip', 'derived_normal', ';'
    )
    single, simple = db.load_derived_normal(pi)
    assert single['fc_nfkc']['037a'] == '0020 03B9'
    assert single['nfkc_cf']['e0fff'] == ''
    assert '0340' in simple['comp_ex']
    assert 'e0fff' in simple['cwkcf']


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


# Test load_prop_list.
def test_load_prop_list():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, :func:`charex.db.load_prop_list` should return the data
    contained within the path as a :class:`dict`.
    """
    pi = db.PathInfo(
        'PropList.txt', 'UCD.zip', 'prop_list', ';'
    )
    data = db.load_prop_list(pi)
    assert '0000' not in data['wspace']
    assert '0009' in data['wspace']
    assert '1f1ff' in data['ri']
    assert '10ffff' not in data['ri']


# Test load_property_alias.
def test_load_property_alias():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, :func:`charex.db.load_property_alias` should return the data
    contained within the path as a :class:`set`.
    """
    pi = db.PathInfo(
        'PropertyAliases.txt', 'UCD.zip', 'property_alias', ';'
    )
    data = db.load_property_alias(pi)
    assert data['kaccountingnumeric'].alias == 'cjkAccountingNumeric'
    assert data['expands_on_nfkd'].alias == 'XO_NFKD'


# Test load_simple_list.
def test_load_simple_list():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, :func:`charex.db.load_simple_list` should return the data
    contained within the path as a :class:`set`.
    """
    pi = db.PathInfo(
        'CompositionExclusions.txt', 'UCD.zip', 'simple_list', ';'
    )
    data = db.load_simple_list(pi)
    assert '0000' not in data
    assert '0958' in data
    assert '1d1c0' in data
    assert '10FFFF' not in data


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
    assert data[106] == db.ValueRange(0x2fe0, 0x2ff0, 'No_Block')
