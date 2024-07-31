"""
Authorization key methods.
"""
import uuid

from backendcore.common.constants import AUTH
import backendcore.users.query as uqry

import backendcore.security.utils as utl
from backendcore.security.utils import naive_dt_from_db
from backendcore.security.settings import get_auth_key_ttl


def _gen_auth_key():
    return str(uuid.uuid4())


def get_user_key(user_id: str):
    """
    Return a (string) key this user can use to "stay logged in."
    (Whatever an app decides that means.)
    Return None if bad credentials.
    """
    return uqry.get_auth_key(user_id)


def update_key(user_id: str, new_key: str):
    """
    Update a user's auth key
    """
    uqry.update_auth_key(user_id, new_key)


def set_auth_key(email: str):
    """
    Generates a new API user auth key and saves it to the user.
    """
    key = _gen_auth_key()
    # TODO: the data package should not know how to update the key
    # (e.g. setting the issue date field.) Refactor so that
    # the data package knows nothing about auth.
    update_key(email, key)
    return key


def exists_user_with_key(key):
    """
    Returns true if user with the given key exists.
    """
    return uqry.fetch_by_auth_key(key) is not None


def is_key_expired(user_id, key):
    """
    Returns True if the key has expired.
    """
    user = uqry.fetch_user(user_id)
    if user:
        issue_dt = naive_dt_from_db(time_rec=user.get(uqry.ISSUE_TIME))
        now = utl.now()
        print(f'{now=}')
        print(f'{(now - issue_dt)=}')
        print(f'{get_auth_key_ttl()=}')
        return now - issue_dt >= get_auth_key_ttl()
    else:
        return True


def is_valid_key(user_id: str, auth_key: str):
    """
    Returns whether key is valid.
    Parameters
    ----------
    key: str
    """
    return (get_user_key(user_id) == auth_key and not
            is_key_expired(user_id, auth_key))


def fetch_user_id_by_key(auth_key):
    user = uqry.fetch_by_auth_key(auth_key)
    if not user:
        return None
    return uqry.get_user_id(user)


def is_valid_key_only(auth_key):
    """
    Temporary function until the frontend sends back user_id with login.
    Messy
    """
    user_id = fetch_user_id_by_key(auth_key)
    if not user_id:
        return False
    return not is_key_expired(user_id, auth_key)


def create_auth_key_hdr(auth_key):
    return {AUTH: auth_key}
