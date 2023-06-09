"""
__init__
~~~~~~~~

Initialization for the :mod:`charex` package.
"""
from charex.charex import (
    Character, filter_by_property, get_properties, get_property_values,
    expand_property, expand_property_value
)
from charex.charsets import get_codecs, get_description
from charex.charsets import multidecode, multiencode
from charex.denormal import count_denormalizations, denormalize
from charex.denormal import gen_denormalize, gen_random_denormalize
from charex.escape import get_schemes
from charex.escape import escape as escape_text
from charex.escape import reg_escape
from charex.normal import get_forms, normalize, reg_form
