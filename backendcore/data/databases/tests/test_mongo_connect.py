"""
This module tests our code for managing API categories.
"""
import random
from copy import deepcopy

import pytest
import pymongo

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


def rand_fld_val():
    """
    Return this as a str due to Mongo int limits.
    We should only get a duplicate every billion or so tests.
    """
    return str(random.randint(0, BIG_INT))


@pytest.fixture(scope='function')
def some_docs():
    """
    General mongo test fixture.
    Creates a bunch o' docs, then deletes them after test runs.
    """
    db = mdb.MongoDB()
    for i in range(RECS_TO_TEST):
        db.create(TEST_DB, TEST_COLLECT, {DEF_FLD: f'val{i}'})
    yield
    for i in range(RECS_TO_TEST):
        db.delete(TEST_DB, TEST_COLLECT, filters={DEF_FLD: f'val{i}'})


@pytest.fixture(scope='function')
def a_doc():
    """
    General mongo test fixture.
    Creates one doc, then deletes it after test runs.
    """
    db = mdb.MongoDB()
    ret = db.create(TEST_DB, TEST_COLLECT, {DEF_FLD: DEF_VAL, LIST_FLD: []})
    yield ret
    db.delete(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)


@pytest.fixture(scope='function')
def new_doc():
    """
    General mongo test fixture.
    Creates one doc, but does NOT delete it after test runs:
        needed for testing delete functions!
    """
    db = mdb.MongoDB()
    return db.create(TEST_DB, TEST_COLLECT,
                     {DEF_FLD: DEF_VAL, LIST_FLD: []})


GOOD_ID = '1' * mdb.DB_ID_LEN
BAD_ID = '1' * (mdb.DB_ID_LEN - 1)


def test_is_valid_id():
    assert mdb.is_valid_id(GOOD_ID)


def test_is_not_valid_id():
    assert not mdb.is_valid_id(BAD_ID)


DATE_SAMPLE = '2023-06-06T13:50:23.091Z'
DATE_REC_SAMPLE = {'issue_time': {mdb.DATE_KEY: DATE_SAMPLE}}


REC_W_ID = {
    mdb.DB_ID: {
        mdb.INNER_DB_ID: '6466b27e3bddcc6a7adc6637'
    },
    'other_field': 1,
}


@pytest.fixture(scope='function')
def rec_w_id():
    return deepcopy(REC_W_ID)


def test_id_handler_without_id(rec_w_id):
    new_rec = mdb._id_handler(rec_w_id, True)
    assert mdb.DB_ID not in new_rec
    assert 'other_field' in new_rec


def test_id_handler_with_id(rec_w_id):
    new_rec = mdb._id_handler(rec_w_id, False)
    assert mdb.DB_ID in new_rec
    assert 'other_field' in new_rec
    assert isinstance(new_rec[mdb.DB_ID], str)


def test_init_mongo():
    assert isinstance(mdb.MongoDB(), mdb.MongoDB)


@pytest.fixture(scope='function')
def mobj():
    return mdb.MongoDB()


def test_connectDB(mobj):
    """
    We should be able to connect to our DB!
    """
    connection = mobj._connectDB()
    assert connection is not None


def test_fetch_by_id(mobj, a_doc):
    ret = mobj.fetch_by_id(TEST_DB, TEST_COLLECT, a_doc)
    assert ret is not None


def test_del_by_id(mobj, new_doc):
    rec1 = mobj.read_one(TEST_DB, TEST_COLLECT)
    rec_id = rec1[str(mdb.DB_ID)]
    mobj.del_by_id(TEST_DB, TEST_COLLECT, rec_id)
    assert mobj.fetch_by_id(TEST_DB, TEST_COLLECT, rec_id) is None


def test_update_fld(mobj, a_doc):
    unique_val = rand_fld_val()
    mobj.update_fld(TEST_DB, TEST_COLLECT, DEF_PAIR,
                    DEF_FLD, unique_val)
    recs = mobj.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) == 1


def test_update(mobj, a_doc):
    unique_val = rand_fld_val()
    mobj.update(TEST_DB, TEST_COLLECT, DEF_PAIR,
                {DEF_FLD: unique_val, LIST_FLD: ['something']})
    recs = mobj.select(TEST_DB, TEST_COLLECT,
                       filters={DEF_FLD: unique_val, LIST_FLD: ['something']})
    assert len(recs) == 1


def test_select_cursor_no_filter(mobj, some_docs):
    """
    This should return all records in a collection.
    We test with >= since someone may have left other docs
    in our test_db.
    """
    cursor = mobj.select_cursor(TEST_DB, TEST_COLLECT, filters={})
    assert isinstance(cursor, pymongo.cursor.Cursor)


def test_select_no_filter(mobj, some_docs):
    """
    This should return all records in a collection.
    We test with >= since someone may have left other docs
    in our test_db.
    """
    recs = mobj.select(TEST_DB, TEST_COLLECT, filters={})
    assert len(recs) >= RECS_TO_TEST


def test_select_w_filter(mobj, some_docs):
    """
    This should return all records in a collection matching the
    filter.
    This record should be unique except for a 1 in BIG_INT
    chance. Enough for our lifetimes.
    """
    unique_val = rand_fld_val()
    mobj.create(TEST_DB, TEST_COLLECT, {DEF_FLD: unique_val})
    recs = mobj.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    mobj.delete(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) == 1


def test_read_one_no_filter(mobj, a_doc):
    """
    Tests that a fetch with no filter retieves the rec we inserted
    in the fixture.
    """
    rec = mobj.read_one(TEST_DB, TEST_COLLECT, filters={})
    assert rec is not None


def test_read_one_bad_filter(mobj, a_doc):
    """
    Tests that a fetch with a bad filter fails.
    """
    rec = mobj.read_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert rec is None


def test_read_one_good_filter(mobj, a_doc):
    """
    Tests that a fetch with a good filter works.
    """
    assert mobj.read_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)


def test_delete_that_exists(mobj, a_doc):
    """
    Make sure deleting a doc that exists deletes 1 record.
    """
    result = mobj.delete(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert result.deleted_count == 1


def test_delete_that_doesnt_exist(mobj, a_doc):
    """
    Make sure deleting a doc that doesn't exist deletes 0 records.
    """
    result = mobj.delete(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert result.deleted_count == 0


def test_delete_many(mobj, a_doc):
    """
    Make sure deleting many docs leaves none behind.
    """
    mobj.delete_many(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert mobj.read_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR) is None


def test_delete_success(mobj, a_doc):
    """
    Make sure that delete can properly detect if a record has been
    deleted.
    """
    result = mobj.delete(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert mobj.delete_success(result) == True


def test_delete_no_success(mobj, a_doc):
    """
    Make sure that deleted one can properly detect if a record has not been
    deleted.
    """
    result = mobj.delete(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert mobj.delete_success(result) == False


def test_num_deleted_single(mobj, a_doc):
    """
    Make sure that num_deleted can properly detect if a single record has been
    deleted.
    """
    result = mobj.delete(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert mobj.num_deleted(result) == 1


def test_num_deleted_multiple(mobj, some_docs):
    """
    Make sure that num_deleted can properly detect if several records have been
    deleted.
    """
    result = mobj.delete_many(TEST_DB, TEST_COLLECT, filters={})
    assert mobj.num_deleted(result) > 1


def test_num_deleted_none(mobj, a_doc):
    """
    Make sure that num_deleted can properly detect if no records have been
    deleted.
    """
    result = mobj.delete(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert mobj.num_deleted(result) == 0


def test_update_success(mobj, a_doc):
    """
    Make sure that updated one can properly detect if a record has been
    updated.
    """
    result = mobj.update(TEST_DB, TEST_COLLECT, DEF_PAIR, DEF_PAIR)
    assert mobj.update_success(result) == True


def test_update_no_success(mobj, a_doc):
    """
    Make sure that updated one can properly detect if a record has not been
    updated.
    """
    result = mobj.update(TEST_DB, TEST_COLLECT, {DEF_FLD: BAD_VAL}, DEF_PAIR)
    assert mobj.update_success(result) == False


def test_num_updated_single(mobj, a_doc):
    """
    Make sure that num_updated can properly detect if a single record has been
    updated.
    """
    result = mobj.update(TEST_DB, TEST_COLLECT, DEF_PAIR, {DEF_FLD: 'new val'})
    assert mobj.num_updated(result) == 1


def test_num_updated_multiple(mobj, some_docs):
    """
    Make sure that num_updated can properly detect if several records have been
    updated.
    """
    result = mobj.update_fld_for_many(TEST_DB, TEST_COLLECT, {}, 'new field', 'new val')
    assert mobj.num_updated(result) > 1


def test_num_updated_none(mobj, a_doc):
    """
    Make sure that num_updated can properly detect if no records have been
    updated.
    """
    result = mobj.update(TEST_DB, TEST_COLLECT, {DEF_FLD: BAD_VAL}, DEF_PAIR)
    assert mobj.num_updated(result) == 0


def test_add_fld_to_all(mobj, some_docs):
    """
    Testing updating all records with some new field.
    """
    mobj.add_fld_to_all(TEST_DB, TEST_COLLECT, NEW_FLD, NEW_VAL)
    for i in range(RECS_TO_TEST):
        rec = mobj.read_one(TEST_DB, TEST_COLLECT)
        assert rec[NEW_FLD] == NEW_VAL


def test_append_to_list(mobj, a_doc):
    """
    Test appending to an interior doc list.
    `a_doc` initiliazes an empty list, so our new val should be
    at `[LIST_FLD][0]`.
    """
    mobj.append_to_list(TEST_DB, TEST_COLLECT, DEF_FLD, DEF_VAL,
                       LIST_FLD, 1)  # any old val will do!
    rec = mobj.read_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert rec[LIST_FLD][0] == 1


def test_rename_fld(mobj, some_docs):
    """
    Test renaming a field.
    """
    mobj.rename(TEST_DB, TEST_COLLECT, {DEF_FLD: NEW_FLD})
    for i in range(RECS_TO_TEST):
        rec = mobj.read_one(TEST_DB, TEST_COLLECT)
        assert rec[NEW_FLD]


def test_create(mobj):
    """
    There should not be more than one of these after insert,
    but let's test just that there is at least one.
    """
    unique_val = rand_fld_val()
    mobj.create(TEST_DB, TEST_COLLECT, {DEF_FLD: unique_val})
    recs = mobj.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) >= 1
    mobj.delete(TEST_DB, TEST_COLLECT, {DEF_FLD: unique_val})
