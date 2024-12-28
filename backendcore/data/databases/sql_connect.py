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

    def create(self, db_nm: str, clct_nm: str, doc: dict, with_date=False):
        """
        Enter a document or set of documents into a table.
        """
        ic('Unused db_nm:', db_nm)
        collect = self.get_collect(clct_nm)
        # 'Begin once' mode - so we don't need to explicitly commit every time
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

    # def read(self, db_nm, clct_nm, sort=NO_SORT,
    #          sort_fld=OBJ_ID_NM, no_id=False):
    def read(self, clct_nm):
        """
        Returns all docs from a collection.
        `sort` can be DESC, NO_SORT, or ASC.
        """
        # ic(db_nm, sort, sort_fld, no_id)
        all_docs = []
        with engine.connect() as conn:
            res = conn.execute(sqla.text(f"SELECT * from {clct_nm}"))
            all_docs = self._read_recs_to_objs(res)
        return all_docs

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
    collect = 'some_collection'
    new_table = sqlDB.create_table(collect, table_cols)
    ic(new_table)

    doc = [
        {"_id": 0, "x": 1, "y": 1},
        {"_id": 1, "x": 2, "y": 4},
        ]
    ic(sqlDB.create('some_db', collect, doc))
    ic(sqlDB.read(collect))

    return 0


if __name__ == '__main__':
    main()
