"""
cmds
~~~~

Core logic for the different commands/modes of :mod:`charex`.
"""
from collections.abc import Callable, Generator, Sequence
from functools import partial
from itertools import zip_longest
from textwrap import wrap

from charex import charex as ch
from charex import charsets as cset
from charex import denormal as dnm
from charex import escape as esc
from charex import normal as nml
from charex import util


# Command functions.
def cd(address: str) -> Generator[str, None, None]:
    """Decode the given address in all codecs.

    :param address: The address to decode in the codecs.
    :return: Yields the result for each codec as a :class:`str`.
    :rtype: str
    """
    # Get the data.
    codecs = cset.get_codecs()
    results = cset.multidecode(address, (codec for codec in codecs))

    # Write the output.
    width = max(len(codec) for codec in codecs)
    for key in results:
        c = results[key]
        details = ''
        if len(c) < 1:
            details = '*** no character ***'
        elif len(c) > 1:
            details = '*** multiple characters ***'
        else:
            char = ch.Character(c)
            details = f'{char.code_point} {char.name}'
        c = util.neutralize_control_characters(c)
        yield f'{key:>{width}}: {c} {details}'


def ce(base: str) -> Generator[str, None, None]:
    """Encode the given character in all codecs.

    :param address: The character to encode in the codecs.
    :return: Yields the result for each codec as a :class:`str`.
    :rtype: str
    """
    # Get the data.
    codecs = cset.get_codecs()
    results = cset.multiencode(base, (codec for codec in codecs))

    # Write the output.
    width = max(len(codec) for codec in codecs)
    for key in results:
        if b := results[key]:
            c = ' '.join(f'{n:>02x}'.upper() for n in b)
            yield f'{key:>{width}}: {c}'


def cl(show_descr: bool = False) -> Generator[str, None, None]:
    """List registered character sets.

    :param show_descr: (Optional.) Whether to show the descriptions
        for the character sets.
    :return: Yields each codec as a :class:`str`.
    :rtype: str
    """
    codecs = cset.get_codecs()
    for line in write_list(codecs, cset.get_description, show_descr):
        yield line


def ct(base: str, form: str, maxdepth: int, number: int = 0) -> str:
    """Count denormalization results.

    :param base: The base normalized string.
    :param form: The Unicode normalization form for the denormalization.
    :param maxdepth: Maximum number of reverse normalizations to use
        for each character.
    :param number: (Optional.) The number of denormalizations to return.
    :return: The number of denormalizations as a :class:`str`
    :rtype: str
    """
    if number:
        return f'{number:,}'
    count = dnm.count_denormalizations(base, form, maxdepth)
    return f'{count:,}'


def dn(
    base: str,
    form: str,
    maxdepth: int,
    random: bool,
    seed: bytes | int | str
) -> Generator[str, None, None]:
    """Perform denormalizations.

    :param base: The base normalized string.
    :param form: The normalization form for the denormalization.
    :param maxdepth: If not random, sets the maximum number of
        denormalizations to use for each character. If random, sets
        the number of random denormalizations to return.
    :param random: Randomize the denormalization.
    :param seed: Seed the randomized denormalization.
    :return: Yields each codec as a :class:`str`.
    :rtype: str
    """
    if not random:
        for result in dnm.gen_denormalize(base, form, maxdepth):
            yield result

    else:
        if not maxdepth:
            maxdepth = 1
        for result in dnm.gen_random_denormalize(
            base,
            form,
            maxdepth,
            seed
        ):
            yield result


def dt(c: str) -> Generator[str, None, None]:
    """Display details for a code point.

    :param address: The character to encode in the codecs.
    :return: Yields the result for each codec as a :class:`str`.
    :rtype: str
    """
    def rev_normalize(char: ch.Character, form: str) -> str:
        points = char.denormalize(form)
        values = []
        for point in points:
            if len(point) == 1:
                c = ch.Character(point)
                values.append(c.summarize())
            elif len(point) > 1:
                values.append(f'{point} *** multiple characters ***')
                for item in point:
                    char = ch.Character(item)
                    values.append('  ' + char.summarize())
        if not values:
            return ''
        return ('\n' + ' ' * 22).join(v for v in values)

    # Gather the details for display.
    char = ch.Character(c)
    details = (
        ('Display', char.value),
        ('Code Point', char.code_point),
        ('Name', char.na),
        ('Age', char.age),
        ('Block', char.block),
        ('Category', char.category),
        ('Canonical Combining', char.ccc),
        ('Bidi Class', char.bc),
        ('Decomposition Type', char.dt),
        ('Decomposition', char.dm),
        ('Decimal', char.decimal),
        ('Digit', char.digit),
        ('Numeric', char.nv),
        ('Bidi Mirrored', char.bidi_m),
        ('Unicode 1 Name', char.na1),
        ('ISO Comment', char.isc),
        ('Uppercase', char.suc),
        ('Lowercase', char.slc),
        ('Titlecase', char.stc),
        ('Script', char.sc),
        ('Script Extensions', char.scx),
        ('White Space', char.wspace),
        ('Alphabetical', char.alpha),
        ('Hangul Syllable Type', char.hst),
        ('Other Ignorable', char.odi),
        ('UTF-8', char.encode('utf8')),
        ('UTF-16', char.encode('utf_16_be')),
        ('UTF-32', char.encode('utf_32_be')),
        ('C encoded', char.escape('c')),
        ('URL encoded', char.escape('url')),
        ('HTML encoded', char.escape('html')),
        ('Reverse Cfold', rev_normalize(char, 'casefold')),
        ('Reverse NFC', rev_normalize(char, 'nfc')),
        ('Reverse NFD', rev_normalize(char, 'nfd')),
        ('Reverse NFKC', rev_normalize(char, 'nfkc')),
        ('Reverse NFKD', rev_normalize(char, 'nfkd')),
    )

    # Display the details.
    width = 20
    for detail in details:
        label, value = detail
        if value:
            yield f'{label:>{width}}: {value}'


def el(show_descr: bool = False) -> Generator[str, None, None]:
    """List registered escape schemes.

    :param show_descr: (Optional.) Whether to show the descriptions
        for the character sets.
    :return: Yields each codec as a :class:`str`.
    :rtype: str
    """
    schemes = esc.get_schemes()
    for line in write_list(schemes, esc.get_description, show_descr):
        yield line


def es(base: str, scheme: str, codec: str) -> str:
    """Escape a string using the given scheme.

    :param base: The string to escape.
    :param scheme: The key in the `schemes` :class:`dict` to use for
        the escaping.
    :param codec: The character set codec to use when escaping the
        characters.
    :return: The escaped :class:`str`.
    :rtype: str
    """
    return esc.escape(base, scheme, codec)


def fl(show_descr: bool = False) -> Generator[str, None, None]:
    """List registered normalization forms.

    :param show_descr: (Optional.) Whether to show the descriptions
        for the character sets.
    :return: Yields each form as a :class:`str`.
    :rtype: str
    """
    forms = nml.get_forms()
    for line in write_list(forms, nml.get_description, show_descr):
        yield line


def nl(form: str, base: str, expand: bool = False) -> str:
    """Perform normalizations.

    :param form: The key of a registered normalization form.
    :param base: The string to normalize.
    :param expand: (Optional.) Whether to provide a summary of each
        character in the normalization.
    :return: The normalized :class:`str`.
    :rtype: str
    """
    result = nml.normalize(form, base)
    out = result
    if expand:
        out += '\n'
        for item in result:
            char = ch.Character(item)
            indent = '  '
            if 'mark' in char.category.casefold():
                indent += ' '
            out += f'  {char.summarize()}\n'
    return out


def up(show_long: bool = False) -> Generator[str, None, None]:
    """List the Unicode properties.

    :param show_long: (Optional.) Whether to show the long name.
    :return: Yields each property as a :class:`str`.
    :rtype: str
    """
    props = ch.get_properties()
    for line in write_list(props, ch.expand_property, show_long):
        yield line


def uv(prop: str, show_long: bool = False) -> Generator[str, None, None]:
    """List the valid values for a Unicode property.

    :param prop: The Unicode property.
    :param show_long: (Optional.) Whether to show the long name.
    :return: Yields each property as a :class:`str`.
    :rtype: str
    """
    values = ch.get_property_values(prop)
    expand_value = partial(ch.expand_property_value, prop)
    for line in write_list(values, expand_value, show_long):
        yield line


# Utility functions.
def make_description_row(name: str, namewidth: int, descr: str) -> str:
    """Create a two column row with a name and description.

    :param name: The content for the first column.
    :param namewidth: The width of the first column.
    :param descr: The content for the second column.
    :return: The row as a :class:`str`.
    :rtype: str
    """
    name_lines = wrap(name, namewidth)
    descr_lines = wrap(descr, 77 - namewidth)
    lines = (
        f'{n:<{namewidth}}  {d}'
        for n, d in zip_longest(name_lines, descr_lines, fillvalue='')
    )
    return '\n'.join(lines)


def write_list(
    items: Sequence[str],
    get_descr: Callable[[str], str],
    show_descr: bool
) -> Generator[str, None, None]:
    """Output the given list.

    :param items: The items to list.
    :param get_descr: The function used to look up the discription
        of each item.
    :param show_descr: Whether include the descriptions of each item
        in the output.
    :return: Yields each codec as a :class:`str`.
    :rtype: str
    """
    if not items:
        items = ('No values.',)
        show_descr = False
    width = max(len(item) for item in items)
    for item in items:
        if show_descr:
            descr = get_descr(item)
            row = make_description_row(item, width, descr)
            yield row
        else:
            yield item
