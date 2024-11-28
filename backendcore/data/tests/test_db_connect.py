"""
This module tests our code for database connectivity.
For the moment, the tests will assume MongoDB.
"""
import random
from copy import deepcopy

from unittest.mock import patch
import pytest

import backendcore.data.db_connect as dbc
import backendcore.data.databases.mongo_connect as mdb

TEST_DB = 'test_db'
TEST_COLLECT = 'test_collect'

RECS_TO_TEST = 10  # 10 is arbitrary!

DEF_FLD = 'fld0'
DEF_VAL = 'def_val'

DEF_PAIR = {DEF_FLD: DEF_VAL}

LIST_FLD = 'a_list'

NEW_FLD = 'fld1'
NEW_VAL = 'flooby!'

BAD_VAL = "Scooby-dooby-doo!"

BIG_INT = 10**32

MONGO_DB_LOC = 'backendcore.data.databases.mongo_connect'
MONGO_DB_OBJ = f'{MONGO_DB_LOC}.MongoDB'


def rand_fld_val():
    """
    We should only get a duplicate every billion or so tests.
    """
    return str(random.randint(0, BIG_INT))


@patch(f'{MONGO_DB_OBJ}.read_one', autospec=True, return_value={})
def test_read_one_no_filter(mock_read_one):
    """
    Tests that a fetch with no filter retrieves the rec we inserted
    in the fixture.
    """
    rec = dbc.read_one(TEST_DB, TEST_COLLECT, filters={})
    assert rec is not None


@patch(f'{MONGO_DB_OBJ}.read_one', autospec=True, return_value=None)
def test_read_one_bad_filter(a_doc):
    """
    Tests that a fetch with a bad filter fails.
    """
    rec = dbc.read_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert rec is None


@patch(f'{MONGO_DB_OBJ}.read_one', autospec=True, return_value={})
def test_read_one_good_filter(a_doc):
    """
    Tests that a fetch with a good filter works.
    """
    rec = dbc.read_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert rec is not None


@patch(f'{MONGO_DB_OBJ}.fetch_by_id', autospec=True, return_value={})
def test_fetch_by_id(a_doc):
    ret = dbc.fetch_by_id(TEST_DB, TEST_COLLECT, a_doc)
    assert ret is not None


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_del_by_id(new_doc):
    rec1 = dbc.read_one(TEST_DB, TEST_COLLECT)
    rec_id = rec1[str(dbc.DB_ID)]
    dbc.del_by_id(TEST_DB, TEST_COLLECT, rec_id)
    assert dbc.fetch_by_id(TEST_DB, TEST_COLLECT, rec_id) is None


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_update_fld(a_doc):
    unique_val = rand_fld_val()
    dbc.update_fld(TEST_DB, TEST_COLLECT, DEF_PAIR,
                   DEF_FLD, unique_val)
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) == 1


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_update_doc(a_doc):
    unique_val = rand_fld_val()
    dbc.update_doc(TEST_DB, TEST_COLLECT, DEF_PAIR,
                   {DEF_FLD: unique_val, LIST_FLD: ['something']})
    recs = dbc.select(TEST_DB, TEST_COLLECT,
                      filters={DEF_FLD: unique_val, LIST_FLD: ['something']})
    assert len(recs) == 1


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_select_no_filter(some_docs):
    """
    This should return all records in a collection.
    We test with >= since someone may have left other docs
    in our test_db.
    """
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={})
    assert len(recs) >= RECS_TO_TEST


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_select_w_filter(some_docs):
    """
    This should return all records in a collection matching the
    filter.
    This record should be unique except for a 1 in BIG_INT
    chance. Enough for our lifetimes.
    """
    unique_val = rand_fld_val()
    dbc.create(TEST_DB, TEST_COLLECT, {DEF_FLD: unique_val})
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) == 1


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_del_one_that_exists(a_doc):
    """
    Make sure deleting a doc that exists deletes 1 record.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert result.deleted_count == 1


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_del_one_that_dont_exist(a_doc):
    """
    Make sure deleting a doc that doesn't exist deletes 0 records.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert result.deleted_count == 0


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_del_many(a_doc):
    """
    Make sure deleting many docs leaves none behind.
    """
    dbc.del_many(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert dbc.read_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR) is None


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_delete_success(a_doc):
    """
    Make sure that deleted one can properly detect if a record has been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert dbc.delete_success(result) == True


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_delete_no_success(a_doc):
    """
    Make sure that deleted one can properly detect if a record has not been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert dbc.delete_success(result) == False


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_num_deleted_single(a_doc):
    """
    Make sure that num_deleted can properly detect if a single record has been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert dbc.num_deleted(result) == 1


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_num_deleted_multiple(some_docs):
    """
    Make sure that num_deleted can properly detect if several records have been
    deleted.
    """
    result = dbc.del_many(TEST_DB, TEST_COLLECT, filters={})
    assert dbc.num_deleted(result) > 1


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_num_deleted_none(a_doc):
    """
    Make sure that num_deleted can properly detect if no records have been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert dbc.num_deleted(result) == 0


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_update_success(a_doc):
    """
    Make sure that updated one can properly detect if a record has been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, DEF_PAIR, DEF_PAIR)
    assert dbc.update_success(result) == True


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_update_no_success(a_doc):
    """
    Make sure that updated one can properly detect if a record has not been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: BAD_VAL}, DEF_PAIR)
    assert dbc.update_success(result) == False


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_num_updated_single(a_doc):
    """
    Make sure that num_updated can properly detect if a single record has been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, DEF_PAIR,
                            {DEF_FLD: 'new val'})
    assert dbc.num_updated(result) == 1


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_num_updated_multiple(some_docs):
    """
    Make sure that num_updated can properly detect if several records have been
    updated.
    """
    result = dbc.update_fld_for_many(TEST_DB, TEST_COLLECT, {}, 'new field', 'new val')
    assert dbc.num_updated(result) > 1


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_num_updated_none(a_doc):
    """
    Make sure that num_updated can properly detect if no records have been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: BAD_VAL}, DEF_PAIR)
    assert dbc.num_updated(result) == 0


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_add_fld_to_all(some_docs):
    """
    Testing updating all records with some new field.
    """
    dbc.add_fld_to_all(TEST_DB, TEST_COLLECT, NEW_FLD, NEW_VAL)
    for i in range(RECS_TO_TEST):
        rec = dbc.read_one(TEST_DB, TEST_COLLECT)
        assert rec[NEW_FLD] == NEW_VAL


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_append_to_list(a_doc):
    """
    Test appending to an interior doc list.
    `a_doc` initiliazes an empty list, so our new val should be
    at `[LIST_FLD][0]`.
    """
    dbc.append_to_list(TEST_DB, TEST_COLLECT, DEF_FLD, DEF_VAL,
                       LIST_FLD, 1)  # any old val will do!
    rec = dbc.read_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert rec[LIST_FLD][0] == 1


@pytest.mark.skip('Cutting over to new multi-db model.')
def test_rename_fld(some_docs):
    """
    Test renaming a field.
    """
    dbc.rename(TEST_DB, TEST_COLLECT, {DEF_FLD: NEW_FLD})
    for i in range(RECS_TO_TEST):
        rec = dbc.read_one(TEST_DB, TEST_COLLECT)
        assert rec[NEW_FLD]


def test_create():
    """
    There should not be more than one of these after insert,
    but let's test just that there is at least one.
    """
    unique_val = rand_fld_val()
    dbc.create(TEST_DB, TEST_COLLECT, {DEF_FLD: unique_val})
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) >= 1
