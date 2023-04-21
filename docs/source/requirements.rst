###################
charex Requirements
###################

The purpose of this document is to detail the requirements for the
:mod:`charex` package. This is an initial take to help with planning.
There may be additional requirements or non-required features added in
the future. Changes may be made in the code that are not reflected here.


Purpose
=======
The purposes of :mod:`charex` are:

*   Be a tool to explore character information,
*   Be a tool for demonstrating how character encoded data works,
*   Provide a reverse lookup for character decomposition for use in
    security testing.


Functional Requirement
======================
The following are the functional requirements for :mod:`charex`. It can:

*   Display the code point for a given series of bits,
*   Display the bits for a given code point,
*   Show the bits for all normalization forms of a given code point,
*   Show all code points that normalize to a given code point,
*   Show escaped versions of a given code point,
*   Show full details for a given code point,
*   Guess the code point for a given text.


Technical Requirements
======================
The following are the technical requirements for :mod:`charset`. It:

*   Supports a list of common character sets,
*   Supports big and little endian byte order,
*   Has a command line interface.
