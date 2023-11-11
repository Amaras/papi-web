"""A `ConfigReader`-like reader for TOML-based config files"""

from tomllib import load, loads
from pathlib import Path
from collections import UserDict
from typing import Self


class TOMLConfig(UserDict):
    """A dictionary-like class that allows recursive dotted access

    >>> data = TOMLConfig({'event': {'name' : 'test'}})
    >>> data['event']
    {'name': 'test'}

    >>> data['event.name']
    test
    """

    def __getitem__(self, key):
        # NOTE(Amaras) The aim is to partially reproduce the behaviour of
        # ConfigParser: allow dotted support for keys and sections
        try:
            result = self.data[key]
            if isinstance(result, dict):
                result = self.__class__(result)
            return result
        except KeyError:
            result = self.data
            parts = key.split('.')
            previous = []
            for index, part in enumerate(parts):
                try:
                    result = result[part]
                    if isinstance(result, dict):
                        result = TOMLConfig(result)
                except KeyError as e:
                    print(f"Unknown section: {part}")
                    raise
                except TypeError:
                    raise KeyError(f"{'.'.join(previous)}") from None
                else:
                    previous.append(part)
            return result


class TOMLReader:
    def __init__(self, file: Path | None = None):
        self.file = file
        if file is None:
            self.config = TOMLConfig({})
            return
        with open(file, 'rb') as f:
            self.config = TOMLConfig(load(f))

    @classmethod
    def from_str(cls, value: str) -> Self:
        instance = cls(file=None)
        instance.config = TOMLConfig(loads(value))
        return instance


if __name__ == '__main__':
    config = TOMLReader('../export-data/events/france-rapide.toml').config
    print(config['event.name'])
