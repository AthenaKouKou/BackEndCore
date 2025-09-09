import sqlalchemy as sqla
from sqlalchemy import desc, asc
from icecream import ic
import time
import os

import backendcore.data.databases.common as cmn

from backendcore.common.constants import OBJ_ID_NM

con = None
SQLITE_DB_NM = 'SQLITE_DB_NM'

SQLITE_MEM = 'sqllite_mem'
SQLITE = 'sqlite'

SQL_DB_NM = 'sql.db'
db_nm = os.environ.get('SQL_DB_NM', SQL_DB_NM)
db_loc = os.environ.get('SQLITE_LOC', './database/')
SQLITE_BASE = 'sqlite+pysqlite:///'
SQLITE_MEM_STR = SQLITE_BASE + ':memory:'
SQLITE_STR = SQLITE_BASE + db_loc + db_nm

DB_TABLE = {
    SQLITE_MEM: SQLITE_MEM_STR,
    SQLITE: SQLITE_STR,
}

engine = None

NO_SORT = 0
DESC = -1
ASC = 1
NO_PROJ = []
DOC_LIMIT = 100000
INNER_DB_ID = '$oid'

# SQL doesn't have the db/collection that Mongo has,
# so functions here will take the db to match
# and then do nothing with it.
DB_NAME = 'db'

DATE_KEY = '$date'

_type_py2sql_dict = {
 int: sqla.sql.sqltypes.BigInteger,
 str: sqla.sql.sqltypes.Unicode,
 float: sqla.sql.sqltypes.Float,
 bytes: sqla.sql.sqltypes.LargeBinary,
 bool: sqla.sql.sqltypes.Boolean,
 dict: sqla.sql.sqltypes.JSON,
 # Gene confirmed trying to use lists
 # should raise an exception. - Boaz 1/21/25
 #  list: sqla.sql.sqltypes.JSON,
 #  list: sqla.types.ARRAY(sqla.String),
 #  "<class 'str'>list": sqla.types.ARRAY(sqla.String),
 #  "<class 'int'>list": sqla.types.ARRAY(sqla.BigInteger),
}

_type_py2sqltext_dict = {
    int: 'BIGINT',
    str: 'VARCHAR',
    float: 'FLOAT',
}


def _type_py2sql(pytype):
    '''Return the closest sqla type for a given python type'''
    if pytype in _type_py2sql_dict:
        return _type_py2sql_dict[pytype]
    else:
        raise NotImplementedError(
            f"You may add custom `sqltype` to \
            `{pytype}` \
            assignment in `_type_py2sql_dict`.")


def _type_py2sqltext(pytype):
    '''Return the closest textual sql type for a given python type'''
    if pytype in _type_py2sqltext_dict:
        return _type_py2sqltext_dict[pytype]
    else:
        raise NotImplementedError(
            f"You may add custom `sqltype` to ` \
            {str(pytype)} \
            ` assignment in `_type_py2sqltext_dict`.")


def create_del_ret(sql_ret):
    return cmn.DeleteReturn(sql_ret.rowcount)


def create_update_ret(sql_ret):
    return cmn.UpdateReturn(sql_ret.rowcount,
                            sql_ret.rowcount)


class SqlDB():
    """
    Encaspulates a connection to a SQL Server.
    """
    def __init__(self, variant=SQLITE_MEM) -> None:
        self.variant = variant
        global engine
        self.mdata = sqla.MetaData()
        if engine is None:
            engine = self._connectDB()
        self.id_counter = os.urandom(3)
        # Load existing metadata
        self.mdata.reflect(engine)

    def _connectDB(self):
        connect_str = DB_TABLE[self.variant]
        return sqla.create_engine(connect_str, echo=False)

    def _get_metadata(self):
        return self.mdata

    def _get_engine(self):
        return engine

    def _clear_mdata(self):
        self.mdata = sqla.MetaData()

    def _clear_table(self, clct_nm):
        collect = self.get_collect(clct_nm)
        with engine.begin() as conn:
            conn.execute(collect.delete())

    def _obj_id(self):
        timestr = int(time.time()).to_bytes(4, 'big')
        randbytes = os.urandom(1)
        ctrstr = self.id_counter
        self.id_counter = int.from_bytes(ctrstr, 'big') + 1
        self.id_counter = self.id_counter.to_bytes(3, 'big')
        id = timestr + randbytes + ctrstr
        id = int.from_bytes(id, 'big')
        return id

    def create_table(self, table_name, columns=None,
                     key_fld=None):
        # Sets up a new table schema and creates it in the DB
        new_table = sqla.Table(
            table_name,
            self.mdata,
            extend_existing=True,
        )
        new_table.append_column(
            sqla.Column(OBJ_ID_NM, sqla.BigInteger, primary_key=True),
            replace_existing=True,
        )
        for column in columns:
            pkey = False
            if column[0] == key_fld:
                pkey = True
            new_table.append_column(
                sqla.Column(column[0], column[1], primary_key=pkey),
                replace_existing=True,
            )
        self.mdata.create_all(engine)
        return new_table

    def get_collect(self, clct_nm: str, doc={}, create_if_none=False):
        clct = self.mdata.tables.get(clct_nm)
        if clct is not None:
            # clct = self._add_extra_flds_from_doc(clct, doc)
            return clct
        if create_if_none:
            if doc is None:
                raise ValueError(f'Table creation failed: {clct_nm}')
            clct = self._create_clct_from_doc(clct_nm, doc)
            return clct
        return None

    def get_field(self, collect, col_nm: str, create_if_none=False):
        """
        Returns a field if it exists, with option to
        create it if it doesn't.
        """
        field = collect.c.get(col_nm)
        if field is not None:
            return field
        if create_if_none:
            field = self.add_fld(DB_NAME, collect.name, col_nm)
            if field is None:
                raise ValueError('Field creation failed.')
            return field
        raise ValueError(f'No such field: {col_nm}')

    def _create_clct_from_doc(self, clct_nm: str, doc: dict):
        """
        Creates a new table where each field is the datatype
        of that field in the supplied document.
        """
        if isinstance(doc, list):
            doc = doc.pop()
        columns = self._doc_to_cols(doc)
        self.create_table(clct_nm, columns)
        return self.get_collect(clct_nm)

    def _doc_to_cols(self, doc: dict):
        columns = []
        for column in doc:
            if column == OBJ_ID_NM or doc[column] is None:
                continue
            pytp = type(doc[column])
            # Detecting lists; only postgresql allows arrays
            if pytp == list:
                raise ValueError("SQL columns can't be arrays.")
            tp = _type_py2sql(pytp)
            columns.append((column, tp))
        return columns

    def _add_extra_flds_from_doc(self, collect, doc: dict):
        for fld in doc:
            self.get_field(collect, fld, create_if_none=True)
        return collect

    def create(self, db_nm: str, clct_nm: str, doc, with_date=False):
        """
        Enter a document or set of documents into a table.
        """
        print('Unused db_nm (create()):', db_nm)
        if with_date:
            raise NotImplementedError(
                'with_date format is not supported at present time')
        doc_with_ids = self.add_ids(doc)
        collect = self.get_collect(clct_nm, doc=doc_with_ids,
                                   create_if_none=True)
        with engine.begin() as conn:
            conn.execute(sqla.insert(collect), doc)
        if isinstance(doc, dict):
            return doc[OBJ_ID_NM]
        return doc[0][OBJ_ID_NM]

    def add_ids(self, doc):
        if isinstance(doc, dict):
            if doc.get(OBJ_ID_NM) is None:
                doc[OBJ_ID_NM] = self._obj_id()
            return doc
        for row in doc:
            if row.get(OBJ_ID_NM) is None:
                row[OBJ_ID_NM] = self._obj_id()
        return doc

    def _read_recs_to_objs(self, res):
        """
        Transforms results from a SELECT
        into an object with fields.
        """
        all_docs = []
        for doc in res.mappings().all():
            all_docs.append(dict(doc))
        return all_docs

    def _text_wrap(self, name):
        return sqla.text(f"\'{name}\'")

    def _asmbl_sort_slct(self, collect, sort=NO_SORT, sort_fld=OBJ_ID_NM):
        stmt = sqla.select(collect)
        if sort_fld is not None:
            field = self.get_field(collect, sort_fld, create_if_none=True)
        if sort == ASC:
            return stmt.order_by(asc(field))
        elif sort == DESC:
            return stmt.order_by(desc(field))
        return stmt

    def _update_dict_to_vals(self, clct, update_dict):
        vals = {}
        for key in update_dict:
            field = self.get_field(clct, key, create_if_none=True)
            vals[field] = update_dict[key]
        return vals

    def _filter_to_where(self, clct, stmt, filter={}, vals=None):
        """
        Converts a basic {field: val} filter to a WHERE clause
        Should add other mongo operators.
        """
        if not len(filter.keys()):
            return stmt
        for fld_nm in list(filter.keys()):
            field = self.get_field(clct, fld_nm, create_if_none=True)
            stmt = stmt.where(field == filter[fld_nm])
        if vals is not None:
            stmt = stmt.values(self._update_dict_to_vals(clct, vals))
        return stmt

    def _id_handler(self, rec, no_id):
        if rec:
            # if no_id:
            if rec.get(OBJ_ID_NM):
                del rec[OBJ_ID_NM]
            # else:
            #     # eliminate the ID nesting if it's not already a string:
            #     if not isinstance(rec[OBJ_ID_NM], str):
            #         rec[OBJ_ID_NM] = rec[OBJ_ID_NM][INNER_DB_ID]
        return rec

    def _asmbl_read_stmt(self, collect, filters, sort, sort_fld):
        stmt = self._asmbl_sort_slct(collect, sort=sort, sort_fld=sort_fld)
        stmt = self._filter_to_where(collect, stmt, filters)
        return stmt

    def read(self, db_nm, clct_nm, filters={},
             sort=NO_SORT, sort_fld=OBJ_ID_NM, no_id=False):
        """
        Returns all docs from a collection.
        `sort` can be DESC, NO_SORT, or ASC.
        """
        print(f'Unused db_nm (read()): {db_nm}')
        all_docs = []
        clct = self.get_collect(clct_nm)
        if clct is None:
            return all_docs
        stmt = self._asmbl_read_stmt(clct, filters, sort, sort_fld)
        with engine.connect() as conn:
            res = conn.execute(stmt)
            all_docs = self._read_recs_to_objs(res)
        if no_id:
            for rec in all_docs:
                self._id_handler(rec, no_id)
        return all_docs

    def read_one(self, db_nm, clct_nm, filters={}, no_id=False):
        res = self.read(db_nm, clct_nm, filters=filters,
                        no_id=no_id)
        if len(res):
            return res.pop()
        return None

    def exclude_flds(self, flds, res):
        for fld_nm in flds:
            for rec in res:
                del rec[fld_nm]
        return res

    def select(self, db_nm, clct_nm, filters={}, sort=NO_SORT,
               sort_fld='_id', proj=NO_PROJ, limit=DOC_LIMIT,
               no_id=False, exclude_flds=None):
        """
        Select records from a collection matching filters.
        """
        if proj != NO_PROJ:
            raise NotImplementedError('select() proj, limit params')
        res = self.read(db_nm, clct_nm, filters=filters,
                        sort=sort, sort_fld=sort_fld)
        if exclude_flds:
            res = self.exclude_flds(exclude_flds, res)
        if len(res) > limit:
            return res[:(limit - 1)]
        return res

    def fetch_by_id(self, db_nm, clct_nm, _id: str, no_id=False):
        return self.read_one(db_nm, clct_nm, {OBJ_ID_NM: _id}, no_id)

    def update(self, db_nm, clct_nm, filters, update_dict):
        collect = self.get_collect(clct_nm)
        if collect is None:
            raise ValueError(f'Cannot update; {clct_nm} does not exist.')
        stmt = sqla.update(collect)
        stmt = self._filter_to_where(collect, stmt,
                                     filters, update_dict)
        with engine.begin() as conn:
            res = conn.execute(stmt)
        return create_update_ret(res)

    def update_fld(self, db_nm, clct_nm, filters, fld_nm, fld_val):
        """
        This should only be used when we just want to update a single
        field.
        To update more than one field in a doc, use `update_doc`.
        """
        return self.update(db_nm, clct_nm, filters=filters,
                           update_dict={fld_nm: fld_val})

    def upsert(self, db_nm, clct_nm, filters, update_dict):
        """
        Updates a record if it exists, otherwise creates it.
        Getting it based on read() feels hacky. SQLA has an
        on_conflict_do_update() but only in the postgres dialect.
        -Boaz 1/9/25
        """
        if not update_dict.get(OBJ_ID_NM):
            readres = self.read_one(db_nm, clct_nm, filters=filters)
        else:
            readres = self.read_one(db_nm, clct_nm, filters={
                OBJ_ID_NM: update_dict[OBJ_ID_NM]
            })
        if not readres:
            return self.create(db_nm, clct_nm, update_dict)
        return self.update(db_nm, clct_nm, filters, update_dict)

    def delete(self, db_nm, clct_nm, filters={}):
        """
        Deletes documents matching the filters.
        """
        print('Unused db_nm (delete()):', db_nm)
        collect = self.get_collect(clct_nm)
        if collect is None:
            raise ValueError(f'Cannot delete; {clct_nm} does not exist.')
        stmt = sqla.delete(collect)
        stmt = self._filter_to_where(collect, stmt, filters)
        with engine.begin() as conn:
            res = conn.execute(stmt)
        return create_del_ret(res)

    def delete_by_id(self, db, clct_nm, id):
        """
        Delete one record identified by id.
        We convert the passed in string to an ID for our user.
        """
        return self.delete(db, clct_nm, filters={OBJ_ID_NM: id})

    def delete_many(self, db_nm, clct_nm, filters={}):
        """
        Delete many records that meet filters.
        """
        return self.delete(db_nm, clct_nm, filters=filters)

    def add_fld(self, db_nm, clct_nm, fld_nm, fld_data=''):
        """
        SQL Alchemy struggles with modifying table structure
        (as SQL does generally) so I'm using a text alter command.
        SQLA also offers Alembic for industrial-strength migration
        but for now this is ok. -Boaz 1/10/25
        """
        print(f'Unused db_nm (add_fld()): {db_nm}')
        tp = type(fld_data)
        with engine.begin() as conn:
            conn.execute(
                sqla.text(f'alter table {clct_nm} add column ' +
                          f'{fld_nm} {_type_py2sqltext(tp)}')
            )
        collect = self.get_collect(clct_nm)
        column = sqla.Column(fld_nm, _type_py2sql(tp))
        collect.append_column(column, replace_existing=True)
        self.mdata.create_all(engine)
        return column

    def add_fld_to_all(self, db_nm, clct_nm, new_fld, value):
        self.add_fld(db_nm, clct_nm, new_fld, value)
        new_dict = {new_fld: value}
        return self.update(db_nm, clct_nm, update_dict=new_dict)

    def append_to_list(self, db_nm, clct_nm, filter_fld_nm, filter_fld_val,
                       list_nm, new_list_item):
        filter = {filter_fld_nm: filter_fld_val}
        doc = self.read_one(db_nm, clct_nm, filter)
        arr = doc[list_nm]
        arr.push(new_list_item)
        return self.update_fld(db_nm, clct_nm, filter,
                               fld_nm=list_nm, fld_val=arr)

    def rename(self, db_nm: str, clct_nm: str, nm_map: dict):
        """
        Renames specified fields on all documents in a collection.

        Parameters
        ----------
        db_nm: str
            The database name.
        clct_nm: str
            The name of the database collection.
        nm_map: dict
            A dictionary. The keys are the current field names. Each key maps
            to the desired field name:
            {
                "old_nm1": "new_nm1",
                "old_nm2": "new_nm2",
            }
        """
        for key in nm_map:
            with engine.begin() as conn:
                conn.execute(
                    sqla.text(f'alter table {clct_nm} change \
                                {key} {nm_map[key]}')
                )

    def time_str_from_rec(self, date_rec: dict):
        # Not quite sure how this translation works,
        # but tests pass!
        return date_rec


def main():
    sqlDB = SqlDB()

    table_cols = [
            ('x', sqla.BigInteger),
            ('y', sqla.BigInteger),
        ]
    db = 'some_db'
    collect = 'some_collection'
    new_table = sqlDB.create_table(collect, table_cols)
    ic(new_table)

    doc = [
        {"x": 1, "y": 1},
        {"x": 2, "y": 4},
        ]
    ic(sqlDB.create(db, collect, doc))
    ic(sqlDB.read(db, collect, sort=DESC))
    ic(sqlDB.read_one(db, collect))
    return 0


if __name__ == '__main__':
    main()
