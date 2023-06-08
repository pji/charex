"""
test_charex
~~~~~~~~~~~
"""
import json

import pytest

from charex import charex as c


# Global constants.
UNICODE_LEN = 0x110000


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


def test_character_derived_normalization_properties():
    """A :class:`charex.Character` should have the properties from
    DerivedNormalizationProperties.txt.
    """
    char = c.Character('a')

    # Single value properties.
    assert char.fc_nfkc == ''
    assert char.nfd_qc == 'Y'
    assert char.nfc_qc == 'Y'
    assert char.nfkd_qc == 'Y'
    assert char.nfkc_qc == 'Y'
    assert char.nfkc_cf == '0061'

    # Simple list properties.
    assert char.comp_ex == 'N'
    assert char.xo_nfd == 'N'
    assert char.xo_nfc == 'N'
    assert char.xo_nfkd == 'N'
    assert char.xo_nfkc == 'N'
    assert char.cwkcf == 'N'

    char = c.Character('U+037a')
    assert char.fc_nfkc == '0020 03B9'

    char = c.Character('U+095a')
    assert char.comp_ex == 'Y'

    # Singleton decomposition.
    char = c.Character('U+0374')
    assert char.comp_ex == 'Y'

    # Non-starter decomposition.
    char = c.Character('U+0344')
    assert char.comp_ex == 'Y'


def test_character_emoji_properties():
    """A :class:`charex.Character` should have the properties from
    emoji-data.txt.
    """
    char = c.Character('U+1F600')
    assert char.emoji == 'Y'
    assert char.epres == 'Y'
    assert char.emod == 'N'
    assert char.ebase == 'N'
    assert char.ecomp == 'N'
    assert char.extpict == 'Y'


def test_character_proplist_properties():
    """A :class:`charex.Character` should have the properties from
    PropList.txt.
    """
    char = c.Character('a')
    assert char.wspace == 'N'
    assert char.bidi_c == 'N'
    assert char.join_c == 'N'
    assert char.dash == 'N'
    assert char.hyphen == 'N'
    assert char.qmark == 'N'
    assert char.term == 'N'
    assert char.omath == 'N'
    assert char.hex is 'Y'
    assert char.ahex is 'Y'
    assert char.oalpha == 'N'
    assert char.ideo == 'N'
    assert char.dia == 'N'
    assert char.ext == 'N'
    assert char.olower == 'N'
    assert char.oupper == 'N'
    assert char.nchar == 'N'
    assert char.ogr_ext == 'N'
    assert char.idsb == 'N'
    assert char.idst == 'N'
    assert char.radical == 'N'
    assert char.uideo == 'N'
    assert char.odi == 'N'
    assert char.dep == 'N'
    assert char.sd == 'N'
    assert char.loe == 'N'
    assert char.oids == 'N'
    assert char.oidc == 'N'
    assert char.sterm == 'N'
    assert char.vs == 'N'
    assert char.pat_ws == 'N'
    assert char.pat_syn == 'N'
    assert char.pcm == 'N'
    assert char.ri == 'N'

    # DerivedCoreProperties.
    assert char.lower == 'Y'
    assert char.upper == 'N'
    assert char.cased == 'Y'
    assert char.ci == 'N'
    assert char.cwl == 'N'
    assert char.cwt == 'Y'
    assert char.cwu == 'Y'
    assert char.cwcf == 'N'
    assert char.cwcm == 'Y'
    assert char.alpha == 'Y'
    assert char.di == 'N'
    assert char.gr_base == 'Y'
    assert char.gr_ext == 'N'
    assert char.gr_link == 'N'
    assert char.math == 'N'
    assert char.ids == 'Y'
    assert char.idc == 'Y'
    assert char.xids == 'Y'
    assert char.xidc == 'Y'


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


def test_character_simplelist_properties():
    """A :class:`charex.Character` should have the properties from
    the simple lists.
    """
    char = c.Character('a')
    assert char.ce == 'N'

    char = c.Character('U+0958')
    assert char.ce == 'Y'


def test_character_singleval_properties():
    """A :class:`charex.Character` should have the properties from
    the single value lists.
    """
    char = c.Character('a')
    assert char.bmg == '<none>'
    assert char.ea == 'Na'
    assert char.equideo == '<none>'
    assert char.hst == 'NA'
    assert char.inpc == 'NA'
    assert char.insc == 'Other'
    assert char.jsn == ''
    assert char.jg == 'No_Joining_Group'
    assert char.jt == 'U'
    assert char.lb == 'AL'
    assert char.gcb == 'XX'
    assert char.sb == 'LO'
    assert char.vo == 'R'
    assert char.wb == 'LE'


def test_character_speccase():
    """A :class:`charex.Character` should have the properties from the
    SpecialCasing.txt file.
    """
    char = c.Character('a')
    assert char.lc == '0061'
    assert char.tc == '0041'
    assert char.uc == '0041'

    char = c.Character('U+FB00')
    assert char.lc == 'FB00'
    assert char.tc == '0046 0066'
    assert char.uc == '0046 0046'


def test_character_derived_bpt():
    """When called, :attr:`charex.Character.bpt` should derive and return
    the alias for the bidi paired bracket type for the character.
    """
    char = c.Character('a')
    assert char.bpt == 'n'

    char = c.Character('(')
    assert char.bpt == 'o'

    char = c.Character(')')
    assert char.bpt == 'c'


def test_character_derived_bpb():
    """When called, :attr:`charex.Character.bpb` should derive and return
    the alias for the bidi paired bracket for the character.
    """
    char = c.Character('a')
    assert char.bpb == '<none>'

    char = c.Character('(')
    assert char.bpb == '0029'

    char = c.Character(')')
    assert char.bpb == '0028'


def test_character_cf():
    """When called, :attr:`charex.Character.cf` should return the
    `Case_Folding` attribute for the character.
    """
    char = c.Character('a')
    assert char.cf == '0061'

    char = c.Character('U+1E9E')
    assert char.cf == '0073 0073'


def test_character_scf():
    """When called, :attr:`charex.Character.scf` should return the
    `Simple_Case_Folding` attribute for the character.
    """
    char = c.Character('a')
    assert char.scf == '0061'

    char = c.Character('U+1E9E')
    assert char.scf == '00DF'


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


@pytest.mark.skip(reason='Slow.')
def test_character_script_all():
    """All Unicode characters should have a script."""
    for n in range(UNICODE_LEN):
        char = c.Character(n)
        char.script


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


def test_character_summarize():
    """When called, :meth:`Character.summarize` returns a summary of the
    character's information as a :class:`str`.
    """
    exp = 'a U+0061 (LATIN SMALL LETTER A)'
    char = c.Character('a')
    assert char.summarize() == exp
