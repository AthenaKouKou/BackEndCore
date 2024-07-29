"""
Code relating to edit groups.
"""
import backendcore.data.db_connect as dbc

from backendcore.common.constants import NAME

EDIT_GRP_DB = dbc.USER_DB
EDIT_GRP_COLLECT = 'edit_groups'
EDIT_GRP_FLD = 'edit_group'
USERS = 'users'

TEST_NAME = 'test_name'
TEST_USER = 'someone@somewhere.org'
TEST_USERS = [TEST_USER, 'someoneelse@somewhere.org']

TEST_EDIT_GROUP = {
    NAME: TEST_NAME,
    USERS: TEST_USERS,
}


def fetch_edit_groups() -> list:
    db_nm = dbc.setup_connection(EDIT_GRP_DB)
    return dbc.fetch_all(db_nm, EDIT_GRP_COLLECT)


def fetch_edit_group(name: str) -> dict:
    db_nm = dbc.setup_connection(EDIT_GRP_DB)
    return dbc.fetch_one(db_nm, EDIT_GRP_COLLECT,
                         filters={NAME: name})


def fetch_edit_group_users(name: str) -> list:
    edit_grp = fetch_edit_group(name)
    return edit_grp[USERS]


def is_user_in_group(user: str, name: str) -> bool:
    users = fetch_edit_group_users(name)
    return user in users


def get_users_edit_group(user: str) -> str:
    grps = fetch_edit_groups()
    for grp in grps:
        grp_nm = grp[NAME]
        if is_user_in_group(user, grp_nm):
            return grp_nm
    return None


"""
The next two functions exist for our tests, and so need not be tested
themselves.
"""


def add_edit_grp(edit_grp_dict):
    db_nm = dbc.setup_connection(EDIT_GRP_DB)
    return dbc.insert_doc(db_nm, EDIT_GRP_COLLECT, edit_grp_dict)


def del_edit_grp(edit_grp_nm):
    db_nm = dbc.setup_connection(EDIT_GRP_DB)
    return dbc.del_one(db_nm, EDIT_GRP_COLLECT, {NAME: edit_grp_nm})


def main():
    edit_grp = fetch_edit_group('SFA')
    print(edit_grp)


if __name__ == "__main__":
    main()
