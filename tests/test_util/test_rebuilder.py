"""
test_rebuilder
~~~~~~~~~~~~~~
Unit tests for :mod:`util.rebuilder`.
"""
from dataclasses import dataclass
from json import load
from pathlib import Path

import requests_mock

from charex import db
from util import rebuilder as rb


# Static configuration data.
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
