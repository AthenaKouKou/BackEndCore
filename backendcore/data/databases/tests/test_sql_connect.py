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
    res = sqltobj.create(TEST_DB, TEST_COLLECT, {})
    assert res is not None


def test_read(sqltobj):
    res = sqltobj.read(TEST_DB, TEST_COLLECT)
    assert res is not None
    assert len(res) > 0


def test_get_collect(sqltobj):
    res = sqltobj.get_collect(TEST_COLLECT)
    assert res is not None
