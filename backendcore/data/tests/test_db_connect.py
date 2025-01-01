"""
This module tests our code for database connectivity.
For the moment, the tests will assume MongoDB.
"""
import random
from copy import deepcopy

from unittest.mock import patch
import pytest
import os

import backendcore.data.db_connect as dbc

TEST_DB = 'test_db'
TEST_COLLECT = 'test_collect'

DEF_FLD = 'fld0'
DEF_VAL = 'def_val'

DEF_PAIR = {DEF_FLD: DEF_VAL}

RET_CONST = 17

LIST_FLD = 'a_list'

NEW_FLD = 'fld1'
NEW_VAL = 'flooby!'

BAD_VAL = "Scooby-dooby-doo!"

BIG_INT = 10**32

DBS_LOC = 'backendcore.data.databases'
MONGO_DB_LOC = f'{DBS_LOC}.mongo_connect'
MONGO_DB_OBJ = f'{MONGO_DB_LOC}.MongoDB'
SQL_DB_LOC = f'{DBS_LOC}.sql_connect'
SQL_DB_OBJ = f'{SQL_DB_LOC}.SqlDB'

DB_OBJ = MONGO_DB_OBJ
db_type = os.environ.get('DATABASE', dbc.MONGO)
if db_type == dbc.SQL:
    DB_OBJ = SQL_DB_OBJ


def rand_fld_val():
    """
    We should only get a duplicate every billion or so tests.
    """
    return str(random.randint(0, BIG_INT))


@patch(f'{DB_OBJ}.read_one', autospec=True, return_value={})
def test_read_one_no_filter(mock_read_one):
    """
    Tests that a fetch with no filter retrieves the rec we inserted
    in the fixture.
    """
    rec = dbc.read_one(TEST_DB, TEST_COLLECT, filters={})
    assert rec is not None


@patch(f'{DB_OBJ}.read_one', autospec=True, return_value=None)
def test_read_one_bad_filter(mock_read_one):
    """
    Tests that a fetch with a bad filter fails.
    """
    rec = dbc.read_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert rec is None


@patch(f'{DB_OBJ}.read_one', autospec=True, return_value={})
def test_read_one_good_filter(mock_read_one):
    """
    Tests that a fetch with a good filter works.
    """
    rec = dbc.read_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert rec is not None


@patch(f'{DB_OBJ}.fetch_by_id', autospec=True, return_value={})
def test_fetch_by_id(mock_fetch_by_id):
    ret = dbc.fetch_by_id(TEST_DB, TEST_COLLECT, {'any': 'vals'})
    assert ret is not None


@patch(f'{DB_OBJ}.delete_by_id', autospec=True,
       return_value='Not none')
def test_delete_by_id(mock_delete_by_id):
    assert dbc.delete_by_id(TEST_DB, TEST_COLLECT, 'some id') is not None


@patch(f'{DB_OBJ}.update_fld', autospec=True, return_value=RET_CONST)
def test_update_fld(a_doc):
    assert dbc.update_fld(TEST_DB, TEST_COLLECT,
                          DEF_PAIR, DEF_FLD,
                          'Any value') == RET_CONST


@patch(f'{DB_OBJ}.update', autospec=True, return_value=RET_CONST)
def test_update(mock_update):
    """
    Just testing we get back the return of the installed db.
    """
    ret = dbc.update(TEST_DB, TEST_COLLECT, {}, {})
    assert ret == RET_CONST


@patch(f'{DB_OBJ}.upsert', autospec=True, return_value=RET_CONST)
def test_upsert(mock_upsert):
    """
    Just testing we get back the return of the installed db.
    """
    ret = dbc.upsert(TEST_DB, TEST_COLLECT, {}, {})
    assert ret == RET_CONST


@pytest.mark.skip('Update success must be re-written before testing.')
def test_update_success(a_doc):
    """
    Make sure that updated one can properly detect if a record has been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, DEF_PAIR, DEF_PAIR)
    assert dbc.update_success(result) == True


@pytest.mark.skip('Update success must be re-written before testing.')
def test_update_no_success(a_doc):
    """
    Make sure that updated one can properly detect if a record has not been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: BAD_VAL}, DEF_PAIR)
    assert dbc.update_success(result) == False


@pytest.mark.skip('Update success must be re-written before testing.')
def test_num_updated_single(a_doc):
    """
    Make sure that num_updated can properly detect if a single record has been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, DEF_PAIR,
                            {DEF_FLD: 'new val'})
    assert dbc.num_updated(result) == 1


@pytest.mark.skip('num updated must be re-written before testing.')
def test_num_updated_multiple(some_docs):
    """
    Make sure that num_updated can properly detect if several records have been
    updated.
    """
    result = dbc.update_fld_for_many(TEST_DB, TEST_COLLECT, {}, 'new field', 'new val')
    assert dbc.num_updated(result) > 1


@pytest.mark.skip('num updated must be re-written before testing.')
def test_num_updated_none(a_doc):
    """
    Make sure that num_updated can properly detect if no records have been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: BAD_VAL}, DEF_PAIR)
    assert dbc.num_updated(result) == 0


@patch(f'{DB_OBJ}.select', autospec=True, return_value={})
def test_select(mock_select):
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={})
    assert isinstance(recs, dict)


@patch(f'{DB_OBJ}.delete', autospec=True,
       return_value='Not none')
def test_delete(mock_delete):
    assert dbc.delete(TEST_DB, TEST_COLLECT) is not None


@patch(f'{DB_OBJ}.delete_many', autospec=True,
       return_value='Not none')
def test_delete_many(mock_delete_many):
    """
    Make sure deleting many docs leaves none behind.
    """
    assert dbc.delete_many(TEST_DB, TEST_COLLECT) is not None


@pytest.mark.skip('Delete result tests will await rewrite of their functions.')
def test_delete_success(a_doc):
    """
    Make sure that deleted one can properly detect if a record has been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert dbc.delete_success(result) == True


@pytest.mark.skip('Delete result tests will await rewrite of their functions.')
def test_delete_no_success(a_doc):
    """
    Make sure that deleted one can properly detect if a record has not been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert dbc.delete_success(result) == False


@pytest.mark.skip('Delete result tests will await rewrite of their functions.')
def test_num_deleted_single(a_doc):
    """
    Make sure that num_deleted can properly detect if a single record has been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert dbc.num_deleted(result) == 1


@pytest.mark.skip('Delete result tests will await rewrite of their functions.')
def test_num_deleted_multiple(some_docs):
    """
    Make sure that num_deleted can properly detect if several records have been
    deleted.
    """
    result = dbc.del_many(TEST_DB, TEST_COLLECT, filters={})
    assert dbc.num_deleted(result) > 1


@pytest.mark.skip('Delete result tests will await rewrite of their functions.')
def test_num_deleted_none(a_doc):
    """
    Make sure that num_deleted can properly detect if no records have been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert dbc.num_deleted(result) == 0


@patch(f'{DB_OBJ}.add_fld_to_all', autospec=True, return_value=RET_CONST)
def test_add_fld_to_all(mock_add_fld_to_all):
    """
    Testing updating all records with some new field.
    """
    ret = dbc.add_fld_to_all(TEST_DB, TEST_COLLECT, NEW_FLD, NEW_VAL)
    assert ret == RET_CONST


@patch(f'{DB_OBJ}.append_to_list', autospec=True, return_value=RET_CONST)
def test_append_to_list(mock_append_to_list):
    """
    Test appending to an interior doc list.
    """
    assert dbc.append_to_list(TEST_DB, TEST_COLLECT, 'any fld', 'any val',
                              'any list', 'any list val') == RET_CONST


@patch(f'{DB_OBJ}.rename', autospec=True, return_value=RET_CONST)
def test_rename(some_docs):
    """
    Test renaming a field.
    """
    assert dbc.rename(TEST_DB, TEST_COLLECT, {DEF_FLD: NEW_FLD}) == RET_CONST


def test_create():
    """
    There should not be more than one of these after create,
    but let's test just that there is at least one.
    """
    unique_val = rand_fld_val()
    dbc.create(TEST_DB, TEST_COLLECT, {DEF_FLD: unique_val})
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) >= 1
