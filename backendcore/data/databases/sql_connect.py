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
    '''Return the closest sql type for a given python type'''
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

    def create_table(self, table_name, columns=None):
        # Sets up a new table schema and creates it in the DB
        new_table = sqla.Table(
            table_name,
            self.mdata,
            sqla.Column(OBJ_ID_NM, sqla.Integer, primary_key=True),
        )
        for column in columns:
            new_table.append_column(sqla.Column(column[0], column[1]))
        self.mdata.create_all(engine)
        return new_table

    # def get_collect(self, db_nm: str, clct_nm: str):
    def get_collect(self, clct_nm: str):
        return self.mdata.tables.get(clct_nm)

    def get_field(self, collect, col_nm: str):
        return collect.c.get(col_nm)
    
    def _create_clct_from_doc(self, clct_nm: str, doc: dict):
        """
        Creates a new table where each field is the datatype
        of that field in the supplied document.
        """
        if type(doc) == list:
            doc = doc.pop()
        columns = []
        for column in doc:
            tp = _type_py2sql(type(doc[column]))
            columns.append((column, tp))
        res = self.create_table(clct_nm, columns)
        return self.get_collect(clct_nm)

    def create(self, db_nm: str, clct_nm: str, doc, with_date=False):
        """
        Enter a document or set of documents into a table.
        """
        ic('Unused db_nm:', db_nm)
        if with_date:
            print('with_date format is not supported at present time')
        collect = self.get_collect(clct_nm)
        # If collection doesn't exist, create it based on doc
        if not collect:
            collect = self._create_clct_from_doc(clct_nm, doc)
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

    def _asmbl_sort_slct(self, clct_nm, sort=ASC, sort_fld=OBJ_ID_NM):
        collect = self.get_collect(clct_nm)
        stmt = sqla.select(collect)
        if sort == ASC:
            return stmt.order_by(self.get_field(collect, sort_fld).asc())
        if sort == DESC:
            return stmt.order_by(self.get_field(collect, sort_fld).desc())
        return stmt

    def read(self, db_nm, clct_nm,
             sort=NO_SORT, sort_fld=OBJ_ID_NM, no_id=False):
        """
        Returns all docs from a collection.
        `sort` can be DESC, NO_SORT, or ASC.
        """
        ic(db_nm, sort, sort_fld, no_id)
        all_docs = []
        stmt = self._asmbl_sort_slct(clct_nm, sort=sort, sort_fld=sort_fld)
        with engine.connect() as conn:
            res = conn.execute(stmt)
            all_docs = self._read_recs_to_objs(res)
        return all_docs

    # def select(self, db_nm, clct_nm, filters={}, sort=NO_SORT, sort_fld='_id',
    #         proj=NO_PROJ, limit=DOC_LIMIT, no_id=False, exclude_flds=None):
    def select(self, db_nm, clct_nm, filters={}, sort=NO_SORT, sort_fld='_id',
            proj=None, limit=None, no_id=False, exclude_flds=None):
        """
        Select records from a collection matching filters.
        """
        ic(proj, limit, no_id, exclude_flds)
        return self.read(db_nm, clct_nm, sort=sort, sort_fld=sort_fld )

    def update(self):
        pass

    def delete(self):
        pass


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

    return 0


if __name__ == '__main__':
    main()
