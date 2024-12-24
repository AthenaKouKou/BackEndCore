import sqlalchemy as sqla

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
        if engine is None:
            engine = self._connectDB()

    def _connectDB(self):
        connect_str = DB_TABLE[self.variant]
        return sqla.create_engine(connect_str, echo=True)

    def create(self, table: str, record: dict):
        """
        This will also create the table for the moment!
        Return?
        """
        print(record)
        # 'Begin once' mode - so we don't need to explicitly commit every time
        with engine.begin() as conn:
            conn.execute(sqla.text(
                f"CREATE TABLE {table} (_id int, x int, y int)")
                )
            res = conn.execute(
                sqla.text(f"INSERT INTO {table} \
                          (_id, x, y) VALUES (:_id, :x, :y)"),
                [{"_id": 0, "x": 1, "y": 1}, {"_id": 1, "x": 2, "y": 4}],
            )
            return res

    def read_recs_to_objs(self, res):
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
        all_docs = []
        with engine.connect() as conn:
            res = conn.execute(sqla.text(f"SELECT * from {clct_nm}"))
            all_docs = self.read_recs_to_objs(res)
        return all_docs

    def update(self):
        pass

    def delete(self):
        pass


def main():
    sqlDB = SqlDB()
    print(sqlDB.create('some_table', {}))
    print(f'recs = {sqlDB.read("some_table")}')
    return 0


if __name__ == '__main__':
    main()
