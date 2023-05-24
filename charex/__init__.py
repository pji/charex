"""
__init__
~~~~~~~~

Initialization for the :mod:`charex` package.
"""
from charex.charex import Character
from charex.charsets import get_codecs, get_description
from charex.charsets import multidecode, multiencode
from charex.denormal import count_denormalizations, denormalize
from charex.denormal import gen_denormalize, gen_random_denormalize
from charex.escape import get_schemes
from charex.escape import escape as escape_text
from charex.normal import get_forms, normalize
