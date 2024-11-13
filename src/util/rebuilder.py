"""
rebuilder
~~~~~~~~~
Tools for rebuilding the unicode data for :mod:`charex`.
"""
import datetime as dt
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from json import dump
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse
from zipfile import ZipFile

from bs4 import BeautifulSoup, Tag
from requests import get

from charex import db
from charex import model as m
from charex.normal import build_denormalization_map


# Configuration.
PKG_DATA = Path('src/charex/data')


# Typing.
Serializable = db.Version


# Exceptions.
class UnrecognizeableVersionEnumerationError(ValueError):
    """The Unicode enumerated versions file could not be parsed."""


# Functions.
def build_map(formkey: str, path: Path) -> bool:
    """Build a denormalization map, returning whether the build was
    successful.
    """
    result = False

    try:
        content = build_denormalization_map(formkey)
        zpath = path / 'Denormal.zip'
        with ZipFile(zpath, 'a') as zf:
            zf.writestr(f'rev_{formkey}.json', content)
        result = True
    
    except Exception as ex:
        print(f'{type(ex)}({ex})...', end='')

    return result


def build_version_from_row(row: Tag) -> db.Version:
    """Extract version data from a table row."""
    cells = row.find_all('td')
    
    docs_cell = cells[0]
    comps_cell = cells[1]
    year_cell = cells[2]
    release_cell = cells[3]
    other_cell = cells[4]
    
    a = docs_cell.a
    v_string = a.string.split()[-1]
    v = tuple(int(n) for n in v_string.split('.'))
    docs = db.URL(a.string.strip(), a['href'])
    
    a = comps_cell.a
    comps = db.URL(a.string.strip(), a['href']) if a else None
    
    year_str = year_cell.string.strip()
    year = int(year_str) if year_str else None
    
    links = release_cell.find_all('a')
    releases = None
    if links:
        releases = tuple(db.URL(a.string.strip(), a['href']) for a in links)
    
    a = other_cell.a
    other = db.URL(a.string.strip(), a['href']) if a else None
    
    return db.Version(
        version=v,
        documentation=docs,
        components=comps,
        year=year,
        release=releases,
        other=other
    )


def load_versions(path: Path) -> tuple[db.Version, ...]:
    """Load the list of Unicode versions from the given file."""
    versions: list[db.Version] = []
    
    with open(path) as fh:
        text = fh.read()
    
    soup = BeautifulSoup(text, features='html.parser')
    if not soup.body:
        msg = f'Could not find body tag of {path}.'
        raise UnrecognizeableVersionEnumerationError(msg)
    else:
        table = soup.body.find(class_='subtle')
        if not isinstance(table, Tag):
            raise UnrecognizeableVersionEnumerationError('Cannot happen.')
        rows = table.find_all('tr')
        return tuple(build_version_from_row(row) for row in rows[2:])


def pull_data(url: str, path: Path) -> bool:
    """Pull the data from the given URL, returning whether the
    pull was successful.
    
    :param url: The URL to pull data from.
    :param path: The path to save the data to.
    :return: Whether the request was successful as a :class:`bool`.
    :rtype: bool
    """
    result = False

    try:
        resp = get(url)
        if resp.status_code == 200 and resp.text:
            if url.endswith('.zip'):
                with open(path, 'wb') as fh:
                    fh.write(resp.content)
            else:
                with open(path, 'w') as fh:
                    fh.write(resp.text)
            result = True
    except Exception as ex:
        print(f'{type(ex)}({ex})...', end='')

    return result


def serialize(data: Sequence[Serializable], path: Path) -> None:
    """Serialize a sequence of dataclasses.
    
    :param data: A collection of dataclasses for serialization to a file.
    :param path: The location of the file for the serialized data.
    :return: None
    :rtype: NoneType
    """
    result = []
    for item in data:
        serialized = asdict(item)
        serialized['__class__'] = item.__class__.__name__
        result.append(serialized)
    with open(path, 'w') as fh:
        dump(result, fh, indent=4)


def update_data(path: Path = PKG_DATA) -> None:
    """Update the data sources for :mod:`charex`."""
    # Preparation.
    zpath = path / 'Denormal.zip'
    if zpath.exists():
        zpath.unlink()
    
    # Get the list of sources.
    sources = m.deserialize(path / 'sources.json')
    if isinstance(sources, dict):
        sources = {
            k: sources[k] for k in sources
            if isinstance(sources[k], m.Source)
        }
    else:
        raise TypeError('Bad data in sources.json.')
    
    # Process each source.
    done = {}
    today = dt.date.today()
    for name in sources:
        source = sources[name]
        print(name)
        if source.source.startswith('http'):
            if pull_data(source.source, path / name):
                done[name] = m.Source(
                    source.description,
                    source.source,
                    (today.year, today.month, today.day,)
                )
            else:
                done[name] = source
        
        elif source.source.startswith('form'):
            key = source.source.split(':')[1]
            if build_map(key, path):
                done[name] = m.Source(
                    source.description,
                    source.source,
                    (today.year, today.month, today.day,)
                )
            else:
                done[name] = source
    
    # Write out the updated source list.
    m.serialize(done, path / 'sources.json')
    

# Data rebuild script.
def rebuild_data() -> None:
    """Core script to rebuild the Unicode data for :mod:`charex`."""
    # Rebuild version.
    version_src = m.Source(
        description='Current released versions of Unicode.',
        source='https://www.unicode.org/versions/enumeratedversions.html',
        date=(1970, 1, 1)
    )
    with TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        tmppath = tmpdir / get_file_from_url(version_src.source)
        pull_data(version_src.source, tmppath)
        versions = load_versions(tmppath)
    serialize(versions, PKG_DATA / 'versions.json')


# Utility functions.
def get_file_from_url(s: str) -> str:
    """Get the filename from a URL."""
    url = urlparse(s)
    return url.path.split('/')[-1]


if __name__ == '__main__':
    update_data()
    rebuild_data()
