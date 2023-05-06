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

    # Utility methods.
    def denorm(self, base, form, maxdepth=None, maxcount=None, random=False):
        """Perform a denormalization."""
        results = dn.denormalize(base, form, maxdepth, maxcount, random)
        for result in results:
            print(result)


# Mainline.
if __name__ == '__main__':
    Shell().cmdloop()
