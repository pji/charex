"""
build_denormal_maps
~~~~~~~~~~~~~~~~~~~

Rebuild the denormalization maps, using pytest and tox to handle
multiple Python versions.
"""
from datetime import date
from json import dumps, loads
from pathlib import Path
from zipfile import ZipFile

from charex.db import cache
from charex.normal import build_denormalization_map


FORMS = ('casefold', 'nfc', 'nfd', 'nfkc', 'nfkd',)
PKG_DATA = Path('src/charex/data/')


def build_map(version: str, form: str, file: str, zpath: Path) -> bool:
    """Build a denormalization map, returning whether the build was
    successful.
    """
    result = False
    try:
        content = build_denormalization_map(form)
        with ZipFile(zpath, 'a') as zf:
            zf.writestr(file, content)

        result = True
    except Exception as ex:
        print(f'{type(ex)}({ex})...', end='')

    return result


def update_source_date(version, updated_file):
    today = date.today()
    update_date = (today.year, today.month, today.day)
    
    path = PKG_DATA / version / 'sources.json'
    text = path.read_text()
    data = loads(text)
    
    data[updated_file]['date'] = update_date
    
    updated_text = dumps(data, indent=4)
    path.write_text(updated_text)


version = cache.version
zpath = PKG_DATA / version / 'Denormal.zip'
if zpath.exists():
    zpath.unlink()

for form in FORMS:
    file = f'rev_{form}.json'
    success = build_map(version, form, file, zpath)
    
    msg = f'{version} {form}: '
    if success:
        update_source_date(version, file)
        print(msg + 'SUCCESS')
    else:
        print(msg + 'FAIL')


# class TestBuildMaps:
#     def test_casefold(self):
#         version = cache.version
#         form = 'casefold'
#         file = f'rev_{form}.json'
#         success = build_map(version, form, file, PKG_DATA)
#         if success:
#             update_source_date(version, file)
# 
#     def test_nfc(self):
#         form = 'nfc'
#         file = f'rev_{form}.json'
#         success = build_map(file, PKG_DATA)
# 
#     def test_nfd(self):
#         form = 'nfd'
#         file = f'rev_{form}.json'
#         success = build_map(version, form, file, PKG_DATA)
#         if success:
#             update_source_date(version, file)
# 
#     def test_nfkc(self):
#         form = 'nfkc'
#         file = f'rev_{form}.json'
#         success = build_map(version, form, file, PKG_DATA)
#         if success:
#             update_source_date(version, file)
# 
#     def test_nfkd(self):
#         form = 'nfkd'
#         file = f'rev_{form}.json'
#         success = build_map(version, form, file, PKG_DATA)
#         if success:
#             update_source_date(version, file)
