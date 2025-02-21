import os
import backendcore.data.db_connect as dbc

CLIENT_CODE = 'CLIENT_CODE'
DB_NM = 'db'
MFC = 'MFC'
MFC_DB = 'mfcDB'
CAT = 'CAT'
CAT_DB = 'catDB'
DEFAULT = 'default'
client_code = None

CLIENT_TABLE = {
    MFC: {DB_NM: MFC_DB},
    CAT: {DB_NM: CAT_DB},
    DEFAULT: {DB_NM: dbc.USER_DB},
}


def get_client_code():
    global client_code
    client_code = os.getenv(CLIENT_CODE, DEFAULT)
    return client_code


def get_client_db():
    get_client_code()
    return CLIENT_TABLE.get(client_code).get(DB_NM)
