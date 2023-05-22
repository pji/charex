"""
cmds
~~~~

Core logic for the different commands/modes of :mod:`charex`.
"""
from collections.abc import Callable, Generator, Sequence
from itertools import zip_longest
from textwrap import wrap

from charex import charex as ch
from charex import charsets as cset
from charex import denormal as dn
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
    for line in write_list(codecs, cset.get_codec_description, show_descr):
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
    count = dn.count_denormalizations(base, form, maxdepth)
    return f'{count:,}'


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
        ('Name', char.name),
        ('Code Point', char.code_point),
        ('Category', char.category),
        ('UTF-8', char.encode('utf8')),
        ('UTF-16', char.encode('utf_16_be')),
        ('UTF-32', char.encode('utf_32_be')),
        ('Decomposition', char.decomposition),
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
    width = max(len(item) for item in items)
    for item in items:
        if show_descr:
            descr = get_descr(item)
            row = make_description_row(item, width, descr)
            yield row
        else:
            yield item
