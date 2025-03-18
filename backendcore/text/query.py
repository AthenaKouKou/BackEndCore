"""
This is our interface to some texts data.
"""
from backendcore.data.caching import needs_cache, get_cache

from backendcore.text.fields import (
    CODE,
    NAME,
)

DB = 'testDB'  # dbc.someDB
COLLECT = 'Texts'


def needs_texts_cache(fn):
    """
    Should be used to decorate any function that uses datacollection methods.
    """
    return needs_cache(fn, COLLECT, DB, COLLECT, key_fld=CODE)


def is_valid(code):
    text = fetch_dict()
    return code in text


@needs_texts_cache
def fetch_list():
    """
    Fetch all text: returns a list
    """
    return get_cache(COLLECT).fetch_list()


@needs_texts_cache
def fetch_dict():
    return get_cache(COLLECT).fetch_dict()


@needs_texts_cache
def get_choices():
    return get_cache(COLLECT).get_choices()


def fetch_codes():
    """
    Fetch all texts codes
    """
    choices = get_choices()
    return list(choices.keys())


@needs_texts_cache
def fetch_by_key(term):
    """
    Get a single entry by term.
    """
    return get_cache(COLLECT).fetch_by_key(term)


TEST_CODE = 'GC'

TEST_SAMPLE = {
    CODE: TEST_CODE,
    NAME: 'Region du Callahan le Magnifique',
}


@needs_texts_cache
def add(texts_dict):
    return get_cache(COLLECT).add(texts_dict)


@needs_texts_cache
def delete(reg_code):
    return get_cache(COLLECT).delete(reg_code)


@needs_texts_cache
def update(code, update_dict):
    return get_cache(COLLECT).update(code, update_dict)


def main():
    """
    Run this as a program to see the output formats!
    """
    print("Interactive test of texts data module.")
    print(f'{get_choices()=}')


if __name__ == '__main__':
    main()
