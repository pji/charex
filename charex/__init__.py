"""
__init__
~~~~~~~~

Initialization for the :mod:`charex` package.
"""
from charex.charex import Character
from charex.charsets import get_codecs, multidecode, multiencode
from charex.denormal import count_denormalizations, denormalize
from charex.escape import get_schemes
from charex.escape import escape as escape_text
from charex.normal import get_forms, normalize
