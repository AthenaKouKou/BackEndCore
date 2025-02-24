"""
Manager of security protocols.
Each protocol has a unique name.
Attempts to add a name a second time will fail with a ValueError.
"""
from copy import deepcopy
import os

from backendcore.common.constants import (  # noqa F401
    AUTH_KEY,
    CREATE,
    DELETE,
    PASS_PHRASE,
    READ,
    UPDATE,
)
from backendcore.common.clients import get_client_db
import backendcore.data.db_connect as dbc
import backendcore.security.auth_key as ak
import backendcore.users.query as uqry
from backendcore.security.constants import (
    ADD_DSRC,
    BIBLIO,
    COSMOS_JOURNAL,
    GLOSSARY,
    INFRA,
    JOURNAL,
)


IP_ADDRESS = 'ipAddress'
VALIDATE_USER = 'validateUser'

BAD_TYPE = 'Bad type for: '

VALIDATOR = 'validator'
IN_EFFECT = 'in_effect'

SEC_COLLECT = 'security_protocols'
USERS = 'users'
PASSWORD = 'password'
PROT_NM = 'protocol_name'


INFRA_PASS_PHRASE = 'Come on, Beanie!'

sec_manager = {}

VALID_ACTIONS = [
    CREATE,
    READ,
    UPDATE,
    DELETE,
]

SEC_DB = get_client_db()


def is_valid_action(action: str):
    return action in VALID_ACTIONS


class ActionChecks(object):
    """
    The defaults will mean no checks.
    """
    def __init__(self,
                 auth_key=False,
                 pass_phrase=False,
                 valid_users=None,
                 ip_address=None,
                 this_phrase=''):
        self.phrase = None
        if not isinstance(auth_key, bool):
            raise TypeError(f'{BAD_TYPE}{type(auth_key)=}')
        if not isinstance(pass_phrase, bool):
            raise TypeError(f'{BAD_TYPE}{type(pass_phrase)=}')
        elif pass_phrase:
            self.phrase = this_phrase
        if valid_users:
            if not isinstance(valid_users, list):
                raise TypeError(f'{BAD_TYPE}{type(valid_users)=}')
            for user in valid_users:
                if not isinstance(user, str):
                    raise TypeError(f'{BAD_TYPE}{type(user)=}')
        if ip_address and not isinstance(ip_address, str):
            raise TypeError(f'{BAD_TYPE}{type(ip_address)=}')
        self.checks = {
            VALIDATE_USER: {
                IN_EFFECT: valid_users is not None,
                VALIDATOR: self.is_valid_user,
            },
            AUTH_KEY: {
                IN_EFFECT: auth_key,
                VALIDATOR: self.is_valid_auth_key,
            },
            PASS_PHRASE: {
                IN_EFFECT: pass_phrase,
                VALIDATOR: self.is_valid_pass_phrase,
            },
            # IP_ADDRESS: to be developed!
        }
        self.valid_users = valid_users

    def __str__(self):
        return str(self.checks)

    def to_json(self):
        json_checks = deepcopy(self.checks)
        for check in json_checks:
            json_checks[check] = json_checks[check][IN_EFFECT]
        if self.valid_users:
            json_checks[USERS] = self.valid_users
        if self.phrase:
            json_checks[PASSWORD] = self.phrase
        return json_checks

    def is_valid_auth_key(self, user_id: str, auth_key: str) -> bool:
        auth_user = uqry.fetch_id_by_auth_key(auth_key)
        print(f'{auth_user=}')
        return user_id == auth_user

    def is_valid_pass_phrase(self, user_id: str, pass_phrase: str) -> bool:
        """
        This is a temporary expedient!
        """
        print(f'comparing {pass_phrase=} with {self.phrase=}')
        return pass_phrase == self.phrase

    def is_valid_user(self, user_id, user):
        """
        This method gets the user twice so the others can get it once!
        """
        valid = True  # by default all users are valid
        if self.valid_users:
            valid = user in self.valid_users
        return valid

    def is_permitted(self, user_id: str, check_vals: dict) -> bool:
        """
        If any test fails return False.
        """
        for check, val in self.checks.items():
            if val[IN_EFFECT]:
                if check not in check_vals:
                    raise ValueError(f'Value missing for {check}')
                if not self.checks[check][VALIDATOR](user_id,
                                                     check_vals[check]):
                    print(f'is_permitted failing on {check}')
                    return False
        return True


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

    def to_json(self):
        prot = {
            PROT_NM: self.name,
            CREATE: self.create.to_json(),
            READ: self.read.to_json(),
            UPDATE: self.update.to_json(),
            DELETE: self.delete.to_json(),
        }
        return prot

    def get_name(self):
        return self.name

    def is_permitted(self, action, user_id, check_vals):
        print(f'{check_vals=}')
        valid = True
        if action in self.__dict__:
            print(f'{action=}')
            valid = self.__dict__[action].is_permitted(user_id,
                                                       check_vals)
        return valid

    def is_valid_user(self, action, user_id):
        """
        Must pass user_id to the action twice!
        """
        valid = True
        if action in self.__dict__:
            valid = valid = self.__dict__[action].is_valid_user(user_id,
                                                                user_id)
        return valid


def is_permitted(prot_name, action, user_id: str = '', auth_key: str = '',
                 phrase: str = ''):
    prot = fetch_by_key(prot_name)
    if not prot:
        raise ValueError(f'Unknown protocol: {prot_name=}')
    check_vals = {}
    if not user_id:
        user_id = ak.fetch_user_id_by_key(auth_key)
    check_vals[VALIDATE_USER] = user_id
    check_vals[AUTH_KEY] = auth_key
    check_vals[PASS_PHRASE] = phrase
    return prot.is_permitted(action, user_id, check_vals)


def fetch_by_key(prot_name: str):
    print(f'fetch_by_key: {prot_name=}')
    ret = sec_manager.get(prot_name, None)
    print(f'{ret=}')
    return ret


def is_valid_user(prot_name: str, action: str, user: str):
    valid = True
    prot = fetch_by_key(prot_name)
    if prot:
        valid = prot.is_valid_user(action, user)
    return valid


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


def checks_from_json(check_json):
    """
    Takes the output from the db for the check and turns it into a check
    object.
    """
    return ActionChecks(auth_key=check_json.get(AUTH_KEY, False),
                        pass_phrase=check_json.get(PASS_PHRASE, False),
                        valid_users=check_json.get(USERS, None),
                        ip_address=check_json.get(IP_ADDRESS, None),
                        this_phrase=check_json.get(PASSWORD, None))


def protocol_from_json(protocol_json):
    """
    Takes the output from the db and turns it into a protocol object.
    There is only one key in the main json: it is the name of the protocol.
    """
    protocol_name = protocol_json[PROT_NM]
    create_checks = checks_from_json(protocol_json.get(CREATE, ActionChecks()))
    read_checks = checks_from_json(protocol_json.get(READ, ActionChecks()))
    update_checks = checks_from_json(protocol_json.get(UPDATE, ActionChecks()))
    delete_checks = checks_from_json(protocol_json.get(DELETE, ActionChecks()))
    return SecProtocol(protocol_name,
                       create=create_checks,
                       read=read_checks,
                       update=update_checks,
                       delete=delete_checks)


def fetch_all():
    """
    Gets all the security protocols from the db and puts them in sec_manager
    """
    data_list = dbc.fetch_all(SEC_DB,
                              SEC_COLLECT,
                              no_id=True)
    for protocol_json in data_list:
        add(protocol_from_json(protocol_json))


def add_to_db(protocol):
    ret = None
    try:
        ret = dbc.insert_doc(SEC_DB, SEC_COLLECT, protocol.to_json())
    except Exception as e:
        print(e)
    return ret


JOURNAL_CODE = os.environ.get('JOURNAL_CODE', '')

COSMOS_JOURNAL_CODE = 'CAT'


def fetch_journal_protocol_name():
    """
    We are assuming that SFA is the default journal for now
    This code should move: security should not have to know about
    JOURNAL_CODE.
    """
    return JOURNAL


if JOURNAL_CODE == COSMOS_JOURNAL_CODE:
    valid_ct_journal_users = [
        'gcallah@mac.com',
        'kristian.d.nikolov@gmail.com',
        'samuelmebersole@gmail.com',
        'bk1nyc@gmail.com',
        'lesliemarsh@gmail.com',
        'ma6700@nyu.edu',
    ]
    ct_journal_checks = ActionChecks(valid_users=valid_ct_journal_users,
                                     auth_key=True,
                                     pass_phrase=False)
    ct_journal_protocol = SecProtocol(COSMOS_JOURNAL,
                                      create=ct_journal_checks,
                                      delete=ct_journal_checks,
                                      update=ct_journal_checks)
    # add(ct_journal_protocol)
    # add_to_db(ct_journal_protocol)
else:
    # Currently leaving in old in-file data format.
    # New instantiation as follows:
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
                                  pass_phrase=False)
    glossary_protocol = SecProtocol(GLOSSARY,
                                    create=library_checks,
                                    delete=library_checks,
                                    update=library_checks)
    # add(glossary_protocol)
    # add_to_db(glossary_protocol)
    bibliography_protocol = SecProtocol(BIBLIO,
                                        create=library_checks,
                                        delete=library_checks,
                                        update=library_checks)
    # add(bibliography_protocol)
    # add_to_db(bibliography_protocol)

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
    # add(adddsrc_protocol)
    # add_to_db(adddsrc_protocol)

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
                                auth_key=False,
                                pass_phrase=True,
                                this_phrase=INFRA_PASS_PHRASE)
    infra_protocol = SecProtocol(INFRA,
                                 create=infra_checks,
                                 delete=infra_checks,
                                 read=infra_checks,
                                 update=infra_checks)
    # add(infra_protocol)
    # add_to_db(infra_protocol)

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
                                   update=journal_checks)
    # add(journal_protocol)
    # add_to_db(journal_protocol)


# for API testing:
GOOD_IP_ADDRESS = '127.0.0.1'
TEST_EMAIL = 'test@mac.com'
GOOD_VALID_USERS = [TEST_EMAIL, 'kris@smack.com']
TEST_NAME = 'test name'
TEST_PHRASE = 'test phrase'

GOOD_SEC_CHECKS = ActionChecks(auth_key=True,
                               pass_phrase=True,
                               this_phrase=TEST_PHRASE,
                               ip_address=False,
                               valid_users=GOOD_VALID_USERS,)

NO_USERS_SEC_CHECKS = ActionChecks(auth_key=True,
                                   pass_phrase=True,
                                   this_phrase=TEST_PHRASE,
                                   ip_address=GOOD_IP_ADDRESS)

GOOD_PROTOCOL = SecProtocol(TEST_NAME,
                            create=GOOD_SEC_CHECKS,
                            read=GOOD_SEC_CHECKS,
                            update=GOOD_SEC_CHECKS,
                            delete=GOOD_SEC_CHECKS)

fetch_all()


def main():
    create = ActionChecks(valid_users=['gcallah@mac.com'],
                          auth_key=True)
    sp = SecProtocol('test protocol', create=create)
    print(f'{sp=}')
    print(f'{TEST_PHRASE=}')


if __name__ == '__main__':
    main()
