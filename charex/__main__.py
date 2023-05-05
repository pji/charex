"""
__main__
~~~~~~~~

Mainline for command line invocations of :mod:`charex`.
"""
from argparse import ArgumentParser, Namespace, _SubParsersAction
import unicodedata as ucd

from charex import charsets as cs
from charex.charex import Character, Transformer
from charex.denormal import count_denormalizations, denormalize
from charex.util import bin2bytes, hex2bytes


# Utility functions.
def neutralize_control_characters(value: str) -> str:
    """Transform control characters in a string into the Unicode
    symbol for those characters.

    :param value: The :class:`str` to neutralize.
    :return: The neutralized :class:`str`.
    :rtype: str
    """
    def neutralize(char: str) -> str:
        if ucd.category(char) == 'Cc':
            num = ord(char)
            new = chr(num + 0x2400)
            return new
        return char

    return ''.join(neutralize(char) for char in value)


# Running modes.
def mode_charset(args: Namespace) -> None:
    """Perform character set lookups.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    def core(args: Namespace, width: int) -> None:
        """Look up characer values for address."""
        if args.binary:
            base = bin2bytes(args.base)
        elif args.character:
            base = args.base.encode(args.character)
        else:
            base = hex2bytes(args.base)
        results = cs.multidecode(base, (codec for codec in cs.codecs))

        # Write the output.
        for key in results:
            c = results[key]
            details = ''
            if len(c) < 1:
                details = '*** no character ***'
            elif len(c) > 1:
                details = '*** multiple characters ***'
            else:
                char = Character(c)
                details = f'{char.code_point} {char.name}'
            c = neutralize_control_characters(c)
            print(f'{key:>{width}}: {c} {details}')

    def reverse(args: Namespace, width: int) -> None:
        """Look up addresses for code point."""
        results = cs.multiencode(args.base, (codec for codec in cs.codecs))

        # Write the output.
        for key in results:
            if b := results[key]:
                c = ''.join(f'{n:>02x}'.upper() for n in b)
                print(f'{key:>{width}}: {c}')

    # Determine whether this is a code point or address lookup.
    width = max(len(k) for k in cs.codecs)
    if not args.reverse:
        core(args, width)
    else:
        reverse(args, width)
    print()


def mode_denormal(args: Namespace) -> None:
    """Perform denormalizations.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    # Just count the number of denormalizations.
    if args.count:
        count = count_denormalizations(args.base, args.form, args.maxdepth)
        print(f'{count:,}')

    # List all the denormalizations.
    else:
        results = denormalize(
            args.base,
            args.form,
            args.maxdepth,
            args.number,
            args.random,
            args.seed
        )
        for result in results:
            print(result)
        print()


def mode_details(args: Namespace) -> None:
    """Display details for a code point.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    def rev_normalize(char: Character, form: str) -> str:
        points = char.reverse_normalize(form)
        chars = (Character(point) for point in points)
        values = [f'{c.value} {c.code_point} ({c.name})' for c in chars]
        if not values:
            return ''
        return ('\n' + ' ' * 22).join(v for v in values)

    # Gather the details for display.
    char = Character(args.codepoint)
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

    # Display the details.
    width = 20
    for detail in details:
        label, value = detail
        if value:
            print(f'{label:>{width}}: {value}')
    print()


# Command parsing.
def parse_charset(spa: _SubParsersAction) -> None:
    """Add the charset mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
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
    sp.add_argument(
        '--character', '-c',
        help=(
            'Interpret the base integer as a character in the given '
            'character set.'
        ),
        action='store'
    )
    sp.add_argument(
        '--reverse', '-r',
        help=(
            'Show the address for the character in the different '
            'character sets.'
        ),
        action='store_true'
    )
    sp.set_defaults(func=mode_charset)


def parse_denormal(spa: _SubParsersAction) -> None:
    """Add the denormal mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
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
    sp.add_argument(
        '--number', '-n',
        help='Maximum number of results to return.',
        default=0,
        action='store',
        type=int
    )
    sp.add_argument(
        '--random', '-r',
        help='Randomize the denormalization.',
        action='store_true'
    )
    sp.add_argument(
        '--seed', '-s',
        help='Seed the randomized denormalization.',
        action='store',
        default=''
    )
    sp.set_defaults(func=mode_denormal)


def parse_details(spa: _SubParsersAction) -> None:
    """Add the details mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
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
    """Parse the arguments used to invoke the script and execute
    the script.
    """
    # Build the argument parser.
    p = ArgumentParser(
        description='Unicode and character set explorer.',
        prog='charex'
    )

    # Build subparsers for each mode.
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
