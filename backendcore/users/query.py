"""
This is our interface to our user data.
AT PRESENT, the user's id is their email.
We should not assume that is true forever!
Thus, we should cut over from calling the ID
field `email` to calling it `user_id`.
"""
from backendcore.common.hashing import hash_str_and_salt
import backendcore.common.valid as vld
from backendcore.common.constants import EMAIL
import backendcore.data.db_connect as dbc
from backendcore.users.edit_groups import EDIT_GRP_FLD, TEST_NAME
import backendcore.common.time_fmts as tfmt


TEST_EDIT_GRP = TEST_NAME

SUCCESS = 0

USER_COLLECT = 'users'
LOGIN_COLLECT = 'logins'
FIRST_NM = 'first_name'
LAST_NM = 'last_name'
USER_ID = EMAIL
SALT = 'salt'
PASSWD = 'password'
ORG = 'org'
KEY = 'key'
LOGINS = 'logins'
ISSUE_TIME = 'issue_time'
PW_RES_TOK = 'pw_reset_tok'
PW_RES_TOK_ISS_TIME = 'pw_reset_tok_issue_time'
PW_RES_SALT = 'pw_reset_salt'
PAY_PROV_ID = 'pay_prov_id'
PAY_PROV_SID = 'pay_prov_session_id'
PAY_PROV_USER_ID = 'pay_prov_user_id'
# some users may record email addresses they wish to send reports to:
RPT_RECIPS = 'rpt_recipients'


def list_users():
    db_nm = dbc.setup_connection(dbc.USER_DB)
    users = dbc.fetch_all(db_nm, USER_COLLECT)
    return users


def fetch_by_key(user_id: str):
    """
    User IDs must be unique in our db, so we can fetch a unique
    record based on just user_id.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.fetch_one(db_nm, USER_COLLECT,
                         filters={EMAIL: user_id})


def fetch_user(user_id: str):
    """
    Deprecated; use fetch_by_key.
    """
    return fetch_by_key(user_id)


def create_user(email: str, firstname: str, lastname: str,
                passwd: str, salt: str, org: str = None):
    """
    Creates a new user.
    If the user email exists, raise ValueError.
    Otherwise, return the new user's id.
    We hash the password here.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    if exists(email):
        raise ValueError(f'{email=} already exists in userDB')
    else:
        hashed_pw = hash_str_and_salt(passwd, salt)
        return dbc.insert_doc(db_nm, USER_COLLECT,
                              {EMAIL: email,
                               FIRST_NM: firstname,
                               LAST_NM: lastname,
                               PASSWD: hashed_pw,
                               SALT: salt,
                               ORG: org,
                               KEY: '',
                               LOGINS: [tfmt.get_today()],
                               RPT_RECIPS: [],
                               ISSUE_TIME: tfmt.get_today(),
                               PW_RES_TOK: '',
                               PW_RES_TOK_ISS_TIME: '',
                               PW_RES_SALT: ''})


def delete(user_id: str):
    """
    Deletes a user.
    If the user user_id doesn't exist, raise ValueError.
    Otherwise, return SUCCESS
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    if not exists(user_id):
        raise ValueError(f'{user_id=} is not in the database.')
    else:
        dbc.del_one(db_nm, USER_COLLECT, {EMAIL: user_id})
        return SUCCESS


def del_user(user_id: str):
    """
    Deprecated: use `delete()`
    """
    return delete(user_id)


def exists(user_id: str):
    """
    Is this id already in the user DB?
    Returns True is so, else False.
    """
    return fetch_user(user_id) is not None


def user_exists(user_id: str):
    """
    Deprecated: use `exists` instead.
    """
    return exists(user_id)


def get_users_edit_grp(user_id: str):
    edit_grp = None
    user = fetch_user(user_id)
    print(f'{user=}')
    if user:
        edit_grp = user.get(EDIT_GRP_FLD, None)
    return edit_grp


def add_login(user_id: str, date=None):
    """
    Records a new login.
    Potentially passing a date is useful for testing.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    if exists(user_id):
        print(f'adding login for {user_id=}')
        if date is None:
            date = tfmt.get_today()
        dbc.append_to_list(db_nm, LOGIN_COLLECT, EMAIL, user_id, LOGINS, date)


def fetch_logins(user_id: str):
    """
    Fetches all logins for a user as a list.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    print('Calling fetch_logins')
    if exists(user_id):
        return dbc.fetch_one(db_nm, LOGIN_COLLECT,
                             filters={EMAIL: user_id})


def get_last_login(user_id):
    logins = fetch_logins(user_id)
    if logins and len(logins[LOGINS]):
        return logins[LOGINS][-1]
    else:
        return ''


def add_rpt_recip(user_id: str, rec_email: str):
    """
    Adds a report recipient to a user doc.
    Return the new list of recipients, or None
    if the user doesn't exist.
    Of course the `else` clause isn't needed...
    but it makes the code clearer.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    if not isinstance(rec_email, str):
        raise TypeError(f'Recipient email must be a str; {rec_email=}')
    if not vld.is_valid_email(rec_email):
        raise ValueError(f'Invalid recipient email: {rec_email=}')
    user = fetch_user(user_id)
    if user:
        if RPT_RECIPS not in user:
            user[RPT_RECIPS] = []
        user[RPT_RECIPS].append(rec_email)
        dbc.update_fld(db_nm, USER_COLLECT, {EMAIL: user_id},
                       RPT_RECIPS, user[RPT_RECIPS])
        return user[RPT_RECIPS]
    else:
        return None


def replace_rpt_recips(user_id: str, recips: list):
    """
    Adds a report recipient to a user doc.
    Return the new list of recipients, or None
    if the user doesn't exist.
    Of course the `else` clause isn't needed...
    but it makes the code clearer.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    if not isinstance(recips, list):
        raise TypeError(f'Recipients must be a list: {recips=}')
    if exists(user_id):
        ret = dbc.update_fld(db_nm, USER_COLLECT, {EMAIL: user_id},
                             RPT_RECIPS, recips)
        return ret
    else:
        return None


def get_rpt_recips(user_id: str):
    """
    Lists report recipients for a user.
    """
    user = fetch_user(user_id)
    if user:
        if RPT_RECIPS not in user:
            user[RPT_RECIPS] = []
        return user[RPT_RECIPS]
    else:
        return None


def update_pw_reset_token(user_id: str, salt: str, hashed_token: str):
    """
    Updates password resets for a user_id.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.update_doc(db_nm, USER_COLLECT, {EMAIL: user_id},
                          {PW_RES_SALT: salt,
                           PW_RES_TOK: hashed_token,
                           PW_RES_TOK_ISS_TIME: tfmt.now()})


def update_pw(user_id, salt, hashed_pw):
    """
    Updates a user's password (given an user_id)
    and then blanks out the reset salt/token/issue_time,
    so that if they need to reset again, they must get a new token.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.update_doc(db_nm, USER_COLLECT, {EMAIL: user_id},
                          {SALT: salt,
                          PASSWD: hashed_pw,
                          PW_RES_SALT: '',
                          PW_RES_TOK: '',
                          PW_RES_TOK_ISS_TIME: ''})


def get_auth_key(user_id):
    user = fetch_user(user_id)
    if user:
        return user.get(KEY, None)
    else:
        return None


def fetch_by_auth_key(key):
    """
    Fetch a user by their authorization key.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.fetch_one(db_nm, USER_COLLECT,
                         filters={KEY: key})


def update_auth_key(user_id, auth_key):
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.update_doc(db_nm, USER_COLLECT, {EMAIL: user_id},
                          {KEY: auth_key, ISSUE_TIME: tfmt.now()})


def update_pay_prov_sid(user_id, session_id):
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.update_fld(
        db_nm,
        USER_COLLECT,
        {EMAIL: user_id},
        PAY_PROV_SID,
        session_id
    )


def clear_pay_prov_sid(sid):
    assert isinstance(sid, str)
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.update_fld(
        db_nm,
        USER_COLLECT,
        {PAY_PROV_SID: sid},
        PAY_PROV_SID,
        None
    )


def update_pay_prov_user_id(sid: str, pay_prov_user_id: str):
    """
    Identifies a user by his session id and sets his payment provider id.
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.update_fld(
        db_nm,
        USER_COLLECT,
        {PAY_PROV_SID: sid},
        PAY_PROV_USER_ID,
        pay_prov_user_id,
    )


def get_user_id(user):
    return user.get(EMAIL, None)


TEST_EMAIL = 'test_user@koukoudata.com'
TEST_PAY_PROV_SID = 'test pay prov sid'
TEST_PASSWORD = 'a password'


def create_test_user():
    return create_user(
        TEST_EMAIL,
        'test',
        'user',
        TEST_PASSWORD,
        'some salt',
        'an org'
    )


def create_test_user_with_pay_prov_sid(sid=TEST_PAY_PROV_SID):
    db_nm = dbc.setup_connection(dbc.USER_DB)
    create_user(
        TEST_EMAIL,
        'test',
        'user',
        # NOTE: this password isn't hashed
        # so this test user won't have a valid password
        'a password',
        'a salt',
        'an org'
    )
    dbc.update_fld(
        db_nm,
        USER_COLLECT,
        {EMAIL: TEST_EMAIL},
        PAY_PROV_SID,
        sid,
    )
