import pytest
import backendcore.security.feature_password as ftpw

TEST_GOOD_PSWD = 'This should be a fine password 2day!'
TEST_BAD_PSWD = '2short'

TEST_GOOD_USER = 'gcallah@mac.com'


@pytest.fixture(scope='function')
def temp_pswd():
    _id = ftpw.add_password(TEST_GOOD_PSWD, 'gcallah@mac.com')
    yield
    ftpw.del_password_by_id(_id)


def test_fetch_by_password(temp_pswd):
    assert ftpw.fetch_by_password(TEST_GOOD_PSWD, TEST_GOOD_USER) is not None


def test_fetch_by_bad_password(temp_pswd):
    assert ftpw.fetch_by_password(TEST_BAD_PSWD, TEST_GOOD_USER) is None


def test_is_valid_password():
    assert ftpw.is_valid_password(TEST_GOOD_PSWD)


def test_is_not_valid_password_too_short():
    assert not ftpw.is_valid_password(TEST_BAD_PSWD)


def test_is_not_valid_password_bad_type():
    assert not ftpw.is_valid_password(17)


def test_is_valid_feature():
    assert ftpw.is_valid_feature(ftpw.ADD_DSRC)


def test_is_not_valid_feature():
    assert not ftpw.is_valid_feature('Surely not a feature!')


def test_good_phrase(temp_pswd):
    assert ftpw.phrase_ok(ftpw.ADD_DSRC, TEST_GOOD_PSWD, TEST_GOOD_USER)


def test_bad_phrase():
    assert not ftpw.phrase_ok(ftpw.ADD_DSRC, TEST_BAD_PSWD, TEST_GOOD_USER)


def test_add_password():
    assert ftpw.add_password(TEST_GOOD_PSWD, TEST_GOOD_USER) is not None


def test_add_bad_password():
    assert ftpw.add_password(TEST_BAD_PSWD, TEST_GOOD_USER) is None
