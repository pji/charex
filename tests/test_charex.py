"""
test_charex
~~~~~~~~~~~
"""
import json

import pytest

from charex import charex as c
from charex import db


# Global constants.
UNICODE_LEN = 0x110000


# Utility functions.
def raises_exception(char, attr, ex):
    with pytest.raises(ex):
        getattr(char, attr)


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


def test_character_dictlike_properties():
    """A :class:`charex.Character` should have the properties from the
    Unihan Dictionary-Like Data database.
    """
    char = c.Character('a')
    assert char.kcangjie == ''
    assert char.kstrange == ''
    assert char.kphonetic == ''
    assert char.kfenn == ''
    assert char.kunihancore2020 == ''
    assert char.kcheungbauer == ''
    assert char.kfourcornercode == ''
    assert char.kfrequency == ''
    assert char.kgradelevel == ''
    assert char.khdzradbreak == ''
    assert char.khkglyph == ''

    if db.cache.version in ['v15_0', 'v15_1',]:
        assert char.kalternatetotalstrokes == ''
    else:
        assert char.kcihait == ''

    if db.cache.version in ['v15_1',]:
        assert char.kmojijoho == ''


def test_character_dindices_properties():
    """A :class:`charex.Character` should have the properties from the
    Unihan Dictionary Indices database.
    """
    char = c.Character('a')
    assert char.khanyu == ''
    assert char.kirgkangxi == ''
    assert char.kirghanyudazidian == ''
    assert char.ksbgy == ''
    assert char.knelson == ''
    assert char.kcowles == ''
    assert char.kmatthews == ''
    assert char.kgsr == ''
    assert char.kkangxi == ''
    assert char.kfennindex == ''
    assert char.kkarlgren == ''
    assert char.kmeyerwempe == ''
    assert char.klau == ''
    assert char.kcheungbauerindex == ''
    assert char.kmorohashi == ''
    assert char.kdaejaweon == ''
    assert char.kirgdaejaweon == ''

    if db.cache.version in ['v15_0', 'v15_1',]:
        assert char.kcihait == ''

    if db.cache.version in ['v15_1',]:
        raises_exception(char, 'kirgdaikanwaziten', KeyError)
        assert char.ksmszd2003index == ''
    else:
        assert char.kirgdaikanwaziten == ''

    char = c.Character('U+3402')
    assert char.khanyu == ''
    assert char.kirgkangxi == '0078.101'
    assert char.kirghanyudazidian == ''
    assert char.ksbgy == ''
    assert char.knelson == '0265'
    assert char.kcowles == ''
    assert char.kmatthews == ''
    assert char.kgsr == ''
    assert char.kfennindex == ''
    assert char.kkarlgren == ''
    assert char.kmeyerwempe == ''
    assert char.klau == ''
    assert char.kcheungbauerindex == ''
    assert char.kdaejaweon == ''
    assert char.kirgdaejaweon == ''

    if db.cache.version in ['v15_0', 'v15_1',]:
        assert char.kcihait == ''
        assert char.kkangxi == '0078.101'
    else:
        assert char.kkangxi == ''

    if db.cache.version in ['v15_1',]:
        raises_exception(char, 'kirgdaikanwaziten', KeyError)
        assert char.kmorohashi == 'H001'
        assert char.ksmszd2003index == ''
    else:
        assert char.kirgdaikanwaziten == ''
        assert char.kmorohashi == ''


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


def test_character_idna2008_properties():
    """A :class:`charex.Character` should have the properties from the
    Idna2008 data file.
    """
    char = c.Character('a')
    assert char.idna2008 == 'PVALID'


def test_character_irgsource_properties():
    """A :class:`charex.Character` should have the properties from the
    Unicode data database.
    """
    char = c.Character('a')
    assert char.cjkirg_gsource == ''
    assert char.cjkirg_jsource == ''
    assert char.cjkirg_tsource == ''
    assert char.cjkrsunicode == ''
    assert char.ktotalstrokes == ''
    assert char.cjkirg_ksource == ''
    assert char.cjkirg_kpsource == ''
    assert char.cjkirg_vsource == ''
    assert char.cjkirg_hsource == ''
    assert char.cjkirg_usource == ''
    assert char.cjkiicore == ''
    assert char.cjkirg_msource == ''
    assert char.cjkirg_uksource == ''
    assert char.cjkcompatibilityvariant == ''
    assert char.cjkirg_ssource == ''

    char = c.Character('U+31026')
    assert char.cjkirg_gsource == 'GHZR-74462.01'
    assert char.cjkirg_jsource == ''
    assert char.cjkirg_tsource == ''
    assert char.cjkrsunicode == '170.9'
    assert char.ktotalstrokes == '12'
    assert char.cjkirg_ksource == ''
    assert char.cjkirg_kpsource == ''
    assert char.cjkirg_vsource == ''
    assert char.cjkirg_hsource == ''
    assert char.cjkirg_usource == ''
    assert char.cjkiicore == ''
    assert char.cjkirg_msource == ''
    assert char.cjkirg_uksource == ''
    assert char.cjkcompatibilityvariant == ''
    assert char.cjkirg_ssource == ''


def test_character_mappings_properties():
    """A :class:`charex.Character` should have the properties from the
    Unihan Other Mappings database.
    """
    char = c.Character('a')
    assert char.kjis0213 == ''
    assert char.ktgh == ''
    assert char.kkoreanname == ''
    assert char.keacc == ''
    assert char.ktaiwantelegraph == ''
    assert char.kja == ''
    assert char.kbigfive == ''
    assert char.kcccii == ''
    assert char.kcns1986 == ''
    assert char.kcns1992 == ''
    assert char.kgb0 == ''
    assert char.kgb1 == ''
    assert char.kjis0 == ''
    assert char.kjoyokanji == ''
    assert char.kkoreaneducationhanja == ''
    assert char.kmainlandtelegraph == ''
    assert char.kxerox == ''
    assert char.kgb5 == ''
    assert char.kjis1 == ''
    assert char.kpseudogb1 == ''
    assert char.kgb3 == ''
    assert char.kgb8 == ''
    assert char.kjinmeiyokanji == ''
    assert char.kibmjapan == ''
    assert char.kgb7 == ''

    if db.cache.version in ['v15_1',]:
        raises_exception(char, 'kkps0', KeyError)
        raises_exception(char, 'kkps1', KeyError)
        raises_exception(char, 'kksc0', KeyError)
        raises_exception(char, 'kksc1', KeyError)
        raises_exception(char, 'khkscs', KeyError)
    else:
        assert char.kkps0 == ''
        assert char.kkps1 == ''
        assert char.kksc0 == ''
        assert char.kksc1 == ''
        assert char.khkscs == ''


def test_character_multilist_properties():
    """A :class:`charex.Character` should have the properties from
    defined properties that contain multiple values.
    """
    char = c.Character('a')
    assert char.scx == 'Latn'


def test_character_numvalues_properties():
    """A :class:`charex.Character` should have the properties from the
    Unihan Numeric Values database.
    """
    char = c.Character('a')
    assert char.cjkothernumeric == ''
    assert char.cjkprimarynumeric == ''
    assert char.cjkaccountingnumeric == ''

    if db.cache.version in ['v15_1',]:
        assert char.kvietnamesenumeric == ''
        assert char.kzhuangnumeric == ''

    char = c.Character('U+4E07')
    assert char.cjkothernumeric == ''
    assert char.cjkprimarynumeric == '10000'
    assert char.cjkaccountingnumeric == ''

    if db.cache.version in ['v15_1',]:
        assert char.kvietnamesenumeric == ''
        assert char.kzhuangnumeric == ''


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

    if db.cache.version in ['v15_1',]:
        assert char.idsu == 'N'

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


def test_character_radstroke_properties():
    """A :class:`charex.Character` should have the properties from the
    Unihan Radical Stroke Counts database.
    """
    char = c.Character('a')
    assert char.krsadobe_japan1_6 == ''

    if db.cache.version in ['v15_1',]:
        raises_exception(char, 'krskangxi', KeyError)
    else:
        assert char.krskangxi == ''

    char = c.Character('U+3427')
    assert char.krsadobe_japan1_6 == 'C+13910+3.1.3 C+13910+6.1.3'

    if db.cache.version in ['v15_1',]:
        raises_exception(char, 'krskangxi', KeyError)
    else:
        assert char.krskangxi == ''

    char = c.Character('U+3687')
    assert char.krsadobe_japan1_6 == ''

    if db.cache.version in ['v15_1',]:
        raises_exception(char, 'krskangxi', KeyError)
    else:
        assert char.krskangxi == '35.6'


def test_character_readings_properties():
    """A :class:`charex.Character` should have the properties from the
    Unihan Readings database.
    """
    char = c.Character('a')
    assert char.kcantonese == ''
    assert char.kdefinition == ''
    assert char.kmandarin == ''
    assert char.khanyupinyin == ''
    assert char.ktghz2013 == ''
    assert char.kxhc1983 == ''
    assert char.kvietnamese == ''
    assert char.khangul == ''
    assert char.ktang == ''
    assert char.kjapanesekun == ''
    assert char.kjapaneseon == ''
    assert char.khanyupinlu == ''
    assert char.kkorean == ''

    if db.cache.version in ['v15_1',]:
        assert char.kjapanese == ''
        assert char.ksmszd2003readings == ''

    char = c.Character('U+3404')
    assert char.kcantonese == 'kwaa1'
    assert char.kdefinition == ''
    assert char.kmandarin == 'kuà'
    assert char.khanyupinyin == ''
    assert char.ktghz2013 == ''
    assert char.kxhc1983 == ''
    assert char.kvietnamese == ''
    assert char.khangul == ''
    assert char.ktang == ''
    assert char.kjapanesekun == ''
    assert char.kjapaneseon == ''
    assert char.khanyupinlu == ''
    assert char.kkorean == ''

    if db.cache.version in ['v15_1',]:
        assert char.kjapanese == 'カ ケ'
        assert char.ksmszd2003readings == ''


def test_character_rangelist_properties():
    """A :class:`charex.Character` should have the properties from
    defined range lists.
    """
    char = c.Character('a')
    assert char.age == '1.1'
    assert char.blk == 'Basic Latin'
    assert char.sc == 'Latn'


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


def test_character_variants_properties():
    """A :class:`charex.Character` should have the properties from the
    Unihan Variants database.
    """
    char = c.Character('a')
    assert char.ksemanticvariant == ''
    assert char.kspoofingvariant == ''
    assert char.ktraditionalvariant == ''
    assert char.ksimplifiedvariant == ''
    assert char.kspecializedsemanticvariant == ''
    assert char.kzvariant == ''

    char = c.Character('U+3431')
    assert char.ksemanticvariant == 'U+9B12<kMatthews'
    assert char.kspoofingvariant == ''
    assert char.ktraditionalvariant == ''
    assert char.ksimplifiedvariant == ''
    assert char.kspecializedsemanticvariant == ''
    assert char.kzvariant == ''


def test_character_speccase():
    """A :class:`charex.Character` should have the properties from the
    SpecialCasing.txt file.
    """
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


def test_character_na():
    """When called, :attr:`Character.na` should return the correct name
    for the character.
    """
    char = c.Character('a')
    assert char.na == 'LATIN SMALL LETTER A'

    # Rule NR2.
    char = c.Character('U+20002')
    assert char.na == 'CJK UNIFIED IDEOGRAPH-20002'

    # Rule NR1.
    char = c.Character('U+D4DB')
    assert char.na == 'HANGUL SYLLABLE PWILH'


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


# Test utility functions.
def test_validate_normalization_form_valid():
    """Given a :class:`str` that is a valid normalization form,
    :func:`validate_normalization_form` should return that form.
    """
    exp = 'NFC'
    assert exp == c.validate_normalization_form(exp)


def test_validate_normalization_form_lower_case():
    """Given a :class:`str` that is a valid normalization form,
    :func:`validate_normalization_form` should return that form.
    """
    exp = 'NFC'
    assert exp == c.validate_normalization_form(exp.lower())


def test_validate_normalization_invalid():
    """Given a :class:`str` that is a valid normalization form,
    :func:`validate_normalization_form` should return that form.
    """
    exp = c.InvalidNormalizationFormError
    with pytest.raises(exp):
        _ = c.validate_normalization_form('spam')
