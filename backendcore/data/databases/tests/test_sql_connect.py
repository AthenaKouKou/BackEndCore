import pytest
import pymongo

import backendcore.data.databases.sql_connect as sql

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

TABLE_COLS = [
            ('x', sql.Integer),
            ('y', sql.Integer),
        ]
TEST_DOCS = [
        {"_id": 0, "x": 1, "y": 1},
        {"_id": 1, "x": 2, "y": 4},
        ]


@pytest.fixture(scope='module')
def sqltobj():
    return sql.SqlDB()


def test_main():
    assert sql.main() == 0


def test_connectDB(sqltobj):
    """
    We should be able to connect to our DB!
    """
    connection = sqltobj._connectDB()
    assert connection is not None


def test_create_table(sqltobj):
    new_table = sqltobj.create_table(TEST_COLLECT, TABLE_COLS)
    assert new_table is not None


def test_create(sqltobj):
    res = sqltobj.create(TEST_DB, TEST_COLLECT, TEST_DOCS)
    assert res is not None


def test_read(sqltobj):
    res = sqltobj.read(TEST_DB, TEST_COLLECT)
    assert res is not None
    assert len(res) > 0


def test_read_sorted_ascending(sqltobj):
    res = sqltobj.read(TEST_DB, TEST_COLLECT, sort=sql.ASC)
    assert res is not None
    assert res[0][sql.OBJ_ID_NM] <= res[1][sql.OBJ_ID_NM]


def test_read_sorted_descending(sqltobj):
    res = sqltobj.read(TEST_DB, TEST_COLLECT, sort=sql.DESC)
    assert res is not None
    assert res[0][sql.OBJ_ID_NM] >= res[1][sql.OBJ_ID_NM]


def test_read_one(sqltobj):
    res = sqltobj.read_one(TEST_DB, TEST_COLLECT)
    assert res is not None
    assert isinstance(res, dict)


def test_get_collect(sqltobj):
    res = sqltobj.get_collect(TEST_COLLECT)
    assert res is not None
