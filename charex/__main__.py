"""
__main__
~~~~~~~~

Mainline for command line invocations of :mod:`charex`.
"""
from argparse import ArgumentParser, Namespace, _SubParsersAction
from sys import argv

import charex.shell as sh
from charex.util import bin2bytes, hex2bytes


# Running modes.
def mode_charsetlist(args: Namespace) -> None:
    """List registered character sets.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    sh.write_cset_list(args.description)


def mode_charset(args: Namespace) -> None:
    """Perform character set lookups.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    # Determine whether this is a code point or address lookup.
    if args.reverse:
        sh.write_cset_multiencode(args.base)
    else:
        sh.write_cset_multidecode(args.base)


def mode_denormal(args: Namespace) -> None:
    """Perform denormalizations.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    # Just count the number of denormalizations.
    if args.count:
        sh.write_count_denormalizations(args.base, args.form, args.maxdepth)

    # List all the denormalizations.
    else:
        sh.write_denormalizations(
            args.base,
            args.form,
            args.maxdepth,
            args.number,
            args.random,
            args.seed
        )


def mode_details(args: Namespace) -> None:
    """Display details for a code point.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    sh.write_char_detail(args.codepoint)


def mode_escape(args: Namespace) -> None:
    """Escape a string using the given scheme.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    sh.write_escape(args.base, args.scheme)


def mode_esclist(args: Namespace) -> None:
    """List the registered escape schemes.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    sh.write_schemes_list()


def mode_shell(args: Namespace | None) -> None:
    """Run :mod:`charex` in an interactive shell.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    sh.Shell(completekey='tab').cmdloop()


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
        aliases=['cd', 'cset',],
        help=(
            'Show the characters the integer could be in different '
            'characer sets.'
        )
    )
    sp.add_argument(
        'base',
        help=(
            'The base integer. Prefix the integer with "0x" for hex '
            'or "0b" for binary. No prefix will be interpreted as the'
            'UTF-8 address of the character.'
        ),
        action='store',
        type=str
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


def parse_charsetlist(spa: _SubParsersAction) -> None:
    """Add the charsetlist mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'charsetlist',
        aliases=['cl', 'csetlist', 'cslist'],
        help=(
            'Show the characters the integer could be in different '
            'characer sets.'
        )
    )
    sp.add_argument(
        '--description', '-d',
        help='Show the description for the character sets.',
        action='store_true'
    )
    sp.set_defaults(func=mode_charsetlist)


def parse_denormal(spa: _SubParsersAction) -> None:
    """Add the denormal mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'denormal',
        aliases=['dn', 'n',],
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
        aliases=['d', 'deets', 'dt'],
        help='Display the details for the given code point.'
    )
    sp.add_argument(
        'codepoint',
        help='The code point.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_details)


def parse_escape(spa: _SubParsersAction) -> None:
    """Add the escape mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'escape',
        aliases=['es', 'esc',],
        help='Escape the given string with the given scheme.'
    )
    sp.add_argument(
        'base',
        help='The string to escape.',
        action='store',
        type=str
    )
    sp.add_argument(
        '--scheme', '-s',
        help='The scheme to escape with.',
        action='store',
        default='url',
        type=str
    )
    sp.set_defaults(func=mode_escape)


def parse_esclist(spa: _SubParsersAction) -> None:
    """Add the esclist mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'esclist',
        aliases=['el',],
        help='List the registered escape schemes.'
    )
    sp.set_defaults(func=mode_esclist)


def parse_shell(spa: _SubParsersAction) -> None:
    """Add the shell mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'shell',
        aliases=['sh',],
        help=(
            'Run charex in an interactive shell.'
        )
    )
    sp.set_defaults(func=mode_shell)


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
    parse_charsetlist(spa)
    parse_denormal(spa)
    parse_details(spa)
    parse_escape(spa)
    parse_esclist(spa)
    parse_shell(spa)

    # Execute.
    args = p.parse_args()
    args.func(args)


# Mainline.
if __name__ == '__main__':
    # If there were no arguments passed, drop into the command shell.
    if len(argv) < 2:
        mode_shell(None)

    # Otherwise parse the arguments and execute.
    else:
        parse_invocation()
