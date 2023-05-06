"""
shell
~~~~~

An interactive command shell for :mod:`charex`.
"""
from cmd import Cmd
import readline

from charex import denormal as dn


# Classes.
class Shell(Cmd):
    """A command shell for :mod:`charex`."""
    intro = 'Welcome to the charex shell.'
    prompt = 'charex> '

    # Commands.
    def do_dnfkc(self, arg):
        """Denormalize with NFKC."""
        results = dn.denormalize(arg, 'nfkc')
        for result in results:
            print(result)

    def do_denorm(self, arg):
        """Denormalize the string using the form."""
        base, form = arg.split()
        results = dn.denormalize(base, form)
        for result in results:
            print(result)

    def do_EOF(self, arg):
        """Exit the charex shell."""
        print('Exiting charex.')
        return True

    def do_exit(self, arg):
        """Exit the charex shell."""
        print('Exiting charex.')
        return True


# Mainline.
if __name__ == '__main__':
    Shell().cmdloop()
