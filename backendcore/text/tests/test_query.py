from copy import deepcopy

import pytest

import text.query as qry


@pytest.fixture(scope='function')
def temp_text():
    text_dict = deepcopy(qry.TEST_TEXT)
    ret = qry.add(text_dict)
    yield ret
    qry.delete(qry.TEST_TITLE)


def test_fetch_codes(temp_text):
    codes = qry.fetch_codes()
    assert isinstance(codes, list)
    assert qry.TEST_TITLE in codes


def test_fetch_list(temp_text):
    texts = qry.fetch_list()
    assert isinstance(texts, list)
    assert len(texts) > 0


def test_fetch_dict(temp_text):
    texts = qry.fetch_dict()
    assert isinstance(texts, dict)
    assert len(texts) > 0


NEW_TEXT = 'Some new text'
NEW_ED = 'new@ed.com'


def test_update_text(temp_text):
    qry.update(qry.TEST_TITLE, NEW_TEXT, NEW_ED)
    new_rec = qry.fetch_by_key(qry.TEST_TITLE)
    assert new_rec[qry.TEXT] == NEW_TEXT
    assert new_rec[qry.EDITOR] == NEW_ED


def test_update_text_bad_title(temp_text):
    NEW_TEXT = 'Some new text'
    with pytest.raises(ValueError):
        qry.update('Not an existing title', NEW_TEXT, NEW_ED)
