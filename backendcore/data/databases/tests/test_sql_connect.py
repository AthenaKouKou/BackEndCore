import pytest
from icecream import ic

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
            ('x', sql.sqla.BigInteger),
            ('y', sql.sqla.BigInteger),
        ]
TEST_DOCS = [
        {"_id": 0, "x": 1, "y": 1},
        {"_id": 1, "x": 2, "y": 4},
        {"_id": 2, "x": 3, "y": 9},
        ]

SQL_DB_OBJ = None


def create_db():
    global SQL_DB_OBJ
    if not SQL_DB_OBJ:
        SQL_DB_OBJ = sql.SqlDB()
    return SQL_DB_OBJ


@pytest.fixture(scope='module')
def sqltobj():
    return create_db()


@pytest.fixture()
def empty_table():
    sqltdb = create_db()
    res = sqltdb.create_table(TEST_COLLECT, TABLE_COLS)
    yield res
    sqltdb._clear_table(TEST_COLLECT)
    res.drop(sqltdb._get_engine(), checkfirst=False)
    sqltdb._clear_mdata()


@pytest.fixture()
def table_with_docs():
    sqltdb = create_db()
    res = sqltdb.create_table(TEST_COLLECT, TABLE_COLS)
    sqltdb.create(TEST_DB, res.name, TEST_DOCS)
    yield res
    sqltdb._clear_table(TEST_COLLECT)
    res.drop(sqltdb._get_engine(), checkfirst=False)
    sqltdb._clear_mdata()


def test_main():
    assert sql.main() == 0


def test_connectDB(sqltobj):
    """
    We should be able to connect to our DB!
    """
    connection = sqltobj._connectDB()
    assert connection is not None


def test_create(sqltobj, empty_table):
    res = sqltobj.create(TEST_DB, empty_table.name, TEST_DOCS)
    assert res is not None


def test_create_table(sqltobj):
    new_table = sqltobj.create_table(TEST_COLLECT, TABLE_COLS)
    assert new_table is not None


def test_read(sqltobj, table_with_docs):
    res = sqltobj.read(TEST_DB, table_with_docs.name)
    assert res is not None
    assert len(res) > 0


def test_read_sorted_ascending(sqltobj, table_with_docs):
    res = sqltobj.read(TEST_DB, table_with_docs.name, sort=sql.ASC)
    assert res is not None
    assert res[0][sql.OBJ_ID_NM] <= res[1][sql.OBJ_ID_NM]


def test_read_sorted_descending(sqltobj, table_with_docs):
    res = sqltobj.read(TEST_DB, table_with_docs.name, sort=sql.DESC)
    ic(res)
    assert res is not None
    assert res[0][sql.OBJ_ID_NM] >= res[1][sql.OBJ_ID_NM]


def test_read_one(sqltobj, table_with_docs):
    res = sqltobj.read_one(TEST_DB, table_with_docs.name)
    assert res is not None
    assert isinstance(res, dict)


def test_get_collect(sqltobj, empty_table):
    res = sqltobj.get_collect(empty_table.name)
    assert res is not None


def test_update_one_doc(sqltobj, table_with_docs):
    id = 1
    up_dict = {'x': 10, 'y': 100}
    filter = {sql.OBJ_ID_NM: id}
    sqltobj.update(TEST_DB, table_with_docs.name,
                   filters=filter,
                   update_dict=up_dict)
    res = sqltobj.read_one(TEST_DB, table_with_docs.name,
                           filters=filter)
    assert res['x'] == 10
    assert res['y'] == 100


def test_delete_one(sqltobj, table_with_docs):
    beforedel = len(sqltobj.read(TEST_DB, table_with_docs.name))
    res = sqltobj.delete(TEST_DB, table_with_docs.name,
                         {sql.OBJ_ID_NM: 0})
    afterdel = len(sqltobj.read(TEST_DB, table_with_docs.name))
    assert res.succeeded()
    assert res.del_count() == 1
    assert afterdel < beforedel


def test_delete_many(sqltobj, table_with_docs):
    res = sqltobj.delete_many(TEST_DB, table_with_docs.name)
    afterdel = len(sqltobj.read(TEST_DB, table_with_docs.name))
    assert res.succeeded()
    assert res.del_count() > 0
    assert afterdel == 0


def test_delete_by_id(sqltobj, table_with_docs):
    id = 1
    res = sqltobj.delete_by_id(TEST_DB, table_with_docs.name, id)
    afterdel = sqltobj.read(TEST_DB, table_with_docs.name,
                            filters={sql.OBJ_ID_NM: id})
    assert res.succeeded()
    assert res.del_count() == 1
    assert len(afterdel) == 0
