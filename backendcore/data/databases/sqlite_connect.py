import sqlite3 as sqlt
import os

con = None
SQLITE_DB_NM = 'SQLITE_DB_NM'


class SQLite():
    """
    Encaspulates a connection to a SQLite Server.
    """
    def __init__(self) -> None:
        self.con = self._connectDB()

    def _connectDB(self):
        global con
        db = os.environ.get(SQLITE_DB_NM, '/tmp/sqlite_local.db')
        if con is None:
            print('Connecting to local server.')
            con = sqlt.connect(db)
        return con

    def get_cursor(self):
        return self.con.cursor()

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
