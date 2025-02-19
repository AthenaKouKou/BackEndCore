import os
import backendcore.data.db_connect as dbc

CLIENT_CODE = 'CLIENT_CODE'
client_code = None


def get_client_code():
    global client_code
    client_code = os.getenv(CLIENT_CODE)
    if client_code is not None:
        return client_code
    else:
        return ""


def get_client_db():
    if client_code == 'MFC':
        return 'mfcDB'
    else:
        return dbc.USER_DB
