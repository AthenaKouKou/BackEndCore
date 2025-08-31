"""
api_key.py: handles api key authorization.

We're going to start this module out real simple.
We can make it fancier later.
"""

MIN_KEY_LEN = 16

keys = []


def clear_keys():
    global keys
    keys = []


def num_keys():
    return len(keys)


def add(key: str):
    if not isinstance(key, str):
        raise TypeError(f'Bad type for key: {type(key)}')
    if len(key) < MIN_KEY_LEN:
        raise ValueError(f'{key} too short')
    keys.append(key)


def exists(key: str):
    return key in keys
