"""
shell
~~~~~

An interactive command shell for :mod:`charex`.
"""
from collections.abc import Callable, Sequence
from argparse import ArgumentParser, Namespace, _SubParsersAction
from cmd import Cmd
from itertools import zip_longest
import readline
from shlex import split
from textwrap import wrap

from charex import charex as ch
from charex import charsets as cset
from charex import denormal as dn
from charex import escape as esc
from charex import util


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
) -> None:
    """Output the given list.

    :param items: The items to list.
    :param get_descr: The function used to look up the discription
        of each item.
    :param show_descr: Whether include the descriptions of each item
        in the output.
    :return: None.
    :rtype: NoneType
    """
    width = max(len(item) for item in items)
    for item in items:
        if show_descr:
            descr = get_descr(item)
            row = make_description_row(item, width, descr)
            print(row)
            print()
        else:
            print(item)


# Running modes.
def mode_cd(args: Namespace) -> None:
    """Decode the given address in all codecs.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    # Normalize the data.
    if args.base.startswith('0b'):
        b = util.bin2bytes(args.base[2:])
    elif args.base.startswith('0x'):
        b = util.hex2bytes(args.base[2:])
    else:
        b = args.base.encode('utf8')

    # Get the data.
    codecs = cset.get_codecs()
    results = cset.multidecode(b, (codec for codec in codecs))

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
        print(f'{key:>{width}}: {c} {details}')
    print()


def mode_ce(args: Namespace) -> None:
    """Encode the given character in all codecs.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    # Get the data.
    codecs = cset.get_codecs()
    results = cset.multiencode(args.base, (codec for codec in codecs))

    # Write the output.
    width = max(len(codec) for codec in codecs)
    for key in results:
        if b := results[key]:
            c = ''.join(f'{n:>02x}'.upper() for n in b)
            print(f'{key:>{width}}: {c}')
    print()


def mode_cl(args: Namespace) -> None:
    """List registered character sets.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    codecs = cset.get_codecs()
    write_list(codecs, cset.get_codec_description, args.description)
    print()


def mode_ct(args: Namespace) -> None:
    """Count denormalization results.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    count = dn.count_denormalizations(args.base, args.form, args.maxdepth)
    print(f'{count:,}')
    print()


def mode_dn(args: Namespace) -> None:
    """Perform denormalizations.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    results = dn.denormalize(
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


def mode_dt(args: Namespace) -> None:
    """Display details for a code point.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    def rev_normalize(char: ch.Character, form: str) -> str:
        points = char.reverse_normalize(form)
        chars = (ch.Character(point) for point in points)
        values = [f'{c.summarize()}' for c in chars]
        if not values:
            return ''
        return ('\n' + ' ' * 22).join(v for v in values)

    # Gather the details for display.
    char = ch.Character(args.codepoint)
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


def mode_el(args: Namespace) -> None:
    """List the registered escape schemes.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    schemes = esc.get_schemes()
    write_list(schemes, esc.get_description, args.description)
    print()


def mode_es(args: Namespace) -> None:
    """Escape a string using the given scheme.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    result = esc.escape(args.base, args.scheme, 'utf8')
    print(result)
    print()


def mode_sh(args: Namespace | None) -> None:
    """Run :mod:`charex` in an interactive shell.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    Shell(completekey='tab').cmdloop()


# Command parsing.
def build_parser() -> ArgumentParser:
    """Build the argument parser.

    :return: The :class:`argparse.ArgumentParser`.
    :rtype: argparse.ArgumentParser
    """
    # Build the argument parser.
    p = ArgumentParser(
        description='Unicode and character set explorer.',
        prog='charex'
    )

    # Build subparsers for each mode.
    spa = p.add_subparsers(required=True)
    parse_cd(spa)
    parse_ce(spa)
    parse_cl(spa)
    parse_ct(spa)
    parse_dn(spa)
    parse_dt(spa)
    parse_el(spa)
    parse_es(spa)
    parse_sh(spa)

    return p


def parse_cd(spa: _SubParsersAction) -> None:
    """Add the cd mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'cd',
        help='Decode the given address in all codecs.'
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
    sp.set_defaults(func=mode_cd)


def parse_ce(spa: _SubParsersAction) -> None:
    """Add the ce mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'ce',
        help='Encode the given character in all codecs.'
    )
    sp.add_argument(
        'base',
        help='The character to lookup in each character set.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_ce)


def parse_cl(spa: _SubParsersAction) -> None:
    """Add the charsetlist mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'cl',
        aliases=['charsetlist', 'csetlist', 'cslist'],
        help='List the registered character sets.'
    )
    sp.add_argument(
        '-d', '--description',
        help='Show the description for the character sets.',
        action='store_true'
    )
    sp.set_defaults(func=mode_cl)


def parse_ct(spa: _SubParsersAction) -> None:
    """Add the ct mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'ct',
        aliases=['count',],
        help='Count of denormalization results.'
    )
    sp.add_argument(
        'form',
        help='The Unicode normalization form for the denormalization.',
        choices=('nfc', 'nfd', 'nfkc', 'nfkd',)
    )
    sp.add_argument(
        'base',
        help='The base normalized string.',
        action='store',
        type=str
    )
    sp.add_argument(
        '-m', '--maxdepth',
        help=(
            'Maximum number of reverse normalizations to use '
            'for each character.'
        ),
        default=0,
        action='store',
        type=int
    )
    sp.set_defaults(func=mode_ct)


def parse_dn(spa: _SubParsersAction) -> None:
    """Add the dn mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'dn',
        aliases=['denormal',],
        help='Denormalize a string.'
    )
    sp.add_argument(
        'form',
        help='The Unicode normalization form for the denormalization.',
        choices=('nfc', 'nfd', 'nfkc', 'nfkd',)
    )
    sp.add_argument(
        'base',
        help='The base normalized string.',
        action='store',
        type=str
    )
    sp.add_argument(
        '-m', '--maxdepth',
        help=(
            'Maximum number of reverse normalizations to use '
            'for each character.'
        ),
        default=0,
        action='store',
        type=int
    )
    sp.add_argument(
        '-n', '--number',
        help='Maximum number of results to return.',
        default=0,
        action='store',
        type=int
    )
    sp.add_argument(
        '-r', '--random',
        help='Randomize the denormalization.',
        action='store_true'
    )
    sp.add_argument(
        '-s', '--seed',
        help='Seed the randomized denormalization.',
        action='store',
        default=''
    )
    sp.set_defaults(func=mode_dn)


def parse_dt(spa: _SubParsersAction) -> None:
    """Add the dt mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'dt',
        aliases=['details',],
        help='Display the details for the given code point.'
    )
    sp.add_argument(
        'codepoint',
        help='The code point.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_dt)


def parse_el(spa: _SubParsersAction) -> None:
    """Add the el mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'el',
        aliases=['escapelist', 'esclist',],
        help='List the registered escape schemes.'
    )
    sp.add_argument(
        '-d', '--description',
        help='Show the description for the character sets.',
        action='store_true'
    )
    sp.set_defaults(func=mode_el)


def parse_es(spa: _SubParsersAction) -> None:
    """Add the escape mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'es',
        aliases=['escape', 'esc',],
        help='Escape the string.'
    )
    sp.add_argument(
        'scheme',
        help='The scheme to escape with.',
        action='store',
        default='url',
        type=str
    )
    sp.add_argument(
        'base',
        help='The string to escape.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_es)


def parse_sh(spa: _SubParsersAction) -> None:
    """Add the shell mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'sh',
        aliases=['shell',],
        help=(
            'Run charex in an interactive shell.'
        )
    )
    sp.set_defaults(func=mode_sh)


def parse_invocation(
    cmd: str | None = None,
    p: ArgumentParser | None = None
) -> None:
    """Parse the arguments used to invoke the script and execute
    the script.
    """
    if not p:
        p = build_parser()
    if cmd:
        argv = split(cmd)
        args = p.parse_args(argv)
    else:
        args = p.parse_args()
    args.func(args)


# The interactive shell.
class Shell(Cmd):
    """A command shell for :mod:`charex`."""
    intro = (
        'Welcome to the charex shell.\n'
        'Press ? for a list of comands.\n'
    )
    prompt = 'charex> '

    def __init__(self, *args, **kwargs) -> None:
        self.parser = build_parser()
        super().__init__(*args, **kwargs)

    # Commands.
    def do_cd(self, arg):
        """Decode the given address in all codecs."""
        cmd = f'cd {arg}'
        self._run_cmd(cmd)

    def do_ce(self, arg):
        """Encode the given character in all codecs."""
        cmd = f'ce {arg}'
        self._run_cmd(cmd)

    def do_cl(self, arg):
        """List the registered character sets."""
        cmd = f'cl {arg}'
        self._run_cmd(cmd)

    def do_ct(self, arg):
        """Count denormalization results."""
        cmd = f'ct {arg}'
        self._run_cmd(cmd)

    def do_dn(self, arg):
        """Denormalize the given string."""
        cmd = f'dn {arg}'
        self._run_cmd(cmd)

    def do_dt(self, arg):
        """Get details for the given character."""
        cmd = f'dt {arg}'
        self._run_cmd(cmd)

    def do_el(self, arg):
        """List the registered escape schemes."""
        cmd = f'el {arg}'
        self._run_cmd(cmd)

    def do_EOF(self, arg):
        """Exit the charex shell."""
        print()
        print('Exiting charex.')
        print()
        return True

    def do_es(self, arg):
        """Escape the string."""
        cmd = f'es {arg}'
        self._run_cmd(cmd)

    def do_help(self, arg):
        """Display command list."""
        if not arg:
            print('The following commands are available:')
            print()
            cmds = (
                cmd for cmd in dir(self)
                if cmd.startswith('do')
                and not cmd.endswith('EOF')
                and not cmd.endswith('eader')
            )
            for cmd in cmds:
                meth = getattr(self, cmd)
                print(f'*  {cmd[3:]}: {meth.__doc__}')
            print()
            print('For help on individual commands, use "help {command}".')
            print()

        else:
            super().do_help(arg)

    def do_xt(self, arg):
        """Exit the charex shell."""
        print('Exiting charex.')
        print()
        return True

    # Command help.
    def help_cd(self):
        """Help for the cd command."""
        cmd = f'cd -h'
        self._run_cmd(cmd)

    def help_ce(self):
        cmd = f'ce -h'
        self._run_cmd(cmd)

    def help_cl(self):
        cmd = f'cl -h'
        self._run_cmd(cmd)

    def help_ct(self):
        """Help for the ct command."""
        cmd = f'ct -h'
        self._run_cmd(cmd)

    def help_dn(self):
        """Help for the dn command."""
        cmd = f'dn -h'
        self._run_cmd(cmd)

    def help_dt(self):
        """Help for the dt command."""
        cmd = f'dt -h'
        self._run_cmd(cmd)

    def help_el(self):
        """Help for the el command."""
        cmd = f'el -h'
        self._run_cmd(cmd)

    def help_es(self):
        """Help for the es command."""
        cmd = f'es -h'
        self._run_cmd(cmd)

    def help_xt(self):
        lines = util.read_resource('help_xt')
        print(''.join(lines))

    # Private methods.
    def _run_cmd(self, cmd):
        """Run the given command."""
        try:
            parse_invocation(cmd, self.parser)
        except SystemExit as ex:
            print()
