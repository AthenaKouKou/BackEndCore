import os
import backendcore.data.db_connect as dbc

CLIENT_CODE = 'CLIENT_CODE'
SALES_EMAIL = 'sales_email'
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
    # DEFAULT: {DB_NM: dbc.USER_DB, SALES_EMAIL:'seanc@datamixmaster.com'},
    DEFAULT: {DB_NM: dbc.USER_DB, SALES_EMAIL: 'kristian.d.nikolov@gmail.com'},
}


def get_client_code():
    global client_code
    client_code = os.getenv(CLIENT_CODE, DEFAULT)
    return client_code


def get_client_db():
    get_client_code()
    return CLIENT_TABLE.get(client_code).get(DB_NM)


def get_sales_email():
    get_client_code()
    return CLIENT_TABLE.get(client_code).get(SALES_EMAIL)
