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


def build_map(formkey: str, path: Path) -> bool:
    """Build a denormalization map, returning whether the build was
    successful.
    """
    result = False

    try:
        content = build_denormalization_map(formkey)
        with open(path, 'w') as fh:
            fh.write(content)

        zpath = path.parent / 'Denormal.zip'
        with ZipFile(zpath, 'a') as zf:
            zf.writestr(path.name, content)

        result = True
    except Exception as ex:
        print(f'{type(ex)}({ex})...', end='')

    return result


def get_sources(data_path):
    src_path = data_path / 'sources.json'
    with open(src_path) as fh:
        return load(fh)


def update_14_0():
    # Set up values.
    today = date.today()
    data_path = Path('src/charex/data')
    zpath = data_path / 'Denormal.zip'
    if zpath.exists():
        zpath.unlink()

    # Get the list of data files to update.
    data = get_sources(data_path)
#     src_path = data_path / 'sources.json'
#     with open(src_path) as fh:
#         data = load(fh)

    # Update each file.
    for file in data:
        print(f'Rebuilding {file}...', end='')
        success = False

        # Update the file.
        src = data[file]['source']
        path = data_path / file

        # Download hosted data.
        if src.startswith('http'):
            success = pull_data(src, path)

        # Generate denormalization data.
        elif src.startswith('form'):
            key = src.split(':')[1]
            success = build_map(key, path)

        # Update the date in sources data.
        term = Terminal()
        color = term.red
        if success:
            update = (today.year, today.month, today.day)
            data[file]['date'] = update
            color = term.green
        print(color + f'{success}' + term.normal)

    # Update the sources data.
    path = data_path / 'sources.json'
    with open(path, 'w') as fh:
        dump(data, fh, indent=4)


def update_sources_date(data, file, today, success):
    term = Terminal()
    color = term.red
    if success:
        update = (today.year, today.month, today.day)
        for item in update:
            assert isinstance(item, int)
        data[file]['date'] = update
        color = term.green
    print(color + f'{success}' + term.normal)
    return data


def update_sources(data_path, data):
    path = data_path / 'sources.json'
    with open(path, 'w') as fh:
        dump(data, fh, indent=4)


def update_15_0(
    today=date.today(),
    data_path=Path('src/charex/data/v15_0')
):
    data = get_sources(data_path)
    for file in data:
        print(f'Rebuilding {file}...', end='')
        success = False

        # Update the file.
        src = data[file]['source']
        path = data_path / file

        # Download hosted data.
        if src.startswith('http'):
            success = pull_data(src, path)

        data = update_sources_date(data, file, today, success)
    update_sources(data_path, data)


if __name__ == '__main__':
    # update_14_0()
    update_15_0()
