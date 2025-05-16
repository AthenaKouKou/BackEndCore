"""
This is our interface to our us text data.
We never expect our users to add or delete texts,
so we make no provisions for that.
"""
import backendcore.common.time_fmts as tfmt

from backendcore.data.caching import needs_cache, get_cache

from backendcore.text.fields import (
    EDITOR,
    LAST_EDIT,
    TEXT,
    TITLE,
)

DB = 'textDB'
COLLECT = 'dmmText'
CACHE_NM = COLLECT


def needs_text_cache(fn):
    """
    Should be used to decorate any function that uses datacollection methods.
    """
    return needs_cache(fn, CACHE_NM, DB,
                       COLLECT,
                       key_fld=TITLE,
                       sort_fld=TITLE)


def is_valid(code):
    texts = fetch_dict()
    return code in texts


@needs_text_cache
def fetch_list():
    """
    Fetch all texts: returns a list
    """
    return get_cache(CACHE_NM).fetch_list()


@needs_text_cache
def fetch_dict():
    return get_cache(CACHE_NM).fetch_dict()


def fetch_codes():
    """
    Fetch all text codes
    """
    texts = fetch_dict()
    return list(texts.keys())


TEST_TITLE = 'Some Title'

TEST_TEXT = {
    TITLE: TEST_TITLE,
    TEXT: 'Here are our submission guidelines',
}


@needs_text_cache
def add(text_dict):
    return get_cache(CACHE_NM).add(text_dict)


@needs_text_cache
def delete(title):
    return get_cache(CACHE_NM).delete(title)


@needs_text_cache
def update(title, text, editor):
    update_dict = {}
    update_dict[TEXT] = text
    update_dict[LAST_EDIT] = str(tfmt.today())
    update_dict[EDITOR] = editor
    return get_cache(CACHE_NM).update(title, update_dict)


@needs_text_cache
def fetch_by_key(title):
    """
    Get a single entry by term.
    """
    return get_cache(CACHE_NM).fetch_by_key(title)


def main():
    """
    Run this as a program to see the output formats!
    """
    print("Interactive test of text data module.")
    print(f'{fetch_list()=}')
    print(f'{fetch_codes()=}')


if __name__ == '__main__':
    main()
