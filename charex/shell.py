"""
shell
~~~~~

An interactive command shell for :mod:`charex`.
"""
from cmd import Cmd
import readline
from textwrap import wrap

from charex import charex as ch
from charex import charsets as cset
from charex import denormal as dn
from charex import util
from charex.util import neutralize_control_characters, read_resource


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


def write_cset_multidecode(value: bytes) -> None:
    """Print the character that the given hex string decodes to in each
    registered character set.
    """
    # Get the data.
    codecs = cset.get_codecs()
    results = cset.multidecode(value, (codec for codec in codecs))

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
        c = neutralize_control_characters(c)
        print(f'{key:>{width}}: {c} {details}')


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


# Classes.
class Shell(Cmd):
    """A command shell for :mod:`charex`."""
    intro = 'Welcome to the charex shell.'
    prompt = 'charex> '

    # Commands.
    def do_cd(self, arg):
        """Decode the given hex string in all codecs."""
        value = util.hex2bytes(arg)
        write_cset_multidecode(value)

    def do_ce(self, arg):
        """Encode the given character in all codecs."""
        write_cset_multiencode(arg)

    def do_cl(self, arg):
        """List the registered character sets."""
        show_desc = True
        if arg == 'hide':
            show_desc = False
        write_cset_list(show_desc)

    def do_ct(self, arg):
        """Count denormalization results."""
        form, base, *rest = arg.split()
        form = form.lower()
        maxdepth = 0
        if rest:
            maxdepth = rest[0]
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

    def do_xt(self, arg):
        """Exit the charex shell."""
        print('Exiting charex.')
        print()
        return True

    # Command help.
    def help_cd(self):
        """Help for the cd command."""
        lines = read_resource('help_cd')
        print(''.join(lines))

    def help_ce(self):
        lines = read_resource('help_ce')
        print(''.join(lines))

    def help_cl(self):
        lines = read_resource('help_cl')
        print(''.join(lines))

    def help_ct(self):
        """Help for the ct command."""
        lines = read_resource('help_count')
        print(''.join(lines))

    def help_dn(self):
        """Help for the dn command."""
        lines = read_resource('help_dn')
        print(''.join(lines))

    def help_dt(self):
        """Help for the dt command."""
        lines = read_resource('help_dt')
        print(''.join(lines))

    def help_rd(self):
        """Help for the rd command."""
        lines = read_resource('help_rd')
        print(''.join(lines))

    def help_xt(self):
        lines = read_resource('help_xt')
        print(''.join(lines))
