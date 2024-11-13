"""
test_rebuilder
~~~~~~~~~~~~~~
Unit tests for :mod:`util.rebuilder`.
"""
from dataclasses import dataclass
from json import dump, load
from pathlib import Path
from zipfile import ZipFile

import pytest as pt
import requests_mock
from freezegun import freeze_time

from charex import db
from util import rebuilder as rb


# Static configuration data.
DATE = (2024, 11, 12)
TEST_DATA = Path('tests/data')


# Unit tests.
def test_load_versions():
    """When given information for a path as a :class:`charex.db.PathInfo`,
    :func:`charex.db.load_versions` should parse the HTML file at the
    location and return the Unicode versions as a :class:`tuple`.
    """
    path = TEST_DATA / 'enumeratedversions.html'
    versions = rb.load_versions(path)
    assert versions[-1] == db.Version(
        (1, 0, 0),
        db.URL(
            'Unicode 1.0.0',
            'https://www.unicode.org/versions/Unicode1.0.0/',
        ),
        db.URL(
            'Components',
            'https://www.unicode.org/versions/components-1.0.0.html',
        ),
        1991,
        None,
        None
    )
    assert versions[-2] == db.Version(
        (1, 0, 1),
        db.URL(
            'Unicode 1.0.1',
            'https://www.unicode.org/versions/Unicode1.0.0/',
        ),
        db.URL(
            'Components',
            'https://www.unicode.org/versions/components-1.0.1.html',
        ),
        1992,
        None,
        None
    )


def test_pull_data(tmp_path):
    """Given a URL and a path, :func:`util.rebuilder.pull_data` should
    pull the data down from the given URL and save it to the given path.
    """
    exp = '<html><body><p>spam</p></body></html>'
    url = 'http://spam.local/spam.html'
    path = tmp_path / 'spam.html'
    with requests_mock.Mocker() as m:
        m.get(url, text=exp)

        assert rb.pull_data(url, path)

    with open(path) as fh:
        assert fh.read() == exp


def test_serialize(tmp_path):
    """Given a sequence of data classes and a path,
    :func:`util.rebuilder.serialize` should serialize
    the sequence to a JSON file.
    """
    @dataclass
    class Spam:
        spam: int
    
    exp = [{'__class__': 'Spam', 'spam': n} for n in range(3)]
    data = [Spam(item['spam']) for item in exp] 
    path = tmp_path / '_test_serialize.json'
    
    rb.serialize(data, path)
    
    with open(path) as fh:
        assert load(fh) == exp


@freeze_time(f'{DATE[0]}-{DATE[1]}-{DATE[2]}')
def test_update_data(mocker, tmp_path):
    """Given the path to a data sources file, :func:`util.rebuild.update_data`
    should update each of the data sources and then update the dates in
    the data sources file itself.
    """
    exp_spam_file = 'spam.html'
    exp_spam_content = '<html><body><p>spam</p></body></html>'
    exp_denormal_file = 'rev_nfc.json'
    exp_denormal = Path('tests/data/rev_nfc.json').read_text()
    
    mocker.patch(
        'charex.normal.build_denormalization_map',
        return_value=exp_denormal
    )
    tmpdir = Path(tmp_path)
    sources = {
        exp_spam_file: {
            '__class__': 'Source',
            'description': 'spam',
            'source': f'http://spam.local/{exp_spam_file}',
            'date': (1970, 1, 1),
        },
        exp_denormal_file: {
            '__class__': 'Source',
            'description': 'eggs',
            'source': 'form:nfc',
            'date': (1970, 1, 1),
        },
    }
    sources_path = tmpdir / 'sources.json'
    with open(sources_path, 'w') as fh:
        dump(sources, fh)
    with requests_mock.Mocker() as m:
        m.get(sources[exp_spam_file]['source'], text=exp_spam_content)
        
        rb.update_data(tmpdir)
        
    with open(sources_path) as fh:
        data = load(fh)
    for exp in sources:
        assert data[exp]['description'] == sources[exp]['description']
        assert data[exp]['source'] == sources[exp]['source']
        assert data[exp]['date'] == list(DATE)
        
        if sources[exp]['source'].startswith('http'):
            with open(tmpdir / exp) as fh:
                assert fh.read() == exp_spam_content
            
        elif sources[exp]['source'].startswith('form'):
            with ZipFile(tmpdir / 'Denormal.zip') as zh:
                with zh.open(exp) as zch:
                    data = zch.read()
            assert data.decode('utf8') == exp_denormal
