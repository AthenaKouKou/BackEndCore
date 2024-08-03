"""
Contains login methods.
"""
import backendcore.users.query as usr
from backendcore.security.auth_key import set_auth_key
from backendcore.security.password import correct_pw


def login(email, password):
    """

    Parameters
    ----------
    email: str
    password: str

    Returns
    -------

    """
    if correct_pw(email, password):
        ret = set_auth_key(email)
        usr.add_login(email)
        return ret
    else:
        return None
