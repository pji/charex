"""
__main__
~~~~~~~~

Mainline for :mod:`charex`.
"""
from argparse import ArgumentParser, Namespace, _SubParsersAction
import unicodedata as ucd

from charex import charsets as cs
from charex.charex import Character, Transformer
from charex.denormal import count_denormalizations, denormalize
from charex.util import bin2bytes, hex2bytes


# Utility functions.
def neutralize_control_characters(value: str) -> str:
    """Transform a control character into the symbol for that character."""
    result = ''
    for c in value:
        if ucd.category(c) == 'Cc':
            num = ord(c)
            result += chr(num + 0x2400)
        else:
            result += c
    return result


# Running modes.
def mode_charset(args: Namespace) -> None:
    if args.binary:
        base = bin2bytes(args.base)
    else:
        base = hex2bytes(args.base)

    results = cs.multiencode(base, (codec for codec in cs.codecs))
    width = max(len(k) for k in cs.codecs)
    for key in results:
        if results[key]:
            c = results[key]
            details = ''
            if len(c) > 1:
                details = '*** multiple characters ***'
            else:
                char = Character(c)
                details = f'{char.code_point} {char.name}'
            c = neutralize_control_characters(c)
            print(f'{key:>{width}}: {c} {details}')
    print()


def mode_denormal(args: Namespace) -> None:
    if args.count:
        count = count_denormalizations(args.base, args.form, args.maxdepth)
        print(f'{count:,}')

    else:
        results = denormalize(args.base, args.form, args.maxdepth)
        for result in results:
            print(result)
        print()


def mode_details(args: Namespace) -> None:
    def rev_normalize(char: Character, form: str) -> str:
        points = char.reverse_normalize(form)
        chars = (Character(point) for point in points)
        values = [f'{c.value} {c.code_point} ({c.name})' for c in chars]
        if not values:
            return ''
        return ('\n' + ' ' * 22).join(v for v in values)

    char = Character(args.codepoint)

    width = 20
    details = (
        ('display', char.value),
        ('name', char.name),
        ('code_point', char.code_point),
        ('category', char.category),
        ('uft-8', char.encode('utf8')),
        ('uft-16 BE', char.encode('utf_16_be')),
        ('uft-16 LE', char.encode('utf_16_le')),
        ('uft-32 BE', char.encode('utf_32_be')),
        ('uft-32 LE', char.encode('utf_32_le')),
        ('decomposition', char.decomposition),
        ('url encoded', char.escape('url')),
        ('html encoded', char.escape('html')),
        ('reverse nfc', rev_normalize(char, 'nfc')),
        ('reverse nfd', rev_normalize(char, 'nfd')),
        ('reverse nfkc', rev_normalize(char, 'nfkc')),
        ('reverse nfkd', rev_normalize(char, 'nfkd')),
    )

    for detail in details:
        label, value = detail
        if value:
            print(f'{label:>{width}}: {value}')
    print()


# Command parsing.
def parse_charset(spa: _SubParsersAction) -> None:
    """Add the charset mode subparser."""
    sp = spa.add_parser(
        'charset',
        aliases=['cset',],
        help=(
            'Show the characters the integer could be in different '
            'characer sets.'
        )
    )
    sp.add_argument(
        'base',
        help='The base integer. Defaults to being read as hex.',
        action='store',
        type=str
    )
    sp.add_argument(
        '--binary', '-b',
        help='Interpret the base integer as binary rather than hex.',
        action='store_true'
    )
    sp.set_defaults(func=mode_charset)


def parse_denormal(spa: _SubParsersAction) -> None:
    """Add the denormal mode subparser."""
    sp = spa.add_parser(
        'denormal',
        aliases=['n',],
        help='Generate strings that normalize to the given string.'
    )
    sp.add_argument(
        'base',
        help='The base normalized string.',
        action='store',
        type=str
    )
    sp.add_argument(
        '--count', '-c',
        help='Count the total number of denormalizations.',
        action='store_true'
    )
    sp.add_argument(
        '--form', '-f',
        help='Normalization form.',
        default='nfkd',
        action='store',
        type=str
    )
    sp.add_argument(
        '--maxdepth', '-m',
        help=(
            'Maximum number of reverse normalizations to use '
            'for each character.'
        ),
        default=0,
        action='store',
        type=int
    )
    sp.set_defaults(func=mode_denormal)


def parse_details(spa: _SubParsersAction) -> None:
    """Add the details mode subparser."""
    sp = spa.add_parser(
        'details',
        aliases=['d', 'deets'],
        help='Display the details for the given code point.'
    )
    sp.add_argument(
        'codepoint',
        help='The code point.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_details)


def parse_invocation() -> None:
    # Build argument parser.
    p = ArgumentParser(
        description='Unicode and character set explorer.',
        prog='charex'
    )

    # Build subparser for each mode.
    spa = p.add_subparsers(required=True)
    parse_charset(spa)
    parse_denormal(spa)
    parse_details(spa)

    # Execute.
    args = p.parse_args()
    args.func(args)


# Mainline.
if __name__ == '__main__':
    parse_invocation()
