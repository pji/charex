"""
shell
~~~~~

An interactive command shell for :mod:`charex`.
"""
from cmd import Cmd
import readline

from charex import charex as ch
from charex import charsets as cset
from charex import denormal as dn
from charex.util import neutralize_control_characters


# Output functions.
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


# Classes.
class Shell(Cmd):
    """A command shell for :mod:`charex`."""
    intro = 'Welcome to the charex shell.'
    prompt = 'charex> '

    # Commands.
    def do_cslist(self, arg):
        """List the registered character sets."""
        results = cset.get_codecs()
        for result in results:
            print(result)

    def do_csmdecode(self, arg):
        """Decode the given hexadecimal string in each character set."""
        codecs = cset.get_codecs()
        width = max(len(codec) for codec in codecs) + 1
        results = cset.multidecode(arg, codecs)
        for codec in codecs:
            result = results[codec]
            value = neutralize_control_characters(result)
            codec += ':'
            if len(result) == 1:
                c = ch.Character(result)
                print(f'{codec:<{width}} {value} {c.code_point} {c.name}')
            elif len(result) > 1:
                print(f'{codec:<{width}} {value} ** multiple characters **')

    def do_csmencode(self, arg):
        """Encode the given character in each character set."""
        codecs = cset.get_codecs()
        width = max(len(codec) for codec in codecs) + 1
        results = cset.multiencode(arg, codecs)
        for key in results:
            if b := results[key]:
                c = ''.join(f'{n:>02x}'.upper() for n in b)
                print(f'{key:>{width}}: {c}')

    def do_details(self, arg):
        """Display the details for the given character."""
        write_char_detail(arg)

    def do_dnfcnum(self, arg):
        """Count the number of NFC denormalizations."""
        write_count_denormalizations(arg, 'nfc', maxdepth=0)

    def do_dnfkcnum(self, arg):
        """Count the number of NFKC denormalizations."""
        write_count_denormalizations(arg, 'nfkc', maxdepth=0)

    def do_dnfc(self, arg):
        """Denormalize with NFC."""
        self.denorm(arg, 'nfc')

    def do_dnfd(self, arg):
        """Denormalize with NFD."""
        self.denorm(arg, 'nfd')

    def do_dnfkc(self, arg):
        """Denormalize with NFKC."""
        self.denorm(arg, 'nfkc')

    def do_dnfkd(self, arg):
        """Denormalize with NFKD."""
        self.denorm(arg, 'nfkd')

    def do_EOF(self, arg):
        """Exit the charex shell."""
        print()
        print('Exiting charex.')
        return True

    def do_exit(self, arg):
        """Exit the charex shell."""
        print('Exiting charex.')
        return True

    # Utility methods.
    def denorm(self, base, form, maxdepth=None, maxcount=None, random=False):
        """Perform a denormalization."""
        results = dn.denormalize(base, form, maxdepth, maxcount, random)
        for result in results:
            print(result)


# Mainline.
if __name__ == '__main__':
    Shell().cmdloop()
