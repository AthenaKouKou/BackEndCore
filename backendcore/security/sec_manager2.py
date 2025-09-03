"""
Manager of security protocols.
Each protocol has a unique name.
Attempts to add a name a second time will fail with a ValueError.
"""
from copy import deepcopy
import os
from functools import wraps

from backendcore.common.constants import (  # noqa F401
    API_KEY,
    AUTH_KEY,
    CREATE,
    DELETE,
    PASS_PHRASE,
    READ,
    UPDATE,
    CODES,
)
from backendcore.common.clients import (
    CAT,
    FIN,
    get_client_code,
    get_client_db,
)
import backendcore.data.db_connect as dbc
import backendcore.users.query as uqry
from backendcore.security.constants import (
    JOURNAL,
)
import backendcore.security.api_key as apik
import backendcore.security.auth_key as ak


IP_ADDRESS = 'ipAddress'
VALIDATE_USER = 'validateUser'

BAD_TYPE = 'Bad type for: '

VALIDATOR = 'validator'
IN_EFFECT = 'in_effect'

SEC_COLLECT = 'security_protocols'
USERS = 'users'
PASSWORD = 'password'
PROT_NM = 'protocol_name'


VALID_ACTIONS = [
    CREATE,
    READ,
    UPDATE,
    DELETE,
]

SEC_DB = get_client_db()

protocols = {}


def needs_protocols(fn):
    """
    Should be used to decorate any function that directly uses the protocols.
    Functions that call functions that use the protocols don't need this
    decorator.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not protocols:
            fetch_all()  # this will set the global
        return fn(*args, **kwargs)
    return wrapper


def is_valid_action(action: str):
    return action in VALID_ACTIONS


class ActionChecks(object):
    """
    The defaults will mean no checks.
    """
    def __init__(self,
                 auth_key=False,
                 api_key=False,
                 ip_address=None,
                 pass_phrase=False,
                 valid_users=None,
                 codes=None,
                 this_phrase=''):
        self.phrase = None
        if not isinstance(auth_key, bool):
            raise TypeError(f'{BAD_TYPE}{type(auth_key)=}')
        if not isinstance(api_key, bool):
            raise TypeError(f'{BAD_TYPE}{type(api_key)=}')
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
            API_KEY: {
                IN_EFFECT: api_key,
                VALIDATOR: self.is_valid_api_key,
            },
            AUTH_KEY: {
                IN_EFFECT: auth_key,
                VALIDATOR: self.is_valid_auth_key,
            },
            PASS_PHRASE: {
                IN_EFFECT: pass_phrase,
                VALIDATOR: self.is_valid_pass_phrase,
            },
            CODES: {
                IN_EFFECT: codes is not None,
                VALIDATOR: self.is_valid_code,
            },
            # IP_ADDRESS: to be developed!
        }
        self.valid_users = valid_users
        self.codes = codes

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
        # Kludge because we have two types of checks: those that store their
        # value only if they are active, and those that have a seperate value
        # to signifiy that they are active
        if self.codes:
            json_checks[CODES] = self.codes
        else:
            del json_checks[CODES]
        return json_checks

    def is_valid_auth_key(self, user_id: str, auth_key: str) -> bool:
        auth_user = uqry.fetch_id_by_auth_key(auth_key)
        return user_id == auth_user

    def is_valid_api_key(self, api_key: str) -> bool:
        return apik.exists(api_key)

    def is_valid_pass_phrase(self, user_id: str, pass_phrase: str) -> bool:
        """
        This is a temporary expedient!
        """
        return pass_phrase == self.phrase

    def is_valid_user(self, user_id: str, user):
        """
        This method gets the user twice so the others can get it once!
        """
        valid = True  # by default all users are valid
        if self.valid_users:
            valid = user in self.valid_users
        return valid

    def is_valid_code(self, user_id: str, code: str):
        """
        This method compares the code passed to the dictionary of valid codes.
        Note that the dictionary is of the format: {code_name: code}.
        Also, we don't actually use the user_id
        """
        valid = True
        if self.codes:
            valid = code in self.codes.values()
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

    def has_validate_user(self) -> bool:
        return self.checks[VALIDATE_USER][IN_EFFECT]


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

    def is_permitted(self,
                     action: str,
                     user_id: str,
                     check_vals: dict,
                     ) -> bool:
        valid = True
        if action in self.__dict__:
            valid = self.__dict__[action].is_permitted(user_id,
                                                       check_vals)
        return valid

    def is_valid_user(self, action: str, user_id: str) -> bool:
        """
        Must pass user_id to the action twice!
        """
        valid = True
        if action in self.__dict__:
            valid = valid = self.__dict__[action].is_valid_user(user_id,
                                                                user_id)
        return valid

    @needs_protocols
    def add_user(self, user_id: str, actions: list):
        if actions is None:
            actions = VALID_ACTIONS
        for action in actions:
            if is_valid_action(action):
                if self.__dict__[action].has_validate_user():
                    action_list = f'{action}.{USERS}'
                    dbc.append_to_list(SEC_DB, SEC_COLLECT,
                                       filter_fld_nm=PROT_NM,
                                       filter_fld_val=self.name,
                                       list_nm=action_list,
                                       new_list_item=user_id)
            else:
                raise ValueError(f'{action} is not a valid action')

    @needs_protocols
    def delete_user(self, user_id: str, actions: list):
        if actions is None:
            actions = VALID_ACTIONS
        for action in actions:
            if is_valid_action(action):
                if self.__dict__[action].has_validate_user():
                    action_list = f'{action}.{USERS}'
                    dbc.delete_from_list(SEC_DB, SEC_COLLECT,
                                         filter_fld_nm=PROT_NM,
                                         filter_fld_val=self.name,
                                         list_nm=action_list,
                                         new_list_item=user_id)
            else:
                raise ValueError(f'{action} is not a valid action')


def is_permitted(prot_name, action, user_id: str = '', auth_key: str = '',
                 api_key: str = '', phrase: str = '', code: str = None):
    prot = fetch_by_key(prot_name)
    if not prot:
        raise ValueError(f'Unknown protocol: {prot_name=}')
    check_vals = {}
    if not user_id and auth_key:
        user_id = ak.fetch_user_id_by_key(auth_key)
    check_vals[VALIDATE_USER] = user_id
    check_vals[AUTH_KEY] = auth_key
    check_vals[PASS_PHRASE] = phrase
    check_vals[CODES] = code
    return prot.is_permitted(action, user_id, check_vals)


@needs_protocols
def fetch_by_key(prot_name: str):
    ret = protocols.get(prot_name, None)
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
    if name in protocols:
        raise ValueError(f"Can't add duplicate name to protocols: {name=}")
    protocols[name] = protocol


def exists(name):
    return name in protocols


@needs_protocols
def delete(name):
    if name in protocols:
        del protocols[name]
    else:
        raise ValueError(f'Attempt to delete non-existent protocol: {name=}')


def checks_from_json(check_json):
    """
    Takes the output from the db for the check and turns it into a check
    object.
    """
    if not check_json:
        return ActionChecks()
    return ActionChecks(auth_key=check_json.get(AUTH_KEY, False),
                        pass_phrase=check_json.get(PASS_PHRASE, False),
                        valid_users=check_json.get(USERS, None),
                        ip_address=check_json.get(IP_ADDRESS, None),
                        this_phrase=check_json.get(PASSWORD, None),
                        codes=check_json.get(CODES, None))


def protocol_from_json(protocol_json):
    """
    Takes the output from the db and turns it into a protocol object.
    There is only one key in the main json: it is the name of the protocol.
    """
    protocol_name = protocol_json[PROT_NM]
    create_checks = checks_from_json(protocol_json.get(CREATE))
    read_checks = checks_from_json(protocol_json.get(READ))
    update_checks = checks_from_json(protocol_json.get(UPDATE))
    delete_checks = checks_from_json(protocol_json.get(DELETE))
    return SecProtocol(protocol_name,
                       create=create_checks,
                       read=read_checks,
                       update=update_checks,
                       delete=delete_checks)


def fetch_all() -> None:
    """
    Gets all the security protocols from the db and puts them in protocols
    """
    if len(protocols) < 1:
        if get_client_code() == FIN:
            print('Adding finsight protocol')
            protocols[FINSIGHT_NAME] = FINSIGHT_PROTOCOL
        else:
            data_list = dbc.fetch_all(SEC_DB,
                                      SEC_COLLECT,
                                      no_id=True)
            for protocol_json in data_list:
                add(protocol_from_json(protocol_json))


@needs_protocols
def refresh_all() -> bool:
    """
    Clears the sec manager dict before calling fetch_all
    """
    protocols.clear()
    return fetch_all()


@needs_protocols
def add_to_db(protocol):
    ret = None
    try:
        ret = dbc.insert_doc(SEC_DB, SEC_COLLECT, protocol.to_json())
    except Exception as e:
        print(e)
    return ret


JOURNAL_CODE = os.environ.get('JOURNAL_CODE', CAT)


def fetch_journal_protocol_name() -> str:
    """
    We are assuming that CAT is the default journal for now
    This code should move: security should not have to know about
    JOURNAL_CODE.
    """
    return JOURNAL


def add_user_to_protocol(
    protocol_name: str,
    user_id: str,
    actions: list = None,
):
    """
    Adds a user to the specified actions of a given protocol.
    If no actions are provided, they are added to all actions.
    """
    prot = fetch_by_key(protocol_name)
    if prot is None:
        raise ValueError(f'Could not find {protocol_name} protocol')
    return prot.add_user(user_id, actions)


def delete_user_from_protocol(
    protocol_name: str,
    user_id: str,
    actions: list = None,
):
    """
    Deletes a user from the specified actions of a given protocol.
    If no actions are provided, they are deleted from all actions.
    """
    prot = fetch_by_key(protocol_name)
    if prot is None:
        raise ValueError(f'Could not find {protocol_name} protocol')
    return prot.delete_user(user_id, actions)


# for API testing:
GOOD_IP_ADDRESS = '127.0.0.1'
TEST_EMAIL = 'test@mac.com'
GOOD_VALID_USERS = [TEST_EMAIL, 'kris@smack.com']
TEST_NAME = 'test name'
TEST_PHRASE = 'test phrase'
TEST_CODE = 'test code'
TEST_CODES = {TEST_CODE: 'some event name'}

GOOD_SEC_CHECKS = ActionChecks(auth_key=True,
                               api_key=False,
                               pass_phrase=True,
                               this_phrase=TEST_PHRASE,
                               ip_address=False,
                               valid_users=GOOD_VALID_USERS)

NO_USERS_SEC_CHECKS = ActionChecks(auth_key=True,
                                   pass_phrase=True,
                                   this_phrase=TEST_PHRASE,
                                   ip_address=GOOD_IP_ADDRESS)

GOOD_PROTOCOL = SecProtocol(TEST_NAME,
                            create=GOOD_SEC_CHECKS,
                            read=GOOD_SEC_CHECKS,
                            update=GOOD_SEC_CHECKS,
                            delete=GOOD_SEC_CHECKS)

FINSIGHT_NAME = 'FinsightIndex'
FINSIGHT_SEC_CHECKS = ActionChecks(api_key=True)
FINSIGHT_PROTOCOL = SecProtocol(FINSIGHT_NAME, read=FINSIGHT_SEC_CHECKS)


def main():
    create = ActionChecks(valid_users=['gcallah@mac.com'],
                          auth_key=True)
    sp = SecProtocol('test protocol', create=create)
    print(f'{sp=}')
    print(f'{TEST_PHRASE=}')


if __name__ == '__main__':
    main()
