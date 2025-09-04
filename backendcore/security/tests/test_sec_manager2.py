"""
Tests for the security manager.
"""
from copy import deepcopy

import json
import pytest
from unittest.mock import patch
import os

from backendcore.common.clients import FIN
import backendcore.data.db_connect as dbc
import backendcore.users.query as uqry

import backendcore.security.sec_manager2 as sm
import backendcore.security.api_key as apik

TEST_PROTOCOL_NAME = 'Test-Protocol'
TEST_PROTOCOL = sm.SecProtocol(TEST_PROTOCOL_NAME)

GOOD_VALID_USERS = sm.GOOD_VALID_USERS
TEST_NAME = sm.TEST_NAME

GOOD_SEC_CHECKS = sm.GOOD_SEC_CHECKS
GOOD_PROTOCOL = sm.GOOD_PROTOCOL

NOT_A_STR = 17  # could be any non-str value!

TEST_AUTH_KEY = 'test auth key'


@pytest.fixture(scope='function')
def temp_user():
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    NO_LISTS_REASON = os.environ.get('NO_LISTS_REASON')
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)

    try:
        uqry.delete(uqry.TEST_EMAIL)
    except Exception:
        print('User was not already in DB')
    uqry.create_test_user()
    user = uqry.fetch_by_key(uqry.TEST_EMAIL)
    print(f'{user=}')
    yield user
    uqry.delete(uqry.TEST_EMAIL)


def test_init_sec_checks_w_defaults():
    assert isinstance(sm.ActionChecks(), sm.ActionChecks)


def test_init_sec_checks_w_vals():
    assert isinstance(sm.ActionChecks(
                          auth_key=True,
                          pass_phrase=True,
                          ip_address='127.0.0.1',
                          valid_users=GOOD_VALID_USERS,
                      ),
                      sm.ActionChecks)


def test_init_sec_checks_bad_auth_key():
    with pytest.raises(TypeError):
        sm.ActionChecks(auth_key='Not a boolean!')


def test_init_sec_checks_bad_api_key():
    with pytest.raises(TypeError):
        sm.ActionChecks(api_key='Not a boolean!')


def test_init_sec_checks_bad_users():
    with pytest.raises(TypeError):
        sm.ActionChecks(valid_users='Not a list!')


def test_init_sec_checks_a_bad_user():
    with pytest.raises(TypeError):
        sm.ActionChecks(valid_users=['A list but...', NOT_A_STR])


def test_init_sec_checks_bad_ip_address():
    with pytest.raises(TypeError):
        sm.ActionChecks(ip_address=['list', 'not', 'good', 'here'])


def test_init_sec_checks_bad_pass_phrase():
    with pytest.raises(TypeError):
        sm.ActionChecks(pass_phrase=['list', 'not', 'good', 'here'])


def test_sec_checks_to_json():
    json_obj = GOOD_SEC_CHECKS.to_json()
    assert json_obj is not None
    json_str = json.dumps(json_obj)
    assert (isinstance(json_str, str))


def test_sec_checks_str():
    assert (isinstance(str(GOOD_SEC_CHECKS), str))


def test_is_sec_checks_valid_user():
    assert GOOD_SEC_CHECKS.is_valid_user(sm.TEST_EMAIL, sm.TEST_EMAIL)


def test_is_sec_checks_not_valid_user():
    assert not GOOD_SEC_CHECKS.is_valid_user('Not a user on the list!', '')


def test_is_sec_checks_valid_user_by_default():
    assert sm.NO_USERS_SEC_CHECKS.is_valid_user('Any user should be valid', '')


UQRY = 'backendcore.users.query'
FETCH_BY_AUTH_KEY = f'{UQRY}.fetch_id_by_auth_key'


@patch(f'{FETCH_BY_AUTH_KEY}', autospec=True, return_value=sm.TEST_EMAIL)
def test_is_sec_checks_valid_auth_key(mock_auth_key):
    assert GOOD_SEC_CHECKS.is_valid_auth_key(sm.TEST_EMAIL, TEST_AUTH_KEY)


@patch(f'{FETCH_BY_AUTH_KEY}', autospec=True, return_value='bademail.com')
def test_is_sec_checks_not_valid_auth_key(mock_auth_key):
    assert not GOOD_SEC_CHECKS.is_valid_auth_key(sm.TEST_EMAIL, TEST_AUTH_KEY)


@patch(f'{FETCH_BY_AUTH_KEY}', autospec=True, return_value=sm.TEST_EMAIL)
def test_sec_checks_is_permitted(mock_auth_key):
    assert GOOD_SEC_CHECKS.is_permitted(sm.TEST_EMAIL, {sm.VALIDATE_USER:
                                                        sm.TEST_EMAIL,
                                                        sm.API_KEY: apik.TEST_KEY,
                                                        sm.AUTH_KEY: TEST_AUTH_KEY,
                                                        sm.PASS_PHRASE:
                                                        sm.TEST_PHRASE,
                                                        })


def test_sec_checks_is_not_permitted():
    assert not GOOD_SEC_CHECKS.is_permitted(sm.TEST_EMAIL, {sm.VALIDATE_USER: 'Bad email',
                                                            sm.AUTH_KEY: TEST_AUTH_KEY})

def test_is_sec_checks_valid_api_key():
    apik.add(apik.TEST_KEY)
    assert GOOD_SEC_CHECKS.is_valid_api_key('', apik.TEST_KEY)


def test_is_sec_checks_not_valid_api_key():
    assert not GOOD_SEC_CHECKS.is_valid_api_key('', 'some bad key of sufficient length')


def test_init_protocol_w_defaults():
    assert isinstance(sm.SecProtocol(TEST_NAME), sm.SecProtocol)


def test_init_protocol_w_good_vals():
    assert isinstance(sm.SecProtocol(
                          TEST_NAME,
                          create=GOOD_SEC_CHECKS,
                          read=GOOD_SEC_CHECKS,
                          update=GOOD_SEC_CHECKS,
                          delete=GOOD_SEC_CHECKS
                      ),
                      sm.SecProtocol)


def test_init_protocol_w_bad_name():
    with pytest.raises(TypeError):
        sm.SecProtocol(NOT_A_STR)


def test_init_protocol_w_bad_create():
    with pytest.raises(TypeError):
        sm.SecProtocol('a name', create='Not a sec check obj')


def test_init_protocol_w_bad_read():
    with pytest.raises(TypeError):
        sm.SecProtocol('a name', read='Not a sec check obj')


def test_init_protocol_w_bad_update():
    with pytest.raises(TypeError):
        sm.SecProtocol('a name', update='Not a sec check obj')


def test_init_protocol_w_bad_delete():
    with pytest.raises(TypeError):
        sm.SecProtocol('a name', delete='Not a sec check obj')


def test_protocol_to_json():
    json_obj = GOOD_PROTOCOL.to_json()
    assert json_obj is not None
    json_str = json.dumps(json_obj)
    assert (isinstance(json_str, str))


def test_protocol_str():
    assert (isinstance(str(GOOD_PROTOCOL), str))


@patch(f'{FETCH_BY_AUTH_KEY}', autospec=True, return_value=sm.TEST_EMAIL)
def test_protocol_is_permitted(mock_auth_key):
    assert GOOD_PROTOCOL.is_permitted(sm.CREATE, sm.TEST_EMAIL,
                                      {sm.VALIDATE_USER:
                                       sm.TEST_EMAIL,
                                       sm.API_KEY: apik.TEST_KEY,
                                       sm.AUTH_KEY: TEST_AUTH_KEY,
                                       sm.PASS_PHRASE: sm.TEST_PHRASE})


def test_protocol_is_not_permitted():
    assert not GOOD_PROTOCOL.is_permitted(sm.CREATE, sm.TEST_EMAIL,
                                          {sm.VALIDATE_USER: 'Bad email'})


SEC_AUTH = 'backendcore.security.auth_key'


def add_test_protocol():
    prot = deepcopy(GOOD_PROTOCOL)
    sm.add(prot)
    return prot


@pytest.fixture(scope='function')
def temp_protocol():
    prot = add_test_protocol()
    yield prot
    sm.delete(TEST_NAME)
    # Necessary due to add/delete user testing
    dbc.del_one(sm.SEC_DB, sm.SEC_COLLECT,
                filters={sm.PROT_NM: sm.TEST_NAME})


# This one is not self-deleting.
@pytest.fixture(scope='function')
def new_protocol():
    return add_test_protocol()


def test_fetch_by_key_missing_protocol():
    assert sm.fetch_by_key('Not a security protocol!') is None


def test_fetch_by_key_protocol(temp_protocol):
    assert sm.fetch_by_key(TEST_NAME) is not None


# Test is_valid_user
def test_is_valid_user(temp_user, temp_protocol):
    print('In test_is_valid_user')
    assert sm.is_valid_user(TEST_NAME, sm.CREATE, sm.TEST_EMAIL)


def test_add():
    sm.add(TEST_PROTOCOL)
    sm.delete(TEST_PROTOCOL_NAME)


def test_add_duplicate(temp_protocol):
    with pytest.raises(ValueError):
        sm.add(sm.GOOD_PROTOCOL)


def test_add_not_protocol():
    with pytest.raises(TypeError):
        sm.add("This is not a protocol")


def test_delete(new_protocol):
    sm.delete(TEST_NAME)
    assert sm.fetch_by_key(TEST_NAME) is None


def test_delete_missing():
    with pytest.raises(ValueError):
        sm.delete('Will not find this protocol!')


@patch(f'{FETCH_BY_AUTH_KEY}', autospec=True, return_value=sm.TEST_EMAIL)
def test_is_permitted(mock_auth_key, temp_protocol):
    assert sm.is_permitted(TEST_NAME,
                           sm.CREATE,
                           user_id=sm.TEST_EMAIL,
                           api_key=apik.TEST_KEY,
                           auth_key='some auth_key',
                           phrase=sm.TEST_PHRASE)


def test_is_not_permitted_bad_email(temp_protocol):
    assert not sm.is_permitted(TEST_NAME, sm.CREATE, user_id='Bad email')


@patch(f'{FETCH_BY_AUTH_KEY}', autospec=True, return_value=sm.TEST_EMAIL)
def test_is_not_permitted_bad_phrase(mock_auth_key, temp_protocol):
    assert not sm.is_permitted(TEST_NAME, sm.CREATE, user_id=sm.TEST_EMAIL,
                               phrase='Bad phrase')


def test_fetch_journal_protocol_name():
    """
    This needs impprovement but I'm not sure how we want to go around testing
    different environment variables
    """
    assert isinstance(sm.fetch_journal_protocol_name(), str)


def test_checks_from_json():
    test_json = GOOD_SEC_CHECKS.to_json()
    checks = sm.checks_from_json(test_json)
    assert checks.is_valid_user(sm.TEST_EMAIL, sm.TEST_EMAIL)


@patch(f'{FETCH_BY_AUTH_KEY}', autospec=True, return_value=sm.TEST_EMAIL)
def test_protocol_from_json(mock_fetch_by_auth):
    test_json = GOOD_PROTOCOL.to_json()
    protocol = sm.protocol_from_json(test_json)
    assert protocol.is_permitted(sm.CREATE, sm.TEST_EMAIL,
                                 {sm.VALIDATE_USER:
                                  sm.TEST_EMAIL,
                                  sm.API_KEY: apik.TEST_KEY,
                                  sm.AUTH_KEY: TEST_AUTH_KEY,
                                  sm.PASS_PHRASE: sm.TEST_PHRASE})


def test_add_user_to_protocol(temp_protocol):
    sm.add_to_db(temp_protocol)
    NEW_TEST_USER = 'tester@test.com'
    assert not sm.is_valid_user(TEST_NAME, sm.CREATE, NEW_TEST_USER)
    sm.add_user_to_protocol(TEST_NAME, NEW_TEST_USER)
    sm.refresh_all()
    assert sm.is_valid_user(TEST_NAME, sm.CREATE, NEW_TEST_USER)


def test_add_user_to_protocol_invalid_protocol(temp_protocol):
    with pytest.raises(ValueError):
        sm.add_to_db(temp_protocol)
        NEW_TEST_USER = 'tester@test.com'
        sm.add_user_to_protocol('fake protocol', NEW_TEST_USER)


def test_add_user_to_protocol_invalid_action(temp_protocol):
    with pytest.raises(ValueError):
        sm.add_to_db(temp_protocol)
        NEW_TEST_USER = 'tester@test.com'
        sm.add_user_to_protocol(TEST_NAME, NEW_TEST_USER, ['fake action'])


def test_delete_user_from_protocol(temp_protocol):
    sm.add_to_db(temp_protocol)
    assert sm.is_valid_user(TEST_NAME, sm.CREATE, sm.TEST_EMAIL)
    sm.delete_user_from_protocol(TEST_NAME, sm.TEST_EMAIL)
    sm.refresh_all()
    assert not sm.is_valid_user(TEST_NAME, sm.CREATE, sm.TEST_EMAIL)


def test_delete_user_from_protocol_invalid_protocol(temp_protocol):
    with pytest.raises(ValueError):
        sm.add_to_db(temp_protocol)
        NEW_TEST_USER = 'tester@test.com'
        sm.delete_user_from_protocol('fake protocol', NEW_TEST_USER)


def test_delete_user_from_protocol_invalid_action(temp_protocol):
    with pytest.raises(ValueError):
        sm.add_to_db(temp_protocol)
        NEW_TEST_USER = 'tester@test.com'
        sm.delete_user_from_protocol(TEST_NAME, NEW_TEST_USER, ['fake action'])


@patch('backendcore.security.sec_manager2.get_client_code',
       autospec=True, return_value=FIN)
def test_finsight_fetch_all(mock_client_code):
    """
    If client_code is FIN, we should get the Finsight protocol loaded.
    """
    sm.fetch_all()
    print(sm.protocols)
    assert sm.exists(sm.FINSIGHT_NAME)
