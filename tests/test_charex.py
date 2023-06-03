"""
test_charex
~~~~~~~~~~~
"""
import json

import pytest

from charex import charex as c


# Global constants.
UNICODE_LEN = 0x110000


# Test Char.
def test_character_core_properties():
    """A :class:`charex.Character` should have the properties from the
    Unicode data database.
    """
    char = c.Character('a')
    assert char.na == 'LATIN SMALL LETTER A'
    assert char.gc == 'Ll'
    assert char.ccc == '0'
    assert char.bc == 'L'
    assert char.dt == ''
    assert char.nv == ''
    assert char.na1 == ''
    assert char.isc == ''
    assert char.suc == '0041'
    assert char.slc == ''
    assert char.stc == '0041'


def test_character_proplist_properties():
    """A :class:`charex.Character` should have the properties from
    PropList.txt.
    """
    char = c.Character('a')
    assert char.wspace is False
    assert char.bidi_c is False
    assert char.join_c is False
    assert char.dash is False
    assert char.hyphen is False
    assert char.qmark is False
    assert char.term is False
    assert char.omath is False
    assert char.hex is True
    assert char.ahex is True
    assert char.oalpha is False
    assert char.ideo is False
    assert char.dia is False
    assert char.ext is False
    assert char.olower is False
    assert char.oupper is False
    assert char.nchar is False
    assert char.ogr_ext is False
    assert char.idsb is False
    assert char.idst is False
    assert char.radical is False
    assert char.uideo is False
    assert char.odi is False
    assert char.dep is False
    assert char.sd is False
    assert char.loe is False
    assert char.oids is False
    assert char.oidc is False
    assert char.sterm is False
    assert char.vs is False
    assert char.pat_ws is False
    assert char.pat_syn is False
    assert char.pcm is False
    assert char.ri is False


def test_character_multilist_properties():
    """A :class:`charex.Character` should have the properties from
    defined properties that contain multiple values.
    """
    char = c.Character('a')
    assert char.scx == ('Latin',)


def test_character_rangelist_properties():
    """A :class:`charex.Character` should have the properties from
    defined range lists.
    """
    char = c.Character('a')
    assert char.age == '1.1'
    assert char.blk == 'Basic Latin'
    assert char.sc == 'Latin'


def test_character_singleval_properties():
    """A :class:`charex.Character` should have the properties from
    the single value lists.
    """
    char = c.Character('a')
    assert char.hst == 'NA'


# Test Character.
def test_character_init():
    """Given a string containing a character, a :class:`Character`
    object is initialized.
    """
    exp_value = 'a'
    act = c.Character(exp_value)
    assert act.value == exp_value


def test_character_init_with_hex():
    """Given a string containing a hexadecimal number starting with
    "0x", a :class:`Character` object is initialized with the character
    at that address.
    """
    exp_value = 'a'
    act = c.Character('0x0061')
    assert act.value == exp_value


def test_character_init_with_code_point():
    """Given a string containing a unicode code point starting with
    "U+", a :class:`Character` object is initialized with the character
    at that address.
    """
    exp_value = 'a'
    act = c.Character('U+0061')
    assert act.value == exp_value


def test_character_age():
    """When called, :attr:`Character.age` returns the Unicode version
    where the character was introduced.
    """
    char = c.Character('a')
    assert char.age == "1.1"


@pytest.mark.skip(reason='Slow.')
def test_character_age_all():
    """All Unicode characters should have an age."""
    for n in range(UNICODE_LEN):
        char = c.Character(n)
        char.age


@pytest.mark.skip(reason='Slow.')
def test_character_block_all():
    """All Unicode characters should have a block."""
    for n in range(UNICODE_LEN):
        char = c.Character(n)
        char.block


def test_character_code_point():
    """When called, :attr:`Character.code_point` returns the Unicode
    code point for the character.
    """
    char = c.Character('<')
    assert char.code_point == 'U+003C'


def test_character_encode():
    """When called with a valid character encoding,
    :meth:`Character.is_normal` returns a hexadecimal string
    of the encoded form of the character.
    """
    char = c.Character('å')
    assert char.encode('utf8') == 'C3 A5'


def test_character_escape_url():
    """When called with a valid character escaping scheme,
    :meth:`Character.escape` returns a string of the escaped
    form of the character.
    """
    # Percent encoding for URLs.
    char = c.Character('å')
    assert char.escape('url', 'utf8') == '%C3%A5'


def test_character_escape_html():
    """When called with a valid character escaping scheme,
    :meth:`Character.escape` returns a string of the escaped
    form of the character.
    """
    # Percent encoding for URLs.
    char = c.Character('å')
    assert char.escape('html') == '&aring;'


def test_character_is_normal():
    """When called with a valid normalization form,
    :meth:`Character.is_normal` returns whether the value
    is normalized for that form.
    """
    char = c.Character('a')
    assert char.is_normal('NFC')

    char = c.Character('å')
    assert not char.is_normal('NFD')


def test_character_normalize():
    """When given a normalization form, :meth:`Character.normalize` should
    return the normalized form of the character.
    """
    char = c.Character('å')
    assert char.normalize('NFD') == b'a\xcc\x8a'.decode('utf8')


def test_character_repr():
    """When called, :meth:`Character.__repr__` returns the Unicode code
    point and name for the code point.
    """
    char = c.Character('a')
    assert repr(char) == 'U+0061 (LATIN SMALL LETTER A)'


def test_character_denormalize():
    """When given a normalization form, :meth:`Character.reverse_normalize`
    should return the normalized form of the character.
    """
    exp = ("\uf907", "\uf908", "\uface")
    char = c.Character('\u9f9c')
    assert char.denormalize('nfc') == exp


@pytest.mark.skip(reason='Slow.')
def test_character_script_all():
    """All Unicode characters should have a script."""
    for n in range(UNICODE_LEN):
        char = c.Character(n)
        char.script


def test_character_summarize():
    """When called, :meth:`Character.summarize` returns a summary of the
    character's information as a :class:`str`.
    """
    exp = 'a U+0061 (LATIN SMALL LETTER A)'
    char = c.Character('a')
    assert char.summarize() == exp


# Test Lookup.
def test_lookup_init_set_source():
    """Given a key for a data file, an instance of Lookup should be
    created with the data file loaded.
    """
    exp_source = 'rev_nfc'
    with open(f'charex/data/{exp_source}.json') as fh:
        data = json.load(fh)
        exp_data = {k: tuple(data[k]) for k in data}
    act = c.Lookup(exp_source)
    assert act.source == exp_source
    assert act.data == exp_data


def test_lookup_query():
    """Given a string, :meth:`Lookup.query` should return the value
    for that string from the loaded data.
    """
    exp = ("\uf907", "\uf908", "\uface")
    key = '\u9f9c'
    lkp = c.Lookup('rev_nfc')
    act = lkp.query(key)
    assert act == exp

    # If key is not present in the data, return an empty tuple.
    key = 'a'
    assert lkp.query(key) == ()
