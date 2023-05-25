###
API
###

:mod:`charex` is primarily designed to be used as a command line
script. However, it does have an API if you have some need for
using it that way.


General Character Information
*****************************

.. autoclass:: charex.Character
    :members:


Character Set Information
*************************

.. autofunction:: charex.get_codecs
.. autofunction:: charex.multidecode
.. autofunction:: charex.multiencode


Character Escaping
******************

.. autofunction:: charex.escape_text
.. autofunction:: charex.get_schemes
.. autoclass:: charex.reg_escape


Normalization and Denormalization
*********************************

.. autofunction:: charex.count_denormalizations
.. autofunction:: charex.denormalize
.. autofunction:: charex.gen_denormalize
.. autofunction:: charex.gen_random_denormalize
.. autofunction:: charex.get_forms
.. autofunction:: charex.normalize
.. autoclass:: charex.reg_form
