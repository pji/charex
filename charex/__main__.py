"""
__main__
~~~~~~~~

Mainline for :mod:`charex`.
"""
from argparse import ArgumentParser, Namespace

from charex.charex import Character
from charex.denormal import count_denormalizations, denormalize


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
        ('uft-16 BE', char.encode('utf_16be')),
        ('uft-16 LE', char.encode('utf_16le')),
        ('uft-32 BE', char.encode('utf_32be')),
        ('uft-32 LE', char.encode('utf_32le')),
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


def parse_invocation() -> None:
    p = ArgumentParser(
        description='Unicode and character set explorer.',
        prog='charex'
    )
    sp = p.add_subparsers(required=True)

    # Denormal.
    sp_denormal = sp.add_parser(
        'denormal',
        aliases=['n',],
        help='Generate strings that normalize to the given string.'
    )
    sp_denormal.add_argument(
        'base',
        help='The base normalized string.',
        action='store',
        type=str
    )
    sp_denormal.add_argument(
        '--count', '-c',
        help='Count the total number of denormalizations.',
        action='store_true'
    )
    sp_denormal.add_argument(
        '--form', '-f',
        help='Normalization form.',
        default='nfkd',
        action='store',
        type=str
    )
    sp_denormal.add_argument(
        '--maxdepth', '-m',
        help=(
            'Maximum number of reverse normalizations to use '
            'for each character.'
        ),
        default=0,
        action='store',
        type=int
    )
    sp_denormal.set_defaults(func=mode_denormal)

    # Details.
    sp_details = sp.add_parser(
        'details',
        aliases=['d', 'deets'],
        help='Display the details for the given code point.'
    )
    sp_details.add_argument(
        'codepoint',
        help='The code point.',
        action='store',
        type=str
    )
    sp_details.set_defaults(func=mode_details)

    args = p.parse_args()
    args.func(args)


if __name__ == '__main__':
    parse_invocation()
