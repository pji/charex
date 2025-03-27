"""
__init__
~~~~~~~~

Initialization for the :mod:`charex` package.
"""
from charex.charex import (
    Character,
    expand_property,
    expand_property_value,
    filter_by_property,
    get_properties,
    get_property_values
)
from charex.charsets import (
    get_codecs,
    get_description,
    multidecode,
    multiencode
)
from charex.denormal import (
    count_denormalizations,
    denormalize,
    gen_denormalize,
    gen_random_denormalize
)
from charex.escape import escape as escape_text
from charex.escape import get_schemes, reg_escape
from charex.normal import get_forms, normalize, reg_form
