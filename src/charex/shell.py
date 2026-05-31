"""
shell
~~~~~

An interactive command shell for :mod:`charex`.
"""
import readline
from argparse import (
    ArgumentParser,
    Namespace,
    RawDescriptionHelpFormatter,
    _SubParsersAction
)
from cmd import Cmd
from collections.abc import Callable, Sequence
from shlex import split
from shutil import get_terminal_size
from textwrap import wrap

from charex import charsets as cset
from charex import cmds
from charex import escape as esc
from charex import gui
from charex import normal as nl
from charex import util


# Registry.
subparsers: list[Callable[[_SubParsersAction], None]] = []


# Registration.
def subparser(
    fn: Callable[[_SubParsersAction], None]
) -> Callable[[_SubParsersAction], None]:
    """A decorator for registering subparsers.

    :param fn: The function being registered.
    :return: The registered :class:`collections.abc.Callable`.
    :rtype: collections.abc.Callable
    """
    subparsers.append(fn)
    return fn


# Running modes.
def mode_cd(args: Namespace) -> None:
    """Decode the given address in all codecs.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.cd(args.base):
        print(line)
    print()


def mode_ce(args: Namespace) -> None:
    """Encode the given character in all codecs.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.ce(args.base):
        print(line)
    print()


def mode_cl(args: Namespace) -> None:
    """List registered character sets.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.cl(args.description):
        print(line)
        if args.description:
            print()
    print()


def mode_clear(args: Namespace) -> None:
    """Clear the terminal.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    print('\x1b[2J')
    print('\x1b[1;1H', end='')


def mode_ct(args: Namespace) -> None:
    """Count denormalization results.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    count = cmds.ct(args.base, args.form, args.maxdepth)
    print(count)
    print()


def mode_dm(args: Namespace) -> None:
    """Build a denormalization map.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    results = nl.build_denormalization_map(args.form)
    print(results)
    print()


def mode_dn(args: Namespace) -> None:
    """Perform denormalizations.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for result in cmds.dn(
        args.base,
        args.form,
        args.maxdepth,
        args.random,
        args.seed
    ):
        print(result)
    print()


def mode_dt(args: Namespace) -> None:
    """Display details for a code point.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.dt(args.codepoint):
        bline = line.encode('utf_8', errors='replace')
        print(bline.decode('utf_8'))
    print()


def mode_el(args: Namespace) -> None:
    """List the registered escape schemes.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.el(args.description):
        print(line)
        if args.description:
            print()
    print()


def mode_es(args: Namespace) -> None:
    """Escape a string using the given scheme.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    result = cmds.es(args.base, args.scheme, 'utf8')
    print(result)
    print()


def mode_fl(args: Namespace) -> None:
    """List registered normalization forms.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.fl(args.description):
        print(line)
        if args.description:
            print()
    print()


def mode_gui(args: Namespace) -> None:
    """Start the GUI.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    print('Running charex GUI....')
    gui.main()
    print('charex GUI stopped.')


def mode_mf(args: Namespace) -> None:
    """Create emoji sequence for a region's flag.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    result = cmds.mf(args.region)
    print(result)
    print()


def mode_nl(args: Namespace) -> None:
    """Perform normalizations.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    result = cmds.nl(args.form, args.base, args.expand)
    print(result)
    print()


def mode_ns(args: Namespace) -> None:
    """Show the list of named sequences.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.ns():
        print(line)
    print()


def mode_pf(args: Namespace) -> None:
    """List characters with a given property value.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.pf(
        args.prop,
        args.value,
        insensitive=args.insensitive,
        regex=args.regex
    ):
        bline = line.encode('utf_8', errors='replace')
        print(bline.decode('utf_8'))
    print()


def mode_sh(args: Namespace | None) -> None:
    """Run in an interactive shell.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    Shell(completekey='tab').cmdloop()


def mode_sv(args: Namespace) -> None:
    """Show the list of standardized variants.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.sv():
        print(line)
    print()


def mode_up(args: Namespace) -> None:
    """List the Unicode properties.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.up(args.description):
        print(line)
        if args.description:
            print()
    print()


def mode_uv(args: Namespace) -> None:
    """List the valid values for a Unicode property.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.uv(args.prop, args.description):
        print(line)
        if args.description:
            print()
    print()


def mode_zc(args: Namespace) -> None:
    """Show the list of emoji ZWJ sequences.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    for line in cmds.zc():
        print(line)
    print()


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
    for fn in subparsers:
        fn(spa)

    return p


@subparser
def parse_cd(spa: _SubParsersAction) -> None:
    """Add the cd mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'cd',
        description='Decode the given address in all codecs.',
        epilog=util.ADDRESS_FORMAT_DOC,
        formatter_class=RawDescriptionHelpFormatter
    )
    sp.add_argument(
        'base',
        help=(
            'The base address. See below for details.'
        ),
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_cd)


@subparser
def parse_ce(spa: _SubParsersAction) -> None:
    """Add the ce mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'ce',
        description='Encode the given character in all codecs.',
        epilog=util.CHAR_FORMAT_DOC,
        formatter_class=RawDescriptionHelpFormatter
    )
    sp.add_argument(
        'base',
        help='The character to lookup in each character set.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_ce)


@subparser
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


@subparser
def parse_clear(spa: _SubParsersAction) -> None:
    """Clear the terminal.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'clear',
        aliases=['clr',],
        description='Clear the terminal.'
    )
    sp.set_defaults(func=mode_clear)


@subparser
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


@subparser
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


@subparser
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
            'If not random, sets the maximum number of denormalizations '
            'to use for each character. If random, sets the number of '
            'random denormalizations to return.'
        ),
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


@subparser
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
        description='Display the details for the given character.',
        epilog=util.CHAR_FORMAT_DOC,
        formatter_class=RawDescriptionHelpFormatter
    )
    sp.add_argument(
        'codepoint',
        help='The character.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_dt)


@subparser
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


@subparser
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


@subparser
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


@subparser
def parse_gui(spa: _SubParsersAction) -> None:
    """Run the GUI.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'gui',
        aliases=[],
        description='Run the charex GUI.'
    )
    sp.set_defaults(func=mode_gui)


@subparser
def parse_mf(spa: _SubParsersAction) -> None:
    """Add the mf mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'mf',
        aliases=['make_flag', 'region_flag',],
        description='Show flag for a region.'
    )
    sp.add_argument(
        'region',
        help='The ISO 3166 code for the region.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_mf)


@subparser
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


@subparser
def parse_ns(spa: _SubParsersAction) -> None:
    """Add the ns mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'ns',
        aliases=['nseqs', 'named_sequences',],
        description='Show the list of named sequences.'
    )
    sp.set_defaults(func=mode_ns)


@subparser
def parse_pf(spa: _SubParsersAction) -> None:
    """Add the pf mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'pf',
        aliases=['propfilter', 'pfilt',],
        description='List characters with a given property value.'
    )
    sp.add_argument(
        'prop',
        help='The property for the filter.',
        action='store'
    )
    sp.add_argument(
        'value',
        help='The value to filter with.',
        action='store'
    )
    sp.add_argument(
        '--insensitive', '-i',
        help='The matching is case insensitive.',
        action='store_true',
    )
    sp.add_argument(
        '--regex', '-g',
        help='The value is used as a regular expression when matching.',
        action='store_true',
    )
    sp.set_defaults(func=mode_pf)


@subparser
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


@subparser
def parse_sv(spa: _SubParsersAction) -> None:
    """Add the sv mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'sv',
        aliases=['svars', 'standardized_variants',],
        description='Show the list of standardized variants.'
    )
    sp.set_defaults(func=mode_sv)


@subparser
def parse_up(spa: _SubParsersAction) -> None:
    """Add the up mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'up',
        aliases=['proplist', 'plist',],
        description='List the Unicode properties.'
    )
    sp.add_argument(
        '-d', '--description',
        help='Show the long name of the properties.',
        action='store_true'
    )
    sp.set_defaults(func=mode_up)


@subparser
def parse_uv(spa: _SubParsersAction) -> None:
    """Add the uv mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'uv',
        aliases=['propvallist', 'pvlist', 'upv',],
        description='List the valid values of a Unicode property.'
    )
    sp.add_argument(
        'prop',
        help='The Unicode property.',
        action='store'
    )
    sp.add_argument(
        '-d', '--description',
        help='Show the long name of the properties.',
        action='store_true'
    )
    sp.set_defaults(func=mode_uv)


@subparser
def parse_zc(spa: _SubParsersAction) -> None:
    """Add the zc mode subparser.

    :param spa: The subparser action used to add a new subparser to
        the main parser.
    :return: None.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'zc',
        aliases=['emoji_zwj_sequences', 'zwjseqs', 'zwj_sequences',],
        description='Show the list of named sequences.'
    )
    sp.set_defaults(func=mode_zc)


# Command line invocation.
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
    def do_EOF(self, arg):
        """Exit the charex shell."""
        print()
        print('Exiting charex.')
        print()
        return True

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


def make_cmd_handler(mode: str):
    """Dynamically build the shell commands."""
    def handler(self, arg):
        cmd = f'{mode} {arg}'
        self._run_cmd(cmd)

    fn = globals()[f'mode_{mode}']
    docstring = fn.__doc__.split('\n')[0]
    handler.__doc__ = docstring
    return handler


def make_help_handler(mode: str):
    """Dynamically build the help for shell commands."""
    def handler(self):
        cmd = f'{mode} -h'
        self._run_cmd(cmd)

    handler.__doc__ = f'Run the `{mode}` command.'
    return handler


# Add the commands and their help to the shell.
# This will add any command that has a mode_* function above as
# a command in Shell.
for name in modes:
    _, mode = name.split('_')
    meth_name = f'do_{mode}'
    help_name = f'help_{mode}'

    # Add the command method.
    if not hasattr(Shell, meth_name):
        method = make_cmd_handler(mode)
        setattr(Shell, meth_name, method)

    # Add the help method.
    if not hasattr(Shell, help_name):
        help_meth = make_help_handler(mode)
        setattr(Shell, help_name, help_meth)
