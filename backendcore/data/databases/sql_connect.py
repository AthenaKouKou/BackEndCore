import sqlalchemy as sqla
from sqlalchemy import Integer
from icecream import ic

from backendcore.common.constants import OBJ_ID_NM

con = None
SQLITE_DB_NM = 'SQLITE_DB_NM'

SQLITE_MEM = 'sqllite_mem'
SQLITE_MEM_STR = 'sqlite+pysqlite:///:memory:'

DB_TABLE = {
    SQLITE_MEM: SQLITE_MEM_STR,
}

engine = None

NO_SORT = 0
DESC = -1
ASC = 1
NO_PROJ = []
DOC_LIMIT = 100000
INNER_DB_ID = '$oid'


_type_py2sql_dict = {
 int: sqla.sql.sqltypes.BigInteger,
 str: sqla.sql.sqltypes.Unicode,
 float: sqla.sql.sqltypes.Float,
 bytes: sqla.sql.sqltypes.LargeBinary,
 bool: sqla.sql.sqltypes.Boolean,
 list: sqla.sql.sqltypes.ARRAY,
 dict: sqla.sql.sqltypes.JSON
}


def _type_py2sql(pytype):
    '''Return the closest sqla type for a given python type'''
    if pytype in _type_py2sql_dict:
        return _type_py2sql_dict[pytype]
    else:
        raise NotImplementedError(
            f"You may add custom `sqltype` to ` \
            {str(pytype)} \
            ` assignment in `_type_py2sql_dict`.")


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

    def _connectDB(self):
        connect_str = DB_TABLE[self.variant]
        return sqla.create_engine(connect_str, echo=True)

    def _get_metadata(self):
        return self.mdata

    def _get_engine(self):
        global engine
        return engine

    def _clear_mdata(self):
        self.mdata = sqla.MetaData()

    def _clear_table(self, clct_nm):
        collect = self.get_collect(clct_nm)
        with engine.begin() as conn:
            conn.execute(collect.delete())

    def create_table(self, table_name, columns=None):
        # Sets up a new table schema and creates it in the DB
        new_table = sqla.Table(
            table_name,
            self.mdata,
            sqla.Column(OBJ_ID_NM, sqla.Integer, primary_key=True),
            extend_existing=True,
        )
        for column in columns:
            new_table.append_column(
                sqla.Column(column[0], column[1]),
                replace_existing=True,
            )
        self.mdata.create_all(engine)
        return new_table

    # def get_collect(self, db_nm: str, clct_nm: str):
    def get_collect(self, clct_nm: str, doc={}):
        clct = self.mdata.tables.get(clct_nm)
        # If collection doesn't exist, create it based on doc
        if clct is None:
            if doc is None:
                raise ValueError(f'No such table: {clct_nm}')
            clct = self._create_clct_from_doc(clct_nm, doc)
            ic('Created table:', clct)
        return clct

    def get_field(self, collect, col_nm: str):
        """
        Need to create column if it doesn't exist
        But that requires a migration.
        """
        field = collect.c.get(col_nm)
        if field is None:
            raise ValueError(f'No such field: {col_nm}')
        return field

    def _create_clct_from_doc(self, clct_nm: str, doc: dict):
        """
        Creates a new table where each field is the datatype
        of that field in the supplied document.
        """
        if isinstance(doc, list):
            doc = doc.pop()
        columns = []
        for column in doc:
            if column == OBJ_ID_NM:
                continue
            tp = _type_py2sql(type(doc[column]))
            columns.append((column, tp))
        self.create_table(clct_nm, columns)
        return self.get_collect(clct_nm)

    def create(self, db_nm: str, clct_nm: str, doc, with_date=False):
        """
        Enter a document or set of documents into a table.
        """
        print('Unused db_nm (create()):', db_nm)
        ic(doc)
        if with_date:
            raise NotImplementedError(
                'with_date format is not supported at present time')
        collect = self.get_collect(clct_nm, doc=doc)
        with engine.begin() as conn:
            res = conn.execute(sqla.insert(collect), doc)
            return res

    def _read_recs_to_objs(self, res):
        """
        Transforms results from a SELECT
        into objects with fields.
        """
        all_docs = []
        fields = []
        for field in res._metadata.keys:
            fields.append(field)
        for rec in res:
            doc = {}
            for i in range(len(fields)):
                doc[fields[i]] = rec[i]
            all_docs.append(doc)
        return all_docs

    def _text_wrap(self, name):
        return sqla.text(f"\'{name}\'")

    def _asmbl_sort_slct(self, collect, sort=ASC, sort_fld=OBJ_ID_NM):
        stmt = sqla.select(collect)
        if sort == ASC:
            return stmt.order_by(self.get_field(collect, sort_fld).asc())
        if sort == DESC:
            return stmt.order_by(self.get_field(collect, sort_fld).desc())
        return stmt

    def _update_dict_to_vals(self, clct, update_dict):
        vals = {}
        for key in update_dict:
            vals[self.get_field(clct, key)] = update_dict[key]
        return vals

    def _filter_to_where(self, clct, stmt, filter={}, vals=None):
        """
        Converts a basic {field: val} filter to a WHERE clause
        Should add other mongo operators.
        """
        if not len(filter.keys()):
            return stmt
        for field in list(filter.keys()):
            stmt = stmt.where(self.get_field(clct, field) ==
                              filter[field])
        if vals is not None:
            stmt = stmt.values(self._update_dict_to_vals(clct, vals))
        return stmt

    def _id_handler(rec, no_id):
        if rec:
            if no_id:
                del rec[OBJ_ID_NM]
            # else:
            #     # eliminate the ID nesting if it's not already a string:
            #     if not isinstance(rec[OBJ_ID_NM], str):
            #         rec[OBJ_ID_NM] = rec[OBJ_ID_NM][INNER_DB_ID]
        return rec

    def _asmbl_read_stmt(self, clct_nm, filters, sort, sort_fld):
        collect = self.get_collect(clct_nm)
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
        stmt = self._asmbl_read_stmt(clct_nm, filters, sort, sort_fld)
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
        """
        tbi
        """
        return self.read_one(db_nm, clct_nm, {OBJ_ID_NM: _id}, no_id)

    def update(self, db_nm, clct_nm, filters, update_dict):
        """
        tbi
        """
        collect = self.get_collect(clct_nm)
        stmt = sqla.update(collect)
        stmt = self._filter_to_where(collect, stmt,
                                     filters, update_dict)
        with engine.begin() as conn:
            res = conn.execute(stmt)
            return res

    def update_fld(self, db_nm, clct_nm, filters, fld_nm, fld_val):
        """
        This should only be used when we just want to update a single
        field.
        To update more than one field in a doc, use `update_doc`.
        """
        return self.update(db_nm, clct_nm, filters=filters,
                           update_dict={fld_nm: fld_val})

    def upsert(self):
        raise NotImplementedError('upsert')

    def delete(self, db_nm, clct_nm, filters={}):
        """
        Deletes documents matching the filters.
        """
        print('Unused db_nm (delete()):', db_nm)
        collect = self.get_collect(clct_nm)
        stmt = sqla.delete(collect)
        stmt = self._filter_to_where(collect, stmt, filters)
        with engine.begin() as conn:
            res = conn.execute(stmt)
            return res

    def delete_by_id(self, db, clct_nm, id: str):
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

    def add_fld_to_all(self):
        raise NotImplementedError('add_fld_to_all')

    def append_to_list(self):
        raise NotImplementedError('append_to_list')

    def rename(self):
        raise NotImplementedError('rename')


def main():
    sqlDB = SqlDB()

    table_cols = [
            ('x', Integer),
            ('y', Integer),
        ]
    db = 'some_db'
    collect = 'some_collection'
    new_table = sqlDB.create_table(collect, table_cols)
    ic(new_table)

    doc = [
        {"_id": 0, "x": 1, "y": 1},
        {"_id": 1, "x": 2, "y": 4},
        ]
    ic(sqlDB.create(db, collect, doc))
    ic(sqlDB.read(db, collect, sort=DESC))
    ic(sqlDB.read_one(db, collect))
    return 0


if __name__ == '__main__':
    main()
