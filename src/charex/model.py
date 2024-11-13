"""
model
~~~~~
Data model for :mod:`charex`.
"""
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from json import dump, load
from pathlib import Path
from typing import TypeVar


# Utility data.
@dataclass
class Source:
    """Information on a datafile used by :mod:`charex`.
    
    :param description: A simple English description of the file.
    :param source: The original source address of the file.
    :param date: The date the file was last pulled or updated.
    """
    description: str
    source: str
    date: tuple[int, int, int]


# Collective types.
Sources = dict[str, Source]


# Serialization.
Serializable = Source | Sources
SERIALIZATION_MAP = {cls.__name__: cls for cls in [Source,]}


def deserialize(path: Path) -> Serializable:
    """Deserialize a file of stored data.
    
    :param path: The path to the serialized file.
    :return: The deserialized data.
    :rtype: Serializable
    """
    def object_hook(item):
        if '__class__' not in item:
            return item
        if item['__class__'] not in SERIALIZATION_MAP:
            return item
        cls = SERIALIZATION_MAP[item['__class__']]
        del item['__class__']
        for key in item:
            if isinstance(item[key], list):
                item[key] = tuple(item[key])
        return cls(**item)
    
    with open(path) as fh:
        data = load(fh, object_hook=object_hook)
    return data


def serialize(data: Serializable, path: Path) -> None:
    """Serialize a sequence of dataclasses.
    
    :param data: A collection of dataclasses for serialization to a file.
    :param path: The location of the file for the serialized data.
    :return: None
    :rtype: NoneType
    """
    def serialize_object(o):
        serialized = asdict(o)
        serialized['__class__'] = o.__class__.__name__
        return serialized
    
    result: dict | Sequence | Serializable | None = None
    if isinstance(data, dict):
        result = {k: serialize_object(data[k]) for k in data}
    elif isinstance(data, Sequence):
        result = [serialize_object(o) for o in data]
    else:
        result = serialize_object(data)

    with open(path, 'w') as fh:
        dump(result, fh, indent=4)
