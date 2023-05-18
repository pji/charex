###########################
Unicode Normalization Forms
###########################

The following is a brief overview of Unicode normalization as of
Unicode 14.0.0, which is the version supported by Python's
:mod:`unicodedata`.


The Problem
===========
Probably the simplest way for native English speakers to think about
the problem is to think about the problem of case sensitivity.

Consider the following words:

*   first
*   First
*   FIRST

Are they the same word? It depends. Usually capitalization doesn't
change meaning in English, but:

*   `First` could be someone's last name or OS autocapitalization.
*   `FIRST` could be the "Forum of Incident Response and Security Teams"
    or an accidental caps lock.
*   `first` could be the name of either the person or the group as
    typed by someone who doesn't do capitalization.

Sometimes `f` is the same thing as `F`. Sometimes they are different.

Unicode isn't English. For Unicode, those are two different characters:

*   `f U+0066 (LATIN SMALL LETTER F)`
*   `F U+0046 (LATIN CAPITAL LETTER F)`

However, English speakers don't speak Unicode. English speakers speak
English. And, English speakers get really frustrated when they spend
all day trying to figure out why their computer isn't obeying them only
to discover it was because they were typing `first` instead of `First`.

On the flip-side, if the computer needs to treat `f` and `F` the same,
it gets really complicated to check every time for both of them. Things
that are really complicated are also things that break easily. So,
it's much easier for the computer if you just decide which of the two
forms you want up front and transform them into the same form before
you do any processing on them.

To summarize:

*   Sometimes different characters have different meanings.
*   Sometimes different characters have the same meanings.
*   Computers are bad at having different things mean the same thing.
*   So, when different characters mean the same thing, it's best to
    transform them into the same thing.

That process of transforming different things with the same meaning into
the same thing is :dfn:`normalization`.


How to Normalize?
=================
Broadly, there are two different axes to consider when normalizing
Unicode strings:

*   Composition
*   Compatibility


Composition
-----------
This boils down to the question: should combining marks be kept as part
of the character or should they be split into separate characters?

While it's rare to see combining marks in English, they can exist.
You'll see them in loan words from other languages, like the mark
above the letters E in "résumé." You will also occasionally see a
diaeresis used when a prefix ending in a vowel is attached to a word
starting with a vowel, such as "coöperation."

The options for composition are:

*   Composed: Use the combined form of the character.
*   Decomposed: Split all the marks into individual characters.

So in the case of the "é" character:

*   Composed: U+00E9 `é`
*   Decomposed: U+0065 `e` + U+0301 `´`

Composition normalizations are usually lossless. The composed and
decomposed forms are just two different ways to store the same
semantic unit. In most cases, you can flip back and forth between them
without losing data.


Compatibility
-------------
This boils down to the question: should human intuition that the two
characters are the same be recognized?


Further Reading
===============
The following provide more information on normalization:

*   `Unicode_Normalization_Forms`_
*   `Unicode_Normalization_FAQ`_
*   `UTR36 Unicode Security Considerations`_
*   `Input_Validation_and_Data_Sanitization`_

.. _Unicode_Normalization_Forms: https://www.unicode.org/reports/tr15/tr15-51.html#Introduction
.. _Unicode_Normalization_FAQ: https://unicode.org/faq/normalization.html
.. _`UTR36 Unicode Security Considerations`: https://unicode.org/reports/tr36/
.. _Input_Validation_and_Data_Sanitization: https://wiki.sei.cmu.edu/confluence/display/java/Input+Validation+and+Data+Sanitization

