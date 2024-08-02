"""
Tests for the security manager.
"""
from copy import deepcopy

import json
import pytest
from unittest.mock import patch

import backendcore.security.auth_key as akey
import backendcore.users.query as uqry

import backendcore.security.sec_manager as sm

TEST_PROTOCOL_NM = 'Test-Protocol'
TEST_PROTOCOL = sm.SecProtocol(TEST_PROTOCOL_NM)

GOOD_AUTH_KEY = sm.GOOD_AUTH_KEY
GOOD_PASS_PHRASE = sm.GOOD_PASS_PHRASE
GOOD_IP_ADDRESS = sm.GOOD_IP_ADDRESS
GOOD_VALID_USERS = sm.GOOD_VALID_USERS
TEST_NAME = sm.TEST_NAME

GOOD_SEC_CHECKS = sm.GOOD_SEC_CHECKS
GOOD_PROTOCOL = sm.GOOD_PROTOCOL

NOT_A_STR = 17  # could be any non-str value!


@pytest.fixture(scope='function')
def temp_user():
    try:
        uqry.delete(uqry.TEST_EMAIL)
    except Exception:
        print('User was not already in DB')
    mongo_id = uqry.create_test_user()
    user = uqry.fetch_by_key(uqry.TEST_EMAIL)
    print(f'{user=}')
    yield  user
    uqry.delete(uqry.TEST_EMAIL)


def test_init_sec_checks_w_defaults():
    assert isinstance(sm.ActionChecks(), sm.ActionChecks)


def test_init_sec_checks_w_vals():
    assert isinstance(sm.ActionChecks(
                          auth_key=GOOD_AUTH_KEY,
                          pass_phrase=GOOD_PASS_PHRASE,
                          ip_address=GOOD_IP_ADDRESS,
                          valid_users=GOOD_VALID_USERS,
                      ),
                      sm.ActionChecks)


def test_init_sec_checks_bad_auth_key():
    with pytest.raises(TypeError):
        sm.ActionChecks(auth_key='Not a boolean!')


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
    assert(isinstance(json_str, str))


def test_sec_checks_str():
    assert(isinstance(str(GOOD_SEC_CHECKS), str))


def test_is_sec_checks_valid_user():
    assert GOOD_SEC_CHECKS.is_valid_user(sm.TEST_EMAIL)


def test_is_sec_checks_not_valid_user():
    assert not GOOD_SEC_CHECKS.is_valid_user('Not a user on the list!')


def test_is_sec_checks_valid_user_by_default():
    assert sm.NO_USERS_SEC_CHECKS.is_valid_user('Any user should be valid!')


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


def test_protocol_str():
    assert(isinstance(str(GOOD_PROTOCOL), str))


def test_protocol_to_json():
    json_obj = GOOD_PROTOCOL.to_json()
    assert json_obj is not None
    json_str = json.dumps(json_obj)
    assert(isinstance(json_str, str))


SEC_AUTH = 'backendcore.security.auth_key'

@patch(f'{SEC_AUTH}.is_valid_key', autospec=True, return_value=True)
def test_protocol_is_valid_user(mock_is_valid_key):
    assert GOOD_PROTOCOL.is_valid_user(sm.CREATE, sm.TEST_EMAIL, 'valid key')


@patch(f'{SEC_AUTH}.is_valid_key', autospec=True, return_value=False)
def test_protocol_is_not_valid_user(mock_is_valid_key):
    assert not GOOD_PROTOCOL.is_valid_user(sm.CREATE, 'Not a valid user!',
                                           'doesn\'t matter')


@patch(f'{SEC_AUTH}.is_valid_key', autospec=True, return_value=True)
def test_protocol_is_valid_user_no_action(mock_is_valid_key):
    # All users have access to unknown actions.
    assert GOOD_PROTOCOL.is_valid_user('Not an action!', 'User don\'t matter')


def add_test_protocol():
    prot = deepcopy(TEST_PROTOCOL)
    sm.add(prot)
    return prot


@pytest.fixture(scope='function')
def temp_protocol():
    prot = add_test_protocol()
    yield prot
    sm.delete(TEST_PROTOCOL_NM)


# This one is not self-deleting.
@pytest.fixture(scope='function')
def new_protocol():
    return add_test_protocol()


def test_fetch_by_key_missing_protocol():
   assert sm.fetch_by_key('Not a security protocol!') is None


def test_fetch_by_key_protocol(temp_protocol):
   assert sm.fetch_by_key(TEST_PROTOCOL_NM) is not None


def test_add():
    sm.add(TEST_PROTOCOL)
    sm.delete(TEST_PROTOCOL_NM)


def test_add_duplicate(temp_protocol):
    with pytest.raises(ValueError):
        sm.add(TEST_PROTOCOL)


def test_add_not_protocol():
    with pytest.raises(TypeError):
        sm.add("This is not a protocol")


def test_delete(new_protocol):
    sm.delete(TEST_PROTOCOL_NM)
    assert sm.fetch_by_key(TEST_PROTOCOL_NM) is None


def test_delete_missing():
    with pytest.raises(ValueError):
        sm.delete('Will not find this protocol!')


@patch(f'{SEC_AUTH}.is_valid_key', return_value=True, autospec=True)
def test_is_valid_user(mock_auth, temp_user, temp_protocol):
    print('In test_is_valid_user')
    auth_key = akey.get_user_key(temp_user)
    assert sm.is_valid_user(TEST_PROTOCOL_NM, sm.CREATE, temp_user,
                            'fake key')


@patch(f'{SEC_AUTH}.is_valid_key', return_value=True, autospec=True)
def test_is_valid_user_missing_protocol(mock_auth, temp_user, temp_protocol):
    assert sm.is_valid_user('No such protocol', sm.CREATE, temp_user,
                            'fake key')


@patch(f'{SEC_AUTH}.is_valid_key', return_value=True, autospec=True)
def test_is_valid_user_missing_action(mock_auth, temp_user, temp_protocol):
    assert sm.is_valid_user(TEST_PROTOCOL_NM, 'No such action!', temp_user,
                            'fake key')


@patch(f'{SEC_AUTH}.is_valid_key', return_value=False, autospec=True)
def test_is_not_valid_user(mock_auth, temp_user, temp_protocol):
    ret = sm.is_valid_user(TEST_PROTOCOL_NM, sm.CREATE, 'Not a valid user!',
                            'fake key')
    assert ret is False


@patch(f'{SEC_AUTH}.is_valid_key', return_value=True, autospec=True)
def test_is_valid_auth_key(mock_key, temp_user, temp_protocol):
    user_id = uqry.get_user_id(temp_user)
    auth_key = uqry.get_auth_key(user_id)
    print(f'{auth_key=}')
    assert sm.is_valid_auth_key(TEST_PROTOCOL_NM, sm.CREATE, auth_key)


def test_is_not_valid_auth_key(temp_protocol):
    assert not sm.is_valid_auth_key(TEST_PROTOCOL_NM, sm.CREATE, 'fake auth_key')
