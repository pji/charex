"""
rebuild_data
~~~~~~~~~~~~

Rebuild the data files used by :mod:`charex`. This is a maintenance
script not intended for use beyond maintaining the package.
"""
from blessed import Terminal
from datetime import date
from json import dump, load
from pathlib import Path
from zipfile import ZipFile

from charex.normal import build_denormalization_map
from requests import get


# Configuration.
COMMON_FILES = {
    "entities.json": {
        "description": "List of HTML Entities.",
        "source": "https://html.spec.whatwg.org/entities.json",
    },
}
PKG_DATA = Path('src/charex/data/')
VERSIONS = {
    '3.11': 'v14_0',
    '3.12': 'v15_0',
    '3.13': 'v15_1',
}


def get_sources(data_path):
    src_path = data_path / 'sources.json'
    with open(src_path) as fh:
        return load(fh)


def pull_data(url: str, path: Path) -> bool:
    """Pull the data from the given URL, returning whether the
    pull was successful.
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


def update_sources_date(data, file, today, success):
    term = Terminal()
    color = term.red
    if success:
        update = (today.year, today.month, today.day)
        for item in update:
            assert isinstance(item, int)
        data[file]['date'] = update
        color = term.green
    msg = 'SUCCESS' if success else 'FAIL'
    print(color + f'{msg}' + term.normal)
    return data


def update_sources(data_path, data):
    path = data_path / 'sources.json'
    with open(path, 'w') as fh:
        dump(data, fh, indent=4)


def update_status(success):
    term = Terminal()
    color = term.red
    if success:
        color = term.green
    msg = 'SUCCESS' if success else 'FAIL'
    print(color + f'{msg}' + term.normal)


def update_unicode_version(
    today=date.today(),
    version='3.11'
):
    data_path = PKG_DATA / VERSIONS[version]
    data = get_sources(data_path)

    for file in data:
        success = False

        # Update the file.
        src = data[file]['source']
        path = data_path / file

        # Download hosted data.
        if src.startswith('http'):
            print(f'Downloading {file}...', end=' ')
            success = pull_data(src, path)

        # Ignore everything else.
        else:
            continue

        # Update the date in sources data.
        data = update_sources_date(data, file, today, success)

    # Update the sources data.
    update_sources(data_path, data)


if __name__ == '__main__':
    today = date.today()
    
    for name in COMMON_FILES:
        print(f'Downloading {name}...', end=' ')
        path = PKG_DATA / name
        src = COMMON_FILES[name]['source']
        success = pull_data(src, path)
        update_status(success)
    
    for version in VERSIONS:
        print(f'Updating {version}.')
        update_unicode_version(today, version)
        print(f'{version} updated.')
        print()
