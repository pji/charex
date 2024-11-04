.. charex documentation master file, created by
   sphinx-quickstart on Tue May  2 07:09:19 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to :mod:`charex` documentation!
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   /unicode.rst
   /forms.rst
   /api.rst
   /requirements.rst


Why Did I Make This?
====================
I find the ambiguity of text data interesting. In memory it's all ones
and zeros. There is nothing inherent to the data that makes `0x20` mean
a space character, but we've mostly agreed that it does. That "mostly"
part is what's interesting to me, and it's where a lot of fun problems lie.


How Do I Use This?
==================
It's in PyPI, so you can install it with `pip`, as long as you are
using Python 3.11 or higher::

    $ pip install charex

:mod:`charex` has four modes of operation:

*   Direct command line invocation,
*   An interactive shell,
*   A graphical user interface (GUI),
*   An application programming interface (API).


Command Line
------------
To get help for direct invocation from the command line::

    $ charex -h


Interactive Shell
-----------------
To launch the interactive shell::

    $ charex

That will bring you to the :mod:`charex` shell::

    Welcome to the charex shell.
    Press ? for a list of comands.
    
    charex>

From here you can type `?` to see the list of available commands::

    Welcome to the charex shell.
    Press ? for a list of comands.
    
    charex> ?
    The following commands are available:

      * cd: Decode the given address in all codecs.
      * ce: Encode the given character in all codecs.
      * cl: List registered character sets.
      * clear: Clear the terminal.
      * ct: Count denormalization results.
      * dm: Build a denormalization map.
      * dn: Perform denormalizations.
      * dt: Display details for a code point.
      * el: List the registered escape schemes.
      * es: Escape a string using the given scheme.
      * fl: List registered normalization forms.
      * nl: Perform normalizations.
      * sh: Run in an interactive shell.
      * up: List the Unicode properties.
      * uv: List the valid values for a Unicode property.

    For help on individual commands, use "help {command}".

    charex>

And then type `help` then a name of one of the commands to learn what
it does::

    charex> help dn
    usage: charex dn [-h] [-m MAXDEPTH] [-n NUMBER] [-r] [-s SEED] form base

    Denormalize a string.

    positional arguments:
      form                  The normalization form for the denormalization. Valid
                            options are: casefold, nfc, nfd, nfkc, nfkd.
      base                  The base normalized string.

    options:
      -h, --help            show this help message and exit
      -m MAXDEPTH, --maxdepth MAXDEPTH
                            Maximum number of reverse normalizations to use for
                            each character.
      -n NUMBER, --number NUMBER
                            Maximum number of results to return.
      -r, --random          Randomize the denormalization.
      -s SEED, --seed SEED  Seed the randomized denormalization.

    charex>


GUI
---
To launch the :mod:`charex` GUI::

    $ charex gui


API
---
To import :mod:`charex` into your Python script to get a summary of a
Unicode character::

    >>> import charex
    >>>
    >>>
    >>> value = 'a'
    >>> char = charex.Character(value)
    >>> print(char.summarize())
    a U+0061 (LATIN SMALL LETTER A)


Common Problems
===============

`ModuleNotFoundError: No module name '_tkinter'` error
------------------------------------------------------
If you get the above error when running :mod:`charex` or its tests, it's
likely your Python install doesn't have :mod:`tkinter` linked. How you
fix it depends upon your Python install. If you are using Python 3.13 
installed with `homebrew` on macOS, you can probably fix it with::

    brew install python-tk@3.13


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
