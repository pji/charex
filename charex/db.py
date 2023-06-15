"""
db
~~

Tools for reading the Unicode database and related information.
"""
from dataclasses import dataclass
from importlib.resources import as_file, files
from json import load
from zipfile import ZipFile


# Database configuration.
PKG_DATA = files('charex.data')
FILE_PATH_MAP = 'path_map.json'


# Data record structures.
@dataclass
class PathInfo:
    path: str
    archive: str
    kind: str
    delim: str


# Common data types.
Content = tuple[str, ...]
PathMap = dict[str, PathInfo]


# Basic file reading.
def load_path_map() -> PathMap:
    """Load the map of Unicode data files to the archive they are
    stored in.
    """
    path = PKG_DATA / FILE_PATH_MAP
    fh = path.open()
    json = load(fh)
    fh.close()
    return {key: PathInfo(*json[key]) for key in json}


def load_from_archive(info: PathInfo, codec: str = 'utf8') -> Content:
    """Read data from a zip archive."""
    path = PKG_DATA / info.archive
    with as_file(path) as sh:
        with ZipFile(sh) as zh:
            with zh.open(info.path) as zch:
                blines = zch.readlines()
    lines = [bline.decode(codec) for bline in blines]
    return tuple(line.rstrip() for line in lines)
