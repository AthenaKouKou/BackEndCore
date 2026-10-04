from types import SimpleNamespace

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


def test_read_with_limit(sqltobj, table_with_docs):
    LIMIT = 2
    res = sqltobj.read(TEST_DB, table_with_docs.name, limit=LIMIT)
    assert res is not None
    assert len(res) == LIMIT


NEW_CLCT = 'new_collect'
KEY_FLD = 'name'
KEY_VAL = 'a protocol'
TEST_DATE = sql.dt.date(2026, 10, 4)
TEST_DATETIME = sql.dt.datetime(2026, 10, 4, 15, 30)


@pytest.fixture()
def new_clct(sqltobj):
    """
    A collection name with no table behind it; any table a test makes
    for it gets dropped.
    """
    yield NEW_CLCT
    with sqltobj._get_engine().begin() as conn:
        conn.execute(sql.sqla.text(f'drop table if exists {NEW_CLCT}'))
    tbl = sqltobj.get_collect(NEW_CLCT)
    if tbl is not None:
        sqltobj.mdata.remove(tbl)


def test_to_sql_val_date():
    assert sql._to_sql_val(TEST_DATE) == '2026-10-04'


def test_to_sql_val_datetime():
    assert sql._to_sql_val(TEST_DATETIME) == '2026-10-04T15:30:00'


def test_to_sql_val_other():
    assert sql._to_sql_val(BIG_INT) == BIG_INT


def test_change_list_new_top_level():
    assert sql._change_list({}, LIST_FLD, lambda lst: lst + [1]) \
        == (LIST_FLD, [1])


def test_change_list_existing_top_level():
    doc = {LIST_FLD: [1]}
    assert sql._change_list(doc, LIST_FLD, lambda lst: lst + [2]) \
        == (LIST_FLD, [1, 2])
    assert doc == {LIST_FLD: [1]}


def test_change_list_new_nested():
    assert sql._change_list({'create': None}, 'create.a.users',
                            lambda lst: lst + [1]) \
        == ('create', {'a': {'users': [1]}})


def test_change_list_existing_nested():
    doc = {'create': {'auth_key': True, 'users': [1]}}
    assert sql._change_list(doc, 'create.users', lambda lst: lst + [2]) \
        == ('create', {'auth_key': True, 'users': [1, 2]})
    assert doc['create']['users'] == [1]


def test_connectDB_makes_sqlite_dir(tmp_path, monkeypatch):
    db_dir = tmp_path / 'db_dir'
    monkeypatch.setattr(sql, 'db_loc', str(db_dir))
    sql.SqlDB._connectDB(SimpleNamespace(variant=sql.SQLITE))
    assert db_dir.is_dir()


def test_connectDB_mem_makes_no_dir(tmp_path, monkeypatch):
    db_dir = tmp_path / 'db_dir'
    monkeypatch.setattr(sql, 'db_loc', str(db_dir))
    sql.SqlDB._connectDB(SimpleNamespace(variant=sql.SQLITE_MEM))
    assert not db_dir.exists()


def test_create_with_list_and_date(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL,
                                       LIST_FLD: [1, 2],
                                       DEF_FLD: TEST_DATETIME})
    rec = sqltobj.read_one(TEST_DB, new_clct)
    assert rec[LIST_FLD] == [1, 2]
    assert rec[DEF_FLD] == '2026-10-04T15:30:00'


def test_create_adds_new_flds(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL})
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: 'other', NEW_FLD: NEW_VAL})
    rec = sqltobj.read_one(TEST_DB, new_clct, filters={KEY_FLD: 'other'})
    assert rec[NEW_FLD] == NEW_VAL


def test_create_drops_none_only_flds(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL, NEW_FLD: None})
    rec = sqltobj.read_one(TEST_DB, new_clct)
    assert NEW_FLD not in rec


def test_create_keeps_none_for_existing_fld(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL, NEW_FLD: NEW_VAL})
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: 'other', NEW_FLD: None})
    rec = sqltobj.read_one(TEST_DB, new_clct, filters={KEY_FLD: 'other'})
    assert rec[NEW_FLD] is None


def test_create_many_keeps_callers_list(sqltobj, new_clct):
    docs = [{KEY_FLD: KEY_VAL}, {KEY_FLD: 'other', NEW_FLD: NEW_VAL}]
    sqltobj.create(TEST_DB, new_clct, docs)
    assert len(docs) == 2
    assert len(sqltobj.read(TEST_DB, new_clct)) == 2


def test_read_sees_fld_added_after_read(sqltobj, new_clct):
    """
    Adding a column must not leave a stale cached SELECT.
    """
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL})
    sqltobj.read(TEST_DB, new_clct)
    sqltobj.update_fld(TEST_DB, new_clct, {KEY_FLD: KEY_VAL},
                       NEW_FLD, NEW_VAL)
    assert sqltobj.read_one(TEST_DB, new_clct)[NEW_FLD] == NEW_VAL


def test_update_missing_table(sqltobj, new_clct):
    res = sqltobj.update(TEST_DB, new_clct, DEF_PAIR, {NEW_FLD: NEW_VAL})
    assert not res.succeeded()


def test_update_no_filter_updates_all(sqltobj, table_with_docs):
    sqltobj.update(TEST_DB, table_with_docs.name, {}, {'x': 7})
    recs = sqltobj.read(TEST_DB, table_with_docs.name)
    assert all(rec['x'] == 7 for rec in recs)


def test_update_adds_list_fld(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL})
    sqltobj.update_fld(TEST_DB, new_clct, {KEY_FLD: KEY_VAL},
                       LIST_FLD, [1])
    assert sqltobj.read_one(TEST_DB, new_clct)[LIST_FLD] == [1]


def test_delete_missing_table(sqltobj, new_clct):
    res = sqltobj.delete(TEST_DB, new_clct, DEF_PAIR)
    assert res.del_count() == 0


def test_add_fld_none_is_str(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL})
    col = sqltobj.add_fld(TEST_DB, new_clct, NEW_FLD, None)
    assert isinstance(col.type, sql.sqla.Unicode)


def test_add_fld_keyword_name(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL})
    col = sqltobj.add_fld(TEST_DB, new_clct, 'create', {})
    assert isinstance(col.type, sql.sqla.JSON)


def test_append_to_list_no_doc(sqltobj, new_clct):
    res = sqltobj.append_to_list(TEST_DB, new_clct, KEY_FLD, KEY_VAL,
                                 LIST_FLD, 1)
    assert not res.succeeded()
    rec = sqltobj.read_one(TEST_DB, new_clct)
    assert rec[KEY_FLD] == KEY_VAL
    assert rec[LIST_FLD] == [1]


def test_append_to_list_no_list(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL})
    res = sqltobj.append_to_list(TEST_DB, new_clct, KEY_FLD, KEY_VAL,
                                 LIST_FLD, 1)
    assert res.succeeded()
    assert sqltobj.read_one(TEST_DB, new_clct)[LIST_FLD] == [1]


def test_append_to_list_existing_list(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL, LIST_FLD: [1]})
    sqltobj.append_to_list(TEST_DB, new_clct, KEY_FLD, KEY_VAL,
                           LIST_FLD, 2)
    assert sqltobj.read_one(TEST_DB, new_clct)[LIST_FLD] == [1, 2]


def test_append_to_list_nested(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL,
                                       'create': {'auth_key': True}})
    sqltobj.append_to_list(TEST_DB, new_clct, KEY_FLD, KEY_VAL,
                           'create.users', 'a@b.com')
    assert sqltobj.read_one(TEST_DB, new_clct)['create'] \
        == {'auth_key': True, 'users': ['a@b.com']}


def test_delete_from_list_no_doc(sqltobj, new_clct):
    res = sqltobj.delete_from_list(TEST_DB, new_clct, KEY_FLD, KEY_VAL,
                                   LIST_FLD, 1)
    assert not res.succeeded()
    assert sqltobj.read(TEST_DB, new_clct) == []


def test_delete_from_list_removes_all(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL,
                                       LIST_FLD: [1, 2, 1]})
    res = sqltobj.delete_from_list(TEST_DB, new_clct, KEY_FLD, KEY_VAL,
                                   LIST_FLD, 1)
    assert res.succeeded()
    assert sqltobj.read_one(TEST_DB, new_clct)[LIST_FLD] == [2]


def test_delete_from_list_nested(sqltobj, new_clct):
    sqltobj.create(TEST_DB, new_clct, {KEY_FLD: KEY_VAL,
                                       'create': {'users': ['a', 'b']}})
    sqltobj.delete_from_list(TEST_DB, new_clct, KEY_FLD, KEY_VAL,
                             'create.users', 'a')
    assert sqltobj.read_one(TEST_DB, new_clct)['create'] \
        == {'users': ['b']}


def test_create_clct_from_doc_list(sqltobj, new_clct):
    docs = [{KEY_FLD: KEY_VAL}, {KEY_FLD: 'other'}]
    clct = sqltobj._create_clct_from_doc(new_clct, docs)
    assert KEY_FLD in clct.c
    assert len(docs) == 2
