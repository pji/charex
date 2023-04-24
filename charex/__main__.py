"""
__main__
~~~~~~~~

Mainline for :mod:`charex`.
"""
from sys import argv

from charex.charex import Character


c = argv[1]
char = Character(c)
forms = ('nfc', 'nfd', 'nfkc', 'nfkd')
for form in forms:
    values = char.reverse_normalize(form)
    points = [Character(value) for value in values]
    print(f'{form.upper()}')
    for point in points:
        print(f'\t{point!r}')
