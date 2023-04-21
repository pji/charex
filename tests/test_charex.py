"""
test_charex
~~~~~~~~~~~
"""
from charex import charex as c


# Transformer tests.
def test_tranformer_init():
    """An instance of Transformer can be initialized with default
    values.
    """
    act = c.Transformer()
    assert act.charset == 'utf_8'


def test_tranformer_ascii_bin_to_char():
    """Given a binary number as a string, :meth:`Transformer.bin_to_char`
    should return the code point for that binary number.
    """
    exp = 'a'
    tf = c.Transformer()
    bin = '1100001'
    act = tf.bin_to_char(bin)
    assert exp == act
