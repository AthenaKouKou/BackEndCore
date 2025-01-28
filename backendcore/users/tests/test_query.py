"""
This module tests our code for managing users.
"""

import random

import pytest
import os

import backendcore.data.db_connect as dbc
import backendcore.users.query as usr

# email for the a_user fixture:
A_USERS_EMAIL = 'test1729@koukoudata.com'
GARBAGE_TEST_USER = 'suhdfhjgfh'  # not even valid email addr!
GIANT_INT = 10 ** 20
TEST_LN = "ln"
TEST_FN = "fn"
TEST_SALT = "fiaklsnfef"
TEST_ORG = "koukou inc"
EMAIL_SUFFIX = '@someplace.com'
VALID_PASSWD = 'Fl000by!'
SOME_PAST_DATE = '2020-01-01'
LAST_LOGIN_DATE = '2022-01-01'

NO_LISTS_REASON = "DB does not support lists as values"


def gen_new_user_email():
    """
    We will generate a valid, random email address.
    """
    return ('user' + str(random.randint(0, GIANT_INT))
            + EMAIL_SUFFIX)


@pytest.fixture(scope='function')
def a_user():
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)
    # let's try deleting the user first, in case some earlier test failure
    # left this user in the db.
    try:
        usr.del_user(A_USERS_EMAIL)
    except ValueError:
        pass
    user = usr.create_user(A_USERS_EMAIL, TEST_FN, TEST_LN,
                           'Salted password does not matter',
                           TEST_SALT)
    yield user
    usr.del_user(A_USERS_EMAIL)


@pytest.mark.skip()
def test_get_users_edit_grp(a_user):
    edit_grp = usr.get_users_edit_grp(A_USERS_EMAIL)
    assert edit_grp == usr.TEST_EDIT_GRP


def test_list_users(a_user):
    users = usr.list_users()
    assert isinstance(users, list)
    assert len(users) > 0


def test_user_exists(a_user):
    assert usr.user_exists(A_USERS_EMAIL)


def test_user_not_exists(a_user):
    assert not usr.user_exists(GARBAGE_TEST_USER)


@pytest.mark.skip("Can't use login in users tests: reversed heirarchy!")
def test_fetch_logins(a_user, some_logins):
    logins = usr.fetch_logins(A_USERS_EMAIL)
    assert isinstance(logins[usr.LOGINS], list)


@pytest.mark.skip("Can't use login in users tests: reversed heirarchy!")
def test_add_login(a_user, some_logins):
    """
    Adding a login had better increase the number of logins.
    """
    logins1 = usr.fetch_logins(A_USERS_EMAIL)
    num_logins1 = len(logins1[usr.LOGINS])
    usr.add_login(A_USERS_EMAIL)
    logins2 = usr.fetch_logins(A_USERS_EMAIL)
    num_logins2 = len(logins2[usr.LOGINS])
    assert num_logins2 > num_logins1


@pytest.mark.skip("Can't use login in users tests: reversed heirarchy!")
def test_get_last_login(a_user, some_logins):
    assert usr.get_last_login(A_USERS_EMAIL) == LAST_LOGIN_DATE


def test_get_last_login_bad_user():
    """
    We should get a blank string for bad requests.
    """
    assert usr.get_last_login(A_USERS_EMAIL) == ''


def test_update_pw_reset_token(a_user):
    """
    See if we reset token ok: any token value will do.
    """
    TEST_TOKEN = '55b748d1-0162-486d-90ab-0d6cd84b4201'
    usr.update_pw_reset_token(A_USERS_EMAIL, TEST_SALT, TEST_TOKEN)
    user = usr.fetch_user(A_USERS_EMAIL)
    assert user[usr.PW_RES_TOK] == TEST_TOKEN


def test_create_user():
    """
    Can we create a new user?
    """
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)
    ret = usr.create_user(A_USERS_EMAIL, TEST_FN,
                          TEST_LN, VALID_PASSWD, TEST_SALT, TEST_ORG)
    assert ret is not None
    usr.del_user(A_USERS_EMAIL)


def test_create_dup_user(a_user):
    """
    Make sure we can't add a 2nd user with an existing user id.
    (Ids are currently email addresses.)
    """
    with pytest.raises(ValueError):
        usr.create_user(A_USERS_EMAIL, TEST_FN, TEST_LN,
                        VALID_PASSWD, TEST_SALT, TEST_ORG)


def test_del_no_such_user():
    with pytest.raises(ValueError):
        usr.del_user(GARBAGE_TEST_USER)


def test_update_pw(a_user):
    """
    See if the password was updated properly.
    Rather than try to sort through all the encryption,
    we'll just make sure their rest token is blanked out.
    """
    dbc.update_fld(dbc.USER_DB,
                   usr.USER_COLLECT, {usr.EMAIL: A_USERS_EMAIL},
                   usr.PW_RES_TOK, 'some token value')
    usr.update_pw(A_USERS_EMAIL, TEST_SALT, 'ff3d599da14a41add6f74')
    user = usr.fetch_user(A_USERS_EMAIL)
    assert user[usr.PW_RES_TOK] == ''


def test_replace_rpt_recips(a_user):
    new_recips = ['fred@mac.com', 'bean@gmail.com']
    usr.replace_rpt_recips(A_USERS_EMAIL, new_recips)
    user = usr.fetch_user(A_USERS_EMAIL)
    assert user[usr.RPT_RECIPS] == new_recips


def test_add_rpt_recip(a_user):
    recips = usr.add_rpt_recip(A_USERS_EMAIL, 'fred@mac.com')
    assert 'fred@mac.com' in recips


def test_add_rpt_recip_bad_user():
    recips = usr.add_rpt_recip(GARBAGE_TEST_USER, 'fred@mac.com')
    assert recips is None


def test_add_rpt_recip_bad_recip():
    with pytest.raises(TypeError):
        usr.add_rpt_recip(A_USERS_EMAIL, 7)


def test_add_rpt_recip_bad_email_format():
    with pytest.raises(ValueError):
        usr.add_rpt_recip(A_USERS_EMAIL, 'Not a valid email')


def test_get_rpt_recips(a_user):
    recips = usr.get_rpt_recips(A_USERS_EMAIL)
    assert isinstance(recips, list)


TEST_PAY_PROV_USER_ID = 'test pay prov user id'


def test_update_pay_prov_sid():
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)
    usr.create_test_user()
    usr.update_pay_prov_sid(usr.TEST_EMAIL, usr.TEST_PAY_PROV_SID)
    user = usr.fetch_user(usr.TEST_EMAIL)
    assert user[usr.PAY_PROV_SID] == usr.TEST_PAY_PROV_SID
    usr.del_user(usr.TEST_EMAIL)


def test_clear_pay_prov_sid():
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)
    usr.create_test_user()
    usr.update_pay_prov_sid(usr.TEST_EMAIL, usr.TEST_PAY_PROV_SID)
    usr.clear_pay_prov_sid(usr.TEST_PAY_PROV_SID)
    user = usr.fetch_user(usr.TEST_EMAIL)
    assert user[usr.PAY_PROV_SID] is None
    usr.del_user(usr.TEST_EMAIL)


def test_update_user_pay_prov_id():
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)
    usr.create_test_user_with_pay_prov_sid()
    usr.update_pay_prov_user_id(usr.TEST_PAY_PROV_SID, TEST_PAY_PROV_USER_ID)
    user = usr.fetch_user(usr.TEST_EMAIL)
    assert user[usr.PAY_PROV_USER_ID] == TEST_PAY_PROV_USER_ID
    usr.del_user(usr.TEST_EMAIL)
