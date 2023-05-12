"""
__main__
~~~~~~~~

Mainline for command line invocations of :mod:`charex`.
"""
from sys import argv

import charex.shell as sh


# Mainline.
if __name__ == '__main__':
    # If there were no arguments passed, drop into the command shell.
    if len(argv) < 2:
        sh.mode_shell(None)

    # Otherwise parse the arguments and execute.
    else:
        sh.parse_invocation()
