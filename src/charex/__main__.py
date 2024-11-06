"""
__main__
~~~~~~~~

Mainline for command line invocations of :mod:`charex`.
"""
from sys import argv

import charex.shell as sh


# Mainline.
def main() -> None:
    # If there were no arguments passed, drop into the command shell.
    if len(argv) < 2:
        sh.mode_sh(None)

    # Otherwise parse the arguments and execute.
    else:
        sh.invoke()


if __name__ == '__main__':
    main()
