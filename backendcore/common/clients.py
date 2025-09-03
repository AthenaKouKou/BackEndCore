import os
import backendcore.data.db_connect as dbc

CLIENT_CODE = 'CLIENT_CODE'
SALES_EMAIL = 'sales_email'
DB_NM = 'db'
CAT = 'CAT'
CAT_DB = 'catDB'
DMM = 'DMM'
DMM_DB = dbc.USER_DB
FIN = 'FIN'
FIN_DB = None
MFC = 'MFC'
MFC_DB = 'mfcDB'

client_code = None

# For tests: add codes and dbs as needed!
VALID_CODES = [CAT, DMM, FIN, MFC]
CODES_W_DB = [CAT, DMM, MFC]
VALID_DBS = [CAT_DB, DMM_DB, MFC_DB]
CLIENT_HAS_NO_DB = FIN
CLIENT_HAS_EMAIL = DMM
CLIENT_HAS_NO_EMAIL = FIN

CLIENT_TABLE = {
    CAT: {DB_NM: CAT_DB},
    DMM: {DB_NM: DMM_DB, SALES_EMAIL: 'seanc@datamixmaster.com'},
    FIN: {DB_NM: FIN_DB},
    MFC: {DB_NM: MFC_DB},
}


def get_client_code():
    global client_code
    if not client_code:
        client_code = os.getenv(CLIENT_CODE, DMM)
    return client_code


def get_client():
    client = CLIENT_TABLE.get(get_client_code())
    if not client:
        raise ValueError(f'Bad client code: {client_code}')
    return client


def get_client_db():
    return get_client().get(DB_NM)


def get_sales_email():
    return get_client().get(SALES_EMAIL)
