"""
Authorize user to update a resource.
Will connect to our db to authenticate...
for now we just have a single OK phrase,
since we just have a single use case.
"""
from backendcore.common.constants import CREATE_DATE
import backendcore.common.time_fmts as tfmt
import backendcore.data.db_connect as dbc

from backendcore.security.constants import (
    ADD_DSRC,
)

MIN_PHRASE_LEN = 12
TEST_GOOD_PHRASE = 'Come on, Beanie!'
FT_PW_COLLECTION = 'auth_keys'
PSWD = 'key'
USER = 'user'
EXPIRE_DATE = 'expire_date'
FEATURE = 'feature'

FEATURES = [ADD_DSRC]  # just one as of now

FT_PW_DB = dbc.USER_DB  # in case we ever move it!


def fetch_by_password(password: str, user_id: str):
    """
    Fetch a record based upon a unique password.
    """
    print(f'Fetching {password} for {user_id}')
    db_nm = dbc.setup_connection(FT_PW_DB)
    return dbc.fetch_one(db_nm, FT_PW_COLLECTION,
                         filters={PSWD: password, USER: user_id})


def is_valid_password(password):
    """
    Capture our requirements here.
    """
    if not isinstance(password, str):
        return False
    if len(password) < MIN_PHRASE_LEN:
        return False
    return True


def is_valid_feature(feature):
    return feature in FEATURES


def del_password_by_id(_id: str):
    db_nm = dbc.setup_connection(FT_PW_DB)
    return dbc.del_by_id(db_nm, FT_PW_COLLECTION, _id)


def add_password(password: str, user: str,
                 expire_date=None, feature=ADD_DSRC):
    """
    Add a password and return the object id, or
    None if we fail.
    """
    if not is_valid_password(password):
        return None
    # we may want to validate user exists, but we need to think it
    # through carefully!
    if not is_valid_feature(feature):
        return None
    db_nm = dbc.setup_connection(FT_PW_DB)
    return dbc.insert_doc(db_nm, FT_PW_COLLECTION, {PSWD: password, USER: user,
                                                    CREATE_DATE:
                                                    tfmt.get_today(),
                                                    EXPIRE_DATE: None, FEATURE:
                                                    feature})


def password_exists(password: str, user_id: str):
    """
    Is this password already in the user DB?
    Returns True is so, else False.
    """
    return fetch_by_password(password, user_id) is not None


def phrase_ok(feature, phrase, user_id):
    # In the future, we will handle this differently.
    # So don't eliminate it and call `password_exists` instead!
    return password_exists(phrase, user_id)
