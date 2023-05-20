"""
shell
~~~~~

An interactive command shell for :mod:`charex`.
"""
from collections.abc import Callable, Sequence
from argparse import (
    ArgumentParser,
    Namespace,
    _SubParsersAction,
    RawDescriptionHelpFormatter
)
from cmd import Cmd
from itertools import zip_longest
import readline
from shlex import split
from shutil import get_terminal_size
from textwrap import wrap

from charex import charex as ch
from charex import charsets as cset
from charex import denormal as dn
from charex import escape as esc
from charex import normal as nl
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
    # Get the data.
    codecs = cset.get_codecs()
    results = cset.multidecode(args.base, (codec for codec in codecs))

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


def mode_dm(args: Namespace) -> None:
    """Build a denormalization map.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    normal_fn = nl.forms[args.form]
    results = nl.build_denormalization_map(normal_fn)
    print(results)
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
    cp = args.codepoint
    char = ch.Character(cp)
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


def mode_fl(args: Namespace) -> None:
    """List registered normalization forms.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    forms = nl.get_forms()
    write_list(forms, nl.get_description, args.description)
    print()


def mode_nl(args: Namespace) -> None:
    """Perform normalizations.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    result = nl.normalize(args.form, args.base)
    print(result)
    if args.expand:
        for item in result:
            char = ch.Character(item)
            indent = '  '
            if 'mark' in char.category.casefold():
                indent += ' '
            print(f'  {char.summarize()}')
    print()


def mode_sh(args: Namespace | None) -> None:
    """Run in an interactive shell.

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
        epilog=describe_modes(),
        formatter_class=RawDescriptionHelpFormatter,
        prog='charex'
    )

    # Build subparsers for each mode.
    spa = p.add_subparsers(
        help=list_modes(),
        metavar='mode',
        required=True
    )
    parse_cd(spa)
    parse_ce(spa)
    parse_cl(spa)
    parse_ct(spa)
    parse_dm(spa)
    parse_dn(spa)
    parse_dt(spa)
    parse_el(spa)
    parse_es(spa)
    parse_fl(spa)
    parse_nl(spa)
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
        description='Decode the given address in all codecs.'
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
        description='Encode the given character in all codecs.'
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
        description='List the registered character sets.'
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
        description='Count of denormalization results.'
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


def parse_dm(spa: _SubParsersAction) -> None:
    """Add the dm mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    valid_forms = ', '.join(form for form in nl.get_forms())

    sp = spa.add_parser(
        'dm',
        aliases=['denormalmap',],
        description='Build a denormalization map.'
    )
    sp.add_argument(
        'form',
        choices=nl.get_forms(),
        help=(
            'The normalization form for the normalization. Valid '
            f'options are: {valid_forms}.'
        ),
        metavar='form'
    )
    sp.set_defaults(func=mode_dm)


def parse_dn(spa: _SubParsersAction) -> None:
    """Add the dn mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    valid_forms = ', '.join(form for form in nl.get_forms())

    sp = spa.add_parser(
        'dn',
        aliases=['denormal',],
        description='Denormalize a string.'
    )
    sp.add_argument(
        'form',
        choices=nl.get_forms(),
        help=(
            'The normalization form for the denormalization. Valid '
            f'options are: {valid_forms}.'
        ),
        metavar='form'
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
        description='Display the details for the given code point.'
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
        description='List the registered escape schemes.'
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
    valid_schemes = ', '.join(scheme for scheme in esc.get_schemes())

    sp = spa.add_parser(
        'es',
        aliases=['escape', 'esc',],
        description='Escape the string.'
    )
    sp.add_argument(
        'scheme',
        action='store',
        choices=esc.get_schemes(),
        default='url',
        help=(
            'The scheme to escape with. The valid schemes '
            f'are: {valid_schemes}.'
        ),
        metavar='scheme'
    )
    sp.add_argument(
        'base',
        help='The string to escape.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_es)


def parse_fl(spa: _SubParsersAction) -> None:
    """Add the fl mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'fl',
        aliases=['formlist', 'flist',],
        description='List the registered normalization forms.'
    )
    sp.add_argument(
        '-d', '--description',
        help='Show the description for the character sets.',
        action='store_true'
    )
    sp.set_defaults(func=mode_fl)


def parse_nl(spa: _SubParsersAction) -> None:
    """Add the nl mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    valid_forms = ', '.join(form for form in nl.get_forms())

    sp = spa.add_parser(
        'nl',
        aliases=['normal',],
        description='Normalize a string.'
    )
    sp.add_argument(
        'form',
        choices=nl.get_forms(),
        help=(
            'The normalization form for the normalization. Valid '
            f'options are: {valid_forms}.'
        ),
        metavar='form'
    )
    sp.add_argument(
        'base',
        help='The base normalized string.',
        action='store',
        type=str
    )
    sp.add_argument(
        '-e', '--expand',
        help='Show each character in the normalized string.',
        action='store_true'
    )
    sp.set_defaults(func=mode_nl)


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
        description='Run charex in an interactive shell.'
    )
    sp.set_defaults(func=mode_sh)


def invoke(
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

    def do_dm(self, arg):
        """Build a denormalization map."""
        cmd = f'dm {arg}'
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

    def do_fl(self, arg):
        """List the registered normalization forms."""
        cmd = f'fl {arg}'
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

    def do_nl(self, arg):
        """Normalize the given string."""
        cmd = f'nl {arg}'
        self._run_cmd(cmd)

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

    def help_dm(self):
        """Help for the dm command."""
        cmd = f'dm -h'
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

    def help_fl(self):
        """Help for the fl command."""
        cmd = f'fl -h'
        self._run_cmd(cmd)

    def help_nl(self):
        """Help for the nl command."""
        cmd = f'nl -h'
        self._run_cmd(cmd)

    def help_xt(self):
        lines = util.read_resource('help_xt')
        print(''.join(lines))

    # Private methods.
    def _run_cmd(self, cmd):
        """Run the given command."""
        try:
            invoke(cmd, self.parser)
        except SystemExit as ex:
            print()


# Mode registry.
modes = {
    name: globals()[name]
    for name in dir()
    if name.startswith('mode_')
}


def describe_modes() -> str:
    """Return a description of the operating modes."""
    global modes
    width, height = get_terminal_size((80, 20))
    text = wrap((
        'The following are brief desciptions of each of the '
        'available options for the mode:'
    ), width)
    result = '\n'.join(text) + '\n\n'
    for mode in modes:
        name = mode.split('_')[1]
        doc = modes[mode].__doc__
        descr = doc.split('\n\n')[0]
        result += f'  * {name}: {descr}\n'
    return result


def list_modes() -> str:
    """Return a description of the available modes."""
    global modes
    result = 'The following modes are available: '
    names = ', '.join(mode.split('_')[1] for mode in modes)
    result += names
    return result
