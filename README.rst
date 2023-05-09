######
charex
######

`charex` is a Unicode and character set explorer for understanding
issues with character set translation and Unicode normalization.


Why Did I Make This?
====================
I find the ambiguity of text data interesting. In memory its all ones
and zeros. There is nothing inherent to the data that makes `0x20` mean
a space character, but we've mostly agreed that it does. That "mostly"
part is what's interesting to me, and where a lot of fun problems lie.


How Do I Use This?
==================
Right now, the best way to use it is to clone the repository. Then in
the root of the repository, run `charex` as a module::

    python -m charex

That will bring you to the `charex` shell::

    Welcome to the charex shell.
    charex>

From here you can type `?` to see the list of available commands::

    Welcome to the charex shell.
    charex> ?

    Documented commands (type help <topic>):
    ========================================
    EOF  cd  ce  cl  ct  dn  dt  es  help  rd  xt

    charex>

And then type `help` then a name of one of the commands to learn what
it does::

    charex> help dn
    NAME
        dn - denormalize a string

    SYNOPSIS
        dn {form} {base} [{maxdepth}]

    DESCRIPTION
        The parameters are as follows:

        form        The Unicode normalization form for the denormalization.
                    The valid values are: NFC, NFD, NFKC, NFKD.

        base        The string to denormalize.

        maxdepth    (Optional.) How many denormalizations to use per character.
                    This can be used to reduce the number of denormalizations
                    for a string into a manageable subset of the total number
                    of denormalizations.

    charex>

A quick summary of the available commands:

*   cd: Decode a given hex string into all registered character sets.
*   ce: Get the address for a character in the registered character sets.
*   cl: List the registered character sets.
*   ct: Count denormalization results.
*   dn: Denormalize a string.
*   dt: Get character details.
*   es: Escape a string.
*   help: Get the list of commands.
*   rd: Denormalize a string and return random results.
*   xt: Exit the charex shell.
