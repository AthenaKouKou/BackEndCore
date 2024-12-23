import sqlalchemy as sqla

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
            conn.execute(
                sqla.text(f"INSERT INTO {table} \
                          (_id, x, y) VALUES (:_id, :x, :y)"),
                [{"_id": 0, "x": 1, "y": 1}, {"_id": 1, "x": 2, "y": 4}],
            )

    # def read(self, db_nm, clct_nm, sort=NO_SORT,
    #          sort_fld=OBJ_ID_NM, no_id=False):
    def read(self):
        # result._metadata.keys to get field names.
        fields = []
        all_docs = {}
        with engine.connect() as conn:
            res = conn.execute(sqla.text("SELECT * from some_table"))
            for field in res._metadata.keys:
                fields.append(field)
            for rec in res:
                doc = {}
                for i in range(len(fields)):
                    doc[fields[i]] = rec[i]
                id = doc[OBJ_ID_NM]
                all_docs[id] = doc
        return all_docs

    def update(self):
        pass

    def delete(self):
        pass


def main():
    sqlDB = SqlDB()
    sqlDB.create('some_table', {})
    print(f'recs = {sqlDB.read()}')


if __name__ == '__main__':
    main()
