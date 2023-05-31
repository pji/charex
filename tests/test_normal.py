"""
test_normal
~~~~~~~~~~~

Unit testing for :mod:`charex.normal`.
"""
from charex import normal as nl


# Tests for form_casefold().
def test_form_casefold():
    """Given a base string, :class:`charex.normal.form_casefold` should
    return the base string normalized with the casefold form.
    """
    exp = 'a'
    base = 'A'
    assert nl.form_casefold(base) == exp


# Tests for form_nfc().
def test_form_nfc():
    """Given a base string, :class:`charex.normal.form_nfc` should
    return the base string normalized with the NFC form.
    """
    exp = 'é'
    base = '\u0065\u0301'
    assert nl.form_nfc(base) == exp


def test_form_nfd():
    """Given a base string, :class:`charex.normal.form_nfd` should
    return the base string normalized with the NFD form.
    """
    exp = '\u0065\u0301'
    base = 'é'
    assert nl.form_nfd(base) == exp


# Tests for form_nfkc().
def test_form_nfkd():
    """Given a base string, :class:`charex.normal.form_nfkc` should
    return the base string normalized with the NFKC form.
    """
    exp = 'A'
    base = '\u24b6'
    assert nl.form_nfkc(base) == exp


# Tests for form_nfkd().
def test_form_nfkd():
    """Given a base string, :class:`charex.normal.form_nfkd` should
    return the base string normalized with the NFKD form.
    """
    exp = 'A'
    base = '\u24b6'
    assert nl.form_nfkd(base) == exp


# Tests for get_description().
def test_get_description():
    """Given the key for an escape scheme,
    :func:`charex.normal.get_description` should
    return the first paragraph of the docstring of
    that scheme.
    """
    # Expected value.
    exp = 'Eggs bacon.'

    # Test set up.
    @nl.reg_form('__test_get_description')
    def form_spam(char, codec):
        """Eggs bacon.

        Ham and toast.
        """
        return char

    # Run test and determine result.
    assert nl.get_description('__test_get_description') == exp

    # Test clean up.
    del nl.forms['__test_get_description']


# Tests for normalize().
def test_normalize():
    """Given a normalization schem and base string, return the
    base string normalized using the normalization scheme as a
    :class:`str`.
    """
    exp = 'A'
    scheme = 'nfkc'
    base = '\u24b6'
    assert nl.normalize(scheme, base) == exp


# Tests for build_denormalization_map().
def test_build_denormalization_map():
    """When given the key for a denormalization function,
    :func:`charex.normal.build_denormalization_map` will return a map
    of every character that normalizes into a character as a
    JSON string.
    """
    with open('charex/data/rev_nfc.json') as fh:
        exp = fh.read()
    form = 'nfc'
    act = nl.build_denormalization_map(form)
    alines = act.split('\n')
    elines = exp.split('\n')
    for i, lines in enumerate(zip(alines, elines)):
        a, e = lines
        assert (i, a) == (i, e)
    assert act == exp


# Tests for find_max_decomposition().
def test_find_max_decomposition():
    """When called, :func:`charex.normal.find_max_decomposition` finds
    the character that decomposes into the largest string, then returns
    that character and the length of the string it decomposes into as
    a tuple.
    """
    exp = ('ᾂ', 4)
    assert nl.find_max_decomposition() == exp
