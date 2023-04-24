"""
__main__
~~~~~~~~

Mainline for :mod:`charex`.
"""
from sys import argv

from charex.charex import Character


c = argv[1]
char = Character(c)
print(f'NFKC: {char.reverse_normalize("nfkc")}')
