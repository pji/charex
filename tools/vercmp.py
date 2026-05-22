"""
vercmp
~~~~~~

Compare the Unicode data files for two versions of Unicode and list
the files that are different.
"""
import zipfile as zf
from collections.abc import Generator
from pathlib import Path


PKG_DATA = Path('src/charex/data')


def iter_zip(zpath: zf.Path) -> Generator[str]:
    """Yield the names of the contents of a zip file."""
    for p in zpath.iterdir():
        if p.is_dir():
            for s in iter_zip(p):
                yield f'{p.name}/{s}'
        else:
            yield p.name


def list_files(path: Path | zf.ZipFile) -> list[str]:
    """Get a list of a files in the location."""
    if isinstance(path, Path):
        return [p.name for p in path.iterdir()]
    elif isinstance(path, zf.ZipFile):
        zpath = zf.Path(path)
        return [p for p in iter_zip(zpath)]
    else:
        raise TypeError('Must be a Path or ZipFile.')


def cmp_list(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """Compare two lists of strings."""
    a = sorted(a)
    b = sorted(b)
    result = []
    for a_item in a:
        if a_item in b:
            i = b.index(a_item)
            b.pop(i)
        else:
            result.append((a_item, '>'))
    for b_item in b:
        result.append((b_item, '<'))
    result = sorted(result)
    return result


if __name__ == '__main__':
    file = 'UCD.zip'

    ver_a = 'v15_1'
    a_path = PKG_DATA / ver_a
    a_zip = zf.ZipFile(a_path / file)
    a = list_files(a_zip)

    ver_b = 'v16_0'
    b_path = PKG_DATA / ver_b
    b_zip = zf.ZipFile(b_path / file)
    b = list_files(b_zip)

#     for name in a:
#         print(name)

#     a = ['a', 'b', 'c', 'd', 'e']
#     b = ['a', 'c', 'f', 'd', 'g']

    result = cmp_list(a, b)
    for s in result:
        name, direct = s
        print(direct, name)
