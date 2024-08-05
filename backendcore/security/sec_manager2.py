"""
Manager of security protocols.
Each protocol has a unique name.
Attempts to add a name a second time will fail with a ValueError.
"""
from copy import deepcopy

from backendcore.common.constants import (
    AUTH_KEY,
    CREATE,
    DELETE,
    PASS_PHRASE,
    READ,
    UPDATE,
)
import backendcore.data.db_connect as dbc
import backendcore.security.auth_key as aky
# import backendcore.users.query as uqry
from backendcore.security.constants import (
    ADD_DSRC,
    BIBLIO,
    COSMOS_JOURNAL,
    GLOSSARY,
    INFRA,
    JOURNAL,
)
# import backendcore.security.feature_password as ftpw


IP_ADDRESS = 'ipAddress'
VALIDATE_USER = 'validateUser'

BAD_TYPE = 'Bad type for: '


VALIDATOR = 'validator'  # noqa F401
IN_EFFECT = 'in_effect'

SEC_COLLECT = 'security_protocols'
USERS = 'users'
PROT_NM = 'protocol_name'


sec_manager = {}


class ActionChecks(object):
    """
    The defaults will mean no checks.
    """
    def __init__(self,
                 auth_key=False,
                 pass_phrase=False,
                 valid_users=None,
                 ip_address=None):
        if not isinstance(auth_key, bool):
            raise TypeError(f'{BAD_TYPE}{type(auth_key)=}')
        if not isinstance(pass_phrase, bool):
            raise TypeError(f'{BAD_TYPE}{type(pass_phrase)=}')
        if valid_users:
            if not isinstance(valid_users, list):
                raise TypeError(f'{BAD_TYPE}{type(valid_users)=}')
            for user in valid_users:
                if not isinstance(user, str):
                    raise TypeError(f'{BAD_TYPE}{type(user)=}')
        if ip_address and not isinstance(ip_address, str):
            raise TypeError(f'{BAD_TYPE}{type(ip_address)=}')
        self.checks = {
            AUTH_KEY: auth_key,
            # AUTH_KEY: {IN_EFFECT: auth_key, VALIDATOR: is_valid_auth_key}
            PASS_PHRASE: pass_phrase,
            IP_ADDRESS: ip_address,
            VALIDATE_USER: valid_users is not None
        }
        self.valid_users = valid_users

    def __str__(self):
        return str(self.checks)

    def to_json(self):
        json_checks = deepcopy(self.checks)
        return json_checks

    def is_valid_user(self, user):
        valid = True  # by default all users are valid
        if self.valid_users:
            valid = user in self.valid_users
        return valid

    def is_ok(self, check_vals: dict) -> bool:
        """
        Checking an action should be like this:
        """
        for check, val in self.checks.items():
            if val[IN_EFFECT]:
                if check not in check_vals:
                    raise ValueError(f'Value missing for {check}')
                # self.checks[VALIDATOR](check_vals[check])
                # do security checking


class SecProtocol(object):
    """
    The defaults will mean no checks for anything.
    """
    def __init__(self,
                 name,
                 create=ActionChecks(),
                 read=ActionChecks(),
                 update=ActionChecks(),
                 delete=ActionChecks()):
        if not isinstance(name, str):
            raise TypeError(f'{BAD_TYPE}{type(name)=}')
        self.name = name
        if not isinstance(create, ActionChecks):
            raise TypeError(f'{BAD_TYPE}{type(create)=}')
        self.create = create
        if not isinstance(read, ActionChecks):
            raise TypeError(f'{BAD_TYPE}{type(read)=}')
        self.read = read
        if not isinstance(update, ActionChecks):
            raise TypeError(f'{BAD_TYPE}{type(update)=}')
        self.update = update
        if not isinstance(delete, ActionChecks):
            raise TypeError(f'{BAD_TYPE}{type(delete)=}')
        self.delete = delete

    def __str__(self):
        str_rep = str(self.to_json())
        return str_rep

    def __repr__(self):
        return str(self)

    def to_json(self):
        return {
            self.name: {
                CREATE: self.create.to_json(),
                READ: self.read.to_json(),
                UPDATE: self.update.to_json(),
                DELETE: self.delete.to_json(),
            }
        }

    def get_name(self):
        return self.name

    def is_valid_user(self, action, user, auth_key: str = None):
        """
        Leaving auth_key optional until all sec protocols are converted
        """
        if not aky.is_valid_key(user, auth_key):
            return False
        valid = True
        if action in self.__dict__:
            valid = self.__dict__[action].is_valid_user(user)
        return valid


def fetch_by_key(prot_name: str):
    return sec_manager.get(prot_name, None)


def add(protocol):
    if not isinstance(protocol, SecProtocol):
        raise TypeError(f'Invalid type for protocol: {type=}')
    name = protocol.get_name()
    if name in sec_manager:
        raise ValueError(f"Can't add duplicate name to sec_manager: {name=}")
    sec_manager[name] = protocol


def delete(name):
    if name in sec_manager:
        del sec_manager[name]
    else:
        raise ValueError(f'Attempt to delete non-existent protocol: {name=}')


def is_action_ok(prot_name: str, action: str, user_id: str, phrase: str,
                 auth_key: str = None):
    return True


def create_sec_doc(name, users):
    """
    Used to add new sec protocol docs to the database
    """
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.insert_doc(db_nm, SEC_COLLECT, {PROT_NM: name, USERS: users})


def fetch_sec_users(name):
    db_nm = dbc.setup_connection(dbc.USER_DB)
    return dbc.fetch_one(db_nm, SEC_COLLECT, {PROT_NM: name})[USERS]


# Currently leaving in old in-file data format. New instantiation as follows:
# valid_lib_users = fetch_sec_users(LIB)
valid_lib_users = [
    'gcallah@mac.com',
    'vincentlaran@gmail.com',
    'abalohubert25@gmail.com',
    'abalo.hubert87@yahoo.com',
    'elen.callahan@structuredfinance.org',
    'Elen.Callahan@StructuredFinance.org',
]

library_checks = ActionChecks(valid_users=valid_lib_users,
                              auth_key=True,
                              pass_phrase=True)
glossary_protocol = SecProtocol(GLOSSARY,
                                create=library_checks,
                                delete=library_checks,
                                update=library_checks)
add(glossary_protocol)
bibliography_protocol = SecProtocol(BIBLIO,
                                    create=library_checks,
                                    delete=library_checks,
                                    update=library_checks)
add(bibliography_protocol)

# valid_adddsrc_users = fetch_sec_users(ADD_DSRC)
valid_adddsrc_users = [
    'gcallah@mac.com',
    'eugene@gmail.com',
    'vincentlaran@gmail.com',
    'abalohubert25@gmail.com',
    'abalo.hubert87@yahoo.com',
    'kristian.d.nikolov@gmail.com',
    'Elen.Callahan@StructuredFinance.org',
    'test@test.com'
]

adddsrc_checks = ActionChecks(
    valid_users=valid_adddsrc_users,
    auth_key=True,
    pass_phrase=True
)
adddsrc_protocol = SecProtocol(
    ADD_DSRC,
    create=adddsrc_checks,
    delete=adddsrc_checks,
    update=adddsrc_checks
)
add(adddsrc_protocol)

# valid_infra_users = fetch_sec_users(INFRA)
valid_infra_users = [
    'gcallah@mac.com',
    'vincentlaran@gmail.com',
    'abalohubert25@gmail.com',
    'abalo.hubert87@yahoo.com',
    'kristian.d.nikolov@gmail.com',
    'samuelmebersole@gmail.com',
    'bk1nyc@gmail.com',
]

infra_checks = ActionChecks(valid_users=valid_infra_users,
                            auth_key=True,
                            pass_phrase=True)
infra_protocol = SecProtocol(INFRA,
                             create=infra_checks,
                             delete=infra_checks,
                             read=infra_checks,
                             update=infra_checks)
add(infra_protocol)


valid_journal_users = [
    'gcallah@mac.com',
    'kristian.d.nikolov@gmail.com',
    'samuelmebersole@gmail.com',
    'bk1nyc@gmail.com',
    'Elen.Callahan@StructuredFinance.org',
    'elen.callahan@structuredfinance.org',
]

journal_checks = ActionChecks(valid_users=valid_journal_users,
                              auth_key=True,
                              pass_phrase=False)
journal_protocol = SecProtocol(JOURNAL,
                               create=journal_checks,
                               delete=journal_checks,
                               read=journal_checks,
                               update=journal_checks)
add(journal_protocol)


valid_cosmos_journal_users = [
    'gcallah@mac.com',
    'kristian.d.nikolov@gmail.com',
    'samuelmebersole@gmail.com',
    'bk1nyc@gmail.com',
    'lesliemarsh@gmail.com',
]

cosmos_journal_checks = ActionChecks(valid_users=valid_cosmos_journal_users,
                                     auth_key=True,
                                     pass_phrase=False)
cosmos_journal_protocol = SecProtocol(COSMOS_JOURNAL,
                                      create=cosmos_journal_checks,
                                      delete=cosmos_journal_checks,
                                      read=cosmos_journal_checks,
                                      update=cosmos_journal_checks)
add(cosmos_journal_protocol)


# for API testing:
GOOD_AUTH_KEY = True
GOOD_PASS_PHRASE = True
GOOD_IP_ADDRESS = '127.0.0.1'
TEST_EMAIL = 'test@mac.com'
GOOD_VALID_USERS = [TEST_EMAIL, 'kris@smack.com']
TEST_NAME = 'test name'

GOOD_SEC_CHECKS = ActionChecks(auth_key=GOOD_AUTH_KEY,
                               pass_phrase=GOOD_PASS_PHRASE,
                               ip_address=GOOD_IP_ADDRESS,
                               valid_users=GOOD_VALID_USERS,)

NO_USERS_SEC_CHECKS = ActionChecks(auth_key=GOOD_AUTH_KEY,
                                   pass_phrase=GOOD_PASS_PHRASE,
                                   ip_address=GOOD_IP_ADDRESS)

GOOD_PROTOCOL = SecProtocol(TEST_NAME,
                            create=GOOD_SEC_CHECKS,
                            read=GOOD_SEC_CHECKS,
                            update=GOOD_SEC_CHECKS,
                            delete=GOOD_SEC_CHECKS)


def main():
    create = ActionChecks(valid_users=['gcallah@mac.com'],
                          auth_key=True)
    print(create.to_json())
    sp = SecProtocol('test protocol',
                     create=create)
    print(sp.to_json())


if __name__ == '__main__':
    main()
