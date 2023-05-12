"""
shell
~~~~~

An interactive command shell for :mod:`charex`.
"""
from argparse import ArgumentParser, Namespace, _SubParsersAction
from cmd import Cmd
import readline
from textwrap import wrap

from charex import charex as ch
from charex import charsets as cset
from charex import denormal as dn
from charex import escape as esc
from charex import util


# Cached values.
p: ArgumentParser | None = None


# Output functions.
def write_cset_list(show_desc=False) -> None:
    """Print the registered character sets."""
    # Get the data.
    codecs = cset.get_codecs()

    # Print the data.
    width = max(len(codec) for codec in codecs)
    for codec in codecs:
        if show_desc:
            descript = cset.get_codec_description(codec)
            if descript:
                wrapped = wrap(descript, 77 - width)
                print(f'{codec:<{width}}  {wrapped[0]}')
                for line in wrapped[1:]:
                    print(f'{"":<{width}}  {line}')
            else:
                print(codec)
        else:
            print(codec)
    print()


def write_cset_multidecode(value: str) -> None:
    """Print the character that the given hex string decodes to in each
    registered character set.
    """
    # Normalize the data.
    if value.startswith('0b'):
        b = util.bin2bytes(value[2:])
    elif value.startswith('0x'):
        b = util.hex2bytes(value[2:])
    else:
        b = value.encode('utf8')

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


def write_cset_multiencode(value: str) -> None:
    """Print the addresses for the character in each character set."""
    # Get the data.
    codecs = cset.get_codecs()
    results = cset.multiencode(value, (codec for codec in codecs))

    # Write the output.
    width = max(len(codec) for codec in codecs)
    for key in results:
        if b := results[key]:
            c = ''.join(f'{n:>02x}'.upper() for n in b)
            print(f'{key:>{width}}: {c}')
    print()


def write_char_detail(codepoint) -> None:
    """Print the details of the given character."""
    def rev_normalize(char: ch.Character, form: str) -> str:
        points = char.reverse_normalize(form)
        chars = (ch.Character(point) for point in points)
        values = [f'{c.summarize()}' for c in chars]
        if not values:
            return ''
        return ('\n' + ' ' * 22).join(v for v in values)

    # Gather the details for display.
    char = ch.Character(codepoint)
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


def write_count_denormalizations(base: str, form: str, maxdepth: int) -> None:
    """Print the number of denormalizations for the given character
    and form.
    """
    count = dn.count_denormalizations(base, form, maxdepth)
    print(f'{count:,}')
    print()


def write_denormalizations(
    base: str,
    form: str,
    maxdepth: int = 0,
    number: int = 0,
    random: bool = False,
    seed: bytes | int | str = ''
) -> None:
    """Print the denormalizations for the given string."""
    results = dn.denormalize(
        base,
        form,
        maxdepth,
        number,
        random,
        seed
    )
    for result in results:
        print(result)
    print()


def write_escape(base: str, scheme: str, codec: str = 'utf8') -> None:
    """Print the string escaped using the given scheme."""
    result = esc.escape(base, scheme, codec)
    print(result)
    print()


def write_schemes_list() -> None:
    """Print the names of the registered escape schemes."""
    results = esc.get_schemes()
    for scheme in results:
        print(scheme)
    print()


# Running modes.
def mode_cd(args: Namespace) -> None:
    """Decode the given address in all codecs.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    write_cset_multidecode(args.base)


def mode_ce(args: Namespace) -> None:
    """Encode the given character in all codecs.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    write_cset_multiencode(args.base)


def mode_cl(args: Namespace) -> None:
    """List registered character sets.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    write_cset_list(args.description)


def mode_ct(args: Namespace) -> None:
    """Count denormalization results.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    write_count_denormalizations(args.base, args.form, args.maxdepth)


def mode_denormal(args: Namespace) -> None:
    """Perform denormalizations.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    # Just count the number of denormalizations.
    if args.count:
        write_count_denormalizations(args.base, args.form, args.maxdepth)

    # List all the denormalizations.
    else:
        write_denormalizations(
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
    write_char_detail(args.codepoint)


def mode_escape(args: Namespace) -> None:
    """Escape a string using the given scheme.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    write_escape(args.base, args.scheme)


def mode_esclist(args: Namespace) -> None:
    """List the registered escape schemes.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    write_schemes_list()


def mode_shell(args: Namespace | None) -> None:
    """Run :mod:`charex` in an interactive shell.

    :param args: The arguments used when the script was invoked.
    :return: None.
    :rtype: NoneType
    """
    Shell(completekey='tab').cmdloop()


# Command parsing.
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
        '--description', '-d',
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
        help='Count denormalization results.'
    )
    sp.add_argument(
        'form',
        help='Normalization form.',
        action='store',
        type=str
    )
    sp.add_argument(
        'base',
        help='The base normalized string.',
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
    sp.set_defaults(func=mode_ct)


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


def parse_invocation(cmd: str | None = None) -> None:
    """Parse the arguments used to invoke the script and execute
    the script.
    """
    global p

    if not p:
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
        parse_denormal(spa)
        parse_details(spa)
        parse_escape(spa)
        parse_esclist(spa)
        parse_shell(spa)

    # Execute.
    if cmd:
        argv = cmd.split()
        args = p.parse_args(argv)
    else:
        args = p.parse_args()
    args.func(args)


# Classes.
class Shell(Cmd):
    """A command shell for :mod:`charex`."""
    intro = (
        'Welcome to the charex shell.\n'
        'Press ? for a list of comands.\n'
    )
    prompt = 'charex> '

    # Commands.
    def do_cd(self, arg):
        """Decode the given address in all codecs."""
        cmd = f'cd {arg}'
        self._run_cmd(cmd)

    def do_ce(self, arg):
        """Encode the given character in all codecs."""
        write_cset_multiencode(arg)

    def do_cl(self, arg):
        """List the registered character sets."""
        show_desc = False
        if arg in ['-d', '--description']:
            show_desc = True
        write_cset_list(show_desc)

    def do_ct(self, arg):
        """Count denormalization results."""
        form, base, *rest = arg.split()
        form = form.lower()
        maxdepth = 0
        if rest:
            maxdepth = int(rest[1])
        write_count_denormalizations(base, form, maxdepth)

    def do_dn(self, arg):
        """Denormalize the given string."""
        form, base, *rest = arg.split()
        form = form.lower()
        maxdepth = 0
        if rest:
            maxdepth = int(rest[0])
        write_denormalizations(base, form, maxdepth)

    def do_dt(self, arg):
        """Get details for the given character."""
        write_char_detail(arg)

    def do_rd(self, arg):
        """Return random results from a denormalization."""
        form, base, *rest = arg.split()
        form = form.lower()
        number = 0
        seed = ''
        if len(rest) > 0:
            number = int(rest[0])
        if len(rest) > 1:
            seed = rest[1]
        write_denormalizations(
            base,
            form,
            number=number,
            random=True,
            seed=seed
        )

    def do_EOF(self, arg):
        """Exit the charex shell."""
        print()
        print('Exiting charex.')
        print()
        return True

    def do_el(self, arg):
        """List the registered escape schemes."""
        write_schemes_list()

    def do_es(self, arg):
        """Escape the string."""
        scheme, base, *opt = arg.split()
        codec = 'utf8'
        if opt:
            codec = opt[0]
        write_escape(base, scheme, codec)

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
        lines = util.read_resource('help_ce')
        print(''.join(lines))

    def help_cl(self):
        lines = util.read_resource('help_cl')
        print(''.join(lines))

    def help_ct(self):
        """Help for the ct command."""
        lines = util.read_resource('help_count')
        print(''.join(lines))

    def help_dn(self):
        """Help for the dn command."""
        lines = util.read_resource('help_dn')
        print(''.join(lines))

    def help_dt(self):
        """Help for the dt command."""
        lines = util.read_resource('help_dt')
        print(''.join(lines))

    def help_el(self):
        """Help for the el command."""
        lines = util.read_resource('help_el')
        print(''.join(lines))

    def help_es(self):
        """Help for the es command."""
        lines = util.read_resource('help_es')
        print(''.join(lines))

    def help_rd(self):
        """Help for the rd command."""
        lines = util.read_resource('help_rd')
        print(''.join(lines))

    def help_xt(self):
        lines = util.read_resource('help_xt')
        print(''.join(lines))

    # Private methods.
    def _run_cmd(self, cmd):
        """Run the given command."""
        try:
            parse_invocation(cmd)
        except SystemExit as ex:
            print()
