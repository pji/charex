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
part is what's interesting to me, and it's where a lot of fun problems lie.


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
The following features are planned for the v0.2.1 or later releases:

*   Support for more versions of Unicode.
*   Emoji combiner.
*   Basic doctests for all public classes and functions.
*   Web API.
*   Registration for character set codecs.

The list of Unicode properties can be found here: `Index`_

The list of Unihan properties is here: `tr38`_

.. _`Index`: https://www.unicode.org/reports/tr44/tr44-28.html#Property_Index
.. _`tr38`: https://www.unicode.org/reports/tr38/tr38-31.html


Changes in v0.2.3
-----------------
The following are the changes in v0.2.3:

*   Move dependency management to `poetry`.
*   Move package into /src directory.
*   Use `tox` for regression testing.
*   (Started.) Use Unicode version supported by Python version.

    *   Updated the path_map to handle different Unicode versions.
    *   Updated the prop_map to handle different Unicode versions.
    *   Can specify the Unicode version of a `FileCache`.
    *   (Not started.) Create a `FileCache` for the Unicode version
        supported by the running Python on launch.

*   (Started.) Support Unicode 15.0 when running under Python 3.12.

    *   Add Unicode 15.0 files.
    *   Added "kalternatetotalstrokes" property.
    *   Moved "kcihait" property source.
    *   Added "idna2008" property.
    *   (Not started.) Look into UAX9-C2 misleading bidirectional
        ordering of source code spoofing attacks.

*   (Started.) Support Unicode 15.1 when running under Python 3.13.

    *   Add Unicode 15.1 files.
    *   Remove seven Unihan properties.
    
        *   kHKSCS
        *   kIRGDaiKanwaZiten
        *   kKPS0
        *   kKPS1
        *   kKSC0
        *   kKSC1
        *   kRSKangXi
    
    *   Add six Unihan properties.
    
        *   kJapanese
        *   kMojiJoho
        *   kSMSZD2003Index
        *   kSMSZD2003Readings
        *   kVietnameseNumeric
        *   kZhuangNumeric

    *   Add "IDS_Unary_Operator" property.
    *   (Not started.) Add "ID_Compat_Math_Start" property.
    *   (Not started.) Add "ID_Compat_Math_Continue" property.
    *   (Not started.) Add "NFKC_Simple_Casefold" property.
    *   (Not started.) Check if multiple "kPrimaryNumeric" values
        are supported for U+5146 and U+79ED.

*   (Not started.) Return an AttributeError rather than KeyError
    when an attribute doesn't exist.
*   (Not started.) Generate denormalizations for each version.


How Do I Run the Tests?
-----------------------
`charex` is using the `pytest` package for unit testing. It also
comes with a makefile that automates testing. So, to run the
tests:

*   Install `poetry`: `pip install poetry`
*   Install the development dependencies: `poetry install`
*   To run just the unit tests: `make test`
*   To run the full test suite: `make pre`


Common Problems
===============

`ModuleNotFoundError: No module name '_tkinter'` error
------------------------------------------------------
If you get the above error when running `charex` or its tests, it's
likely your Python install doesn't have `tkinter` linked. How you
fix it depends upon your Python install. If you are using Python 3.13 
installed with `homebrew` on macOS, you can probably fix it with::

    brew install python-tk@3.13
