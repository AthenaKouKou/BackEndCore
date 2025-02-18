import os

CLIENT_CODE = 'CLIENT_CODE'
client_code = None


def get_client_code():
    global client_code
    client_code = os.getenv(CLIENT_CODE)
    if client_code is not None:
        return client_code
    else:
        return ""
