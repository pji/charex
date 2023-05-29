"""
rebuild_data
~~~~~~~~~~~~

Rebuild the data files used by :mod:`charex`. This is a maintenance
script not intended for use beyond maintaining the package.
"""
from datetime import date
from json import dump, load
from pathlib import Path

from requests import get


# Set up values.
today = date.today()
data_path = Path('charex/data')

# Get the list of data files to update.
src_path = data_path / 'sources.json'
with open(src_path) as fh:
    data = load(fh)

# Update each file.
for file in data:
    # Download the file.
    url = data[file]['source']
    resp = get(url)

    # Update the file if the download worked.
    if resp.status_code == 200 and resp.text:
        path = data_path / file
        with open(path, 'w') as fh:
            fh.write(resp.text)

        # Update the date in sources data.
        update = (today.year, today.month, today.day)
        data[file]['date'] = update

# Update the sources data.
path = data_path / 'sources.json'
with open(path, 'w') as fh:
    dump(data, fh, indent=4)
