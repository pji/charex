"""
test_db
~~~~~~~

Unit tests for :mod:`charex.db`.
"""
from charex import db


# Test load_from_archive.
def test_load_from_archive():
    """When given the information for a path as a :class:`charex.db.PathInfo`
    object, return the lines contained in the file as a :class:`tuple`.
    """
    pi = db.PathInfo('Jamo.txt', 'UCD.zip', 'single_value', ';')
    lines = db.load_from_archive(pi)
    assert lines[0] == '# Jamo-14.0.0.txt'
    assert lines[-1] == '# EOF'


# Test load_path_map.
def test_load_path_map():
    """When called, :func:`charex.db.load_path_map` should return a
    :class:`dict` that allows mapping of a Unicode file name to the
    archive that contains it.
    """
    exp = 'UCD.zip'
    path = 'UnicodeData.txt'
    pm = db.load_path_map()
    pi = pm[path]
    assert pi.archive == exp
