import pytest
import os

import backendcore.users.edit_groups as egrp


@pytest.fixture(scope='function')
def edit_grp():
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    NO_LISTS_REASON = "DB does not support lists as values"
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)
    egrp.add_edit_grp(egrp.TEST_EDIT_GROUP)
    yield
    egrp.del_edit_grp(egrp.TEST_NAME)


def test_fetch_edit_groups(edit_grp):
    grps = egrp.fetch_edit_groups()
    assert isinstance(grps, list)
    assert len(grps) > 0


def test_fetch_edit_group(edit_grp):
    grp = egrp.fetch_edit_group(egrp.TEST_NAME)
    assert isinstance(grp, dict)
    assert grp[egrp.NAME] == egrp.TEST_NAME


def test_fetch_edit_group_not_there():
    assert egrp.fetch_edit_group(egrp.TEST_NAME) is None


def test_fetch_edit_group_users(edit_grp):
    users = egrp.fetch_edit_group_users(egrp.TEST_NAME)
    assert isinstance(users, list)
    assert users == egrp.TEST_USERS


def test_is_user_in_group(edit_grp):
    assert egrp.is_user_in_group(egrp.TEST_USER, egrp.TEST_NAME)


def test_is_user_not_in_group(edit_grp):
    assert not egrp.is_user_in_group("She's not there", egrp.TEST_NAME)


def test_get_users_edit_group(edit_grp):
    assert egrp.get_users_edit_group(egrp.TEST_USER) == egrp.TEST_NAME


def test_get_users_edit_group_none(edit_grp):
    assert egrp.get_users_edit_group("She's not there") is None
