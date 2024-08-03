import backendcore.users.query as usr
import backendcore.security.utils as utils

from backendcore.users.login import login


def signup(email: str,
           pw: str,
           fname: str,
           lname: str,
           org: str = None) -> str:
    """
    Create user.

    Parameters
    ----------
    email: str
        User's email address.
    pw: str
        User's password.
    fname: str
        User's first name.
    lname: str
        User's last name
    org: str
        User's organization
    Returns
    -------
    auth_key: str
        The user's new authorization key.

    Raises
    -------
    ValueError if user already exists.
    """
    _exists(email)
    _create_user(email, pw, fname, lname, org)
    return login(email, pw)


def _exists(email: str):
    if usr.user_exists(email):
        raise ValueError("A user with that email already exists.")


def _create_user(email: str,
                 pw: str,
                 fname: str,
                 lname: str,
                 org: str = None) -> None:
    """
    Creates a user with a hashed password.
    """
    salt = utils.gen_salt()
    usr.create_user(email.lower(), fname, lname, pw, salt, org)
