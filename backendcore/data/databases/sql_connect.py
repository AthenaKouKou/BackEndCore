import sqlalchemy as sqla

con = None
SQLITE_DB_NM = 'SQLITE_DB_NM'

SQLITE_MEM = 'sqllite_mem'
SQLITE_MEM_STR = 'sqlite+pysqlite:///:memory:'

DB_TABLE = {
    SQLITE_MEM: SQLITE_MEM_STR,
}

engine = None


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

    def create(self, record: dict):
        """
        This will also create the table for the moment!
        Return?
        """
        print(record)
        with engine.connect() as conn:
            conn.execute(sqla.text("CREATE TABLE some_table (x int, y int)"))
            conn.execute(
                sqla.text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
                [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
            )
            conn.commit()
        return con

    def read(self):
        recs = []
        with engine.connect() as conn:
            res = conn.execute(sqla.text("SELECT * from some_table"))
            for rec in res:
                recs.append(rec)
        return recs

    def update(self):
        pass

    def delete(self):
        pass


def main():
    sqlDB = SqlDB()
    sqlDB.create({})
    print(sqlDB.read())


if __name__ == '__main__':
    main()
