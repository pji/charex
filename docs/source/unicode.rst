#######
Unicode
#######

The purpose of this document is to give a brief introduction to
Unicode and the problem it is trying to solve.


The Problem
===========

*   Computers are, essentially, zappy rocks.
*   Those zaps can be used to represent binary numbers.
    *   If there is a zap, we say it's a one.
    *   If there is no zap, we say it's a zero.
*   But, most humans don't communicate in binary.
*   Humans communicate with language.
*   For at least 5,000 years, humans have been using written symbols to
    store language.
*   To work for humans, computers need to work with written language.
*   To work with written language, that language needs to be translated
    into binary numbers, which are then translated into zaps.
*   How we do that translation is arbitrary; it doesn't matter to the 
    computer whether the character `A` is `0b01100001` or `0b11000001`.
*   However, if the humans don't agree on how to do the translation,
    then they can't use the computer to communicate with each other.

This was the problem in the late twentieth century when Unicode was
created.

*   Translation from written language to binary was done with character
    sets.
*   Character sets were usually created by operating system developers.
*   Moving data from one operating system to another could cause that
    data to be mistranslated.
*   A character set also didn't cover all human writing needs, leading
    to humans employing very fragile hacks to try to communicate things
    not covered.

That situation is what Unicode is trying to solve by being a single
standard that all humans can agree on for translating all written
communication into binary numbers.


How Unicode Has Tried to Solve the Problem
==========================================
Unicode attempts to solve the problem by:

*   Pulling groups with a stake in solving the problem, primarily
    software manufacturers, into a consortium, the Unicode Consortium,
    to get agreement on how to do the translation.
*   Assign every every grapheme or grapheme-like unit a unique address
    within the standard called a :dfn:`code point`.

What is a "grapheme"? A :dfn:`grapheme` is the smallest unit that affects
meaning within a writing system. In modern English, the most common ones
are going to be things we thing of as characters: letters, numbers, and
punctuation. However, something we often think of as a single character,
such as the `é` in `résumé`, can consist of multiple graphemes, in this
case the letter `e` and the accent `´`.


Beyond Code Points
==================
The original idea was to get everyone together to agree on a code point
for every character. It turns out, there is more needed to handle human
language than just giving a number to every character. You also have to:

*   Know what direction the text flows,
*   Understand the order they should be sorted in depending on the
    language,
*   Understand how to format numbers and dates,
*   Solve security problems created when similar looking characters
    have different code points.

This has caused the Unicode standard to grow beyond just being a mapping
between code points and the graphemes they represent into a general
database for translating human written languages into computer
representations.


Further Reading
===============
The following provide more information on Unicode:

*   `What Is Unicode`_
*   `Unicode\: A Sea Change`_
*   `Unicode Technical Site`_
*   `Wikipedia Unicode`_

.. _What Is Unicode: https://unicode.org/standard/WhatIsUnicode.html
.. _Unicode\: A Sea Change: http://www.unicode.org/press/seachange.html
.. _Unicode Technical Site: https://unicode.org/main.html
.. _Wikipedia Unicode: https://en.wikipedia.org/wiki/Unicode
