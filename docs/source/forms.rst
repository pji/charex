###########################
Unicode Normalization Forms
###########################

The following is a brief overview of Unicode normalization as of
Unicode 14.0.0, which is the version supported by Python's
:mod:`unicodedata`.


Why Normalize?
==============
The main reason to normalize is to make it easier to match string
comparison results to human needs and expectations. Let's take, for
example, the following two characters:

*   Ω (U+03A9 GREEK CAPITAL LETTER OMEGA)
*   Ω (U+2126 OHM SIGN)

The two characters look the same. You would make the same motions when
writing them by hand. The vectors to draw the glyphs are the same. They
are, to our eye, the same character.

But, there is a semantic difference. The first is a letter you use when
writing words with the greek alphabet. The other is a symbol you use
when writing a measurement of electrical resistance. They are semantically
different characters.

But, there is nuance even there. It's not a coincidence the unit symbol
for electrical resistance looks like a Greek capital letter omega. The
ohm symbol was defined as the Greek capital letter omega. So, while they
are semantically different, it's not really wrong to use them
interchangeably.

We end up with a situation where different things sometimes need to be
considered the same thing. Computers are bad at that. It's easier if
we just decide upfront whether our program needs for those characters
be the same or different.

The process of transforming two different things that are equal into
the same thing is, for the purposes of this discussion, normalization.


Further Reading
===============
The following provide more information on normalization:

*   `Unicode_Normalization_Forms`_
*   `Unicode_Normalization_FAQ`_
*   `Input_Validation_and_Data_Sanitization`_

.. _Unicode_Normalization_Forms: https://www.unicode.org/reports/tr15/tr15-51.html#Introduction
.. _Unicode_Normalization_FAQ: https://unicode.org/faq/normalization.html
.. _Input_Validation_and_Data_Sanitization: https://wiki.sei.cmu.edu/confluence/display/java/Input+Validation+and+Data+Sanitization

