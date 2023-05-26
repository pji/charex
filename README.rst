######
charex
######

`charex` is a Unicode and character set explorer for understanding
issues with character set translation and Unicode normalization.


Why Did I Make This?
====================
I find the ambiguity of text data interesting. In memory it's all ones
and zeros. There is nothing inherent to the data that makes `0x20` mean
a space character, but we've mostly agreed that it does. That "mostly"
part is what's interesting to me, and where a lot of fun problems lie.


How Do I Use This?
==================
It's in PyPI, so you can install it with `pip`, as long as you are
using Python 3.11 or higher::

    pip install charex

`charex` has four modes of operation:

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

That will bring you to the `charex` shell::

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
To launch the `charex` GUI::

    $ charex gui


API
---
To import `charex` into your Python script to get a summary of a
Unicode character::

    >>> import charex
    >>>
    >>>
    >>> value = 'a'
    >>> char = charex.Character(value)
    >>> print(char.summarize())
    a U+0061 (LATIN SMALL LETTER A)


What Is Left To Do?
-------------------
The following features are planned for the v0.1.1 or later releases:

*   Basic doctests for all public classes and functions.
*   Registration for character set codecs.
*   Small text transformer.
*   Emoji combiner.
*   Unicode category explorer.
*   Tool for rebuilding data files.
*   Support for more versions of Unicode.
*   Web API.
*   Accept lower case u for character point prefix.


How Do I Run the Tests?
-----------------------
`charex` is using the `pytest` package for unit testing. It also
comes with a makefile that automates testing. So, to run the
tests:

*   Install `pipenv`: `pip install pipenv`
*   Install the development dependencies: `pipenv install --dev`
*   To run just the unittests: `make test`
*   To run the full test suite: `make pre`
