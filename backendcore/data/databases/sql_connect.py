import sqlalchemy as sqla

con = None
SQLITE_DB_NM = 'SQLITE_DB_NM'

engine = None


class SQLite():
    """
    Encaspulates a connection to a SQLite Server.
    """
    def __init__(self) -> None:
        global engine
        if engine is None:
            engine = self._connectDB()

    def _connectDB(self):
        print('Connecting to local, in-memory server.')
        return sqla.create_engine("sqlite+pysqlite:///:memory:", echo=True)

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
    sqlDB = SQLite()
    print(f'{sqlDB=}')
    sqlDB.create({})
    print(sqlDB.read())


if __name__ == '__main__':
    main()
