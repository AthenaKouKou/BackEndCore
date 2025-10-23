"""
This type is intended to handle immutable dictionaries, that map between some
code and its meaning. We have found these come up frequently in our
work.
"""
from copy import deepcopy


class Map:
    def __init__(self, name: str, data: dict):
        # `name` can enable us to one day create lookup for
        # maps created in advance of use.
        if not isinstance(name, str):
            raise TypeError(f'name must be a str: {type(name)}')
        self.name = name
        # Create a copy to ensure external changes don't affect it:
        self.map = dict(data)

    def __getitem__(self, key):
        return self.map[key]

    def __len__(self) -> int:
        return len(self.map)

    def __iter__(self):
        return iter(self.map)

    def get_name(self):
        return self.name

    def get_choices(self) -> dict:
        return deepcopy(self.map)  # prevent changing the map!

    def is_valid(self, code) -> bool:
        return code in self.map

    def get(self, code, default=None):
        return self.map.get(code, default)


class BiMap(Map):
    def __init__(self, name, data):
        super().__init__(name, data)
        self.rev_map = {}
        for key, val in self.map.items():
            try:
                hash(key)
            except TypeError:
                raise TypeError(f'{val=} in BiMap is not hashable.')
            self.rev_map[val] = key

    def is_rev_valid(self, val) -> bool:
        print(f'{val=}; {self.rev_map=}')
        return val in self.rev_map

    def rev_get(self, val, default=None):
        return self.rev_map.get(val, default)
