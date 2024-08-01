"""
Contains user password functions.
We must devise a time strategy so we use a uniform timezone
for all datetime objects.
"""
import uuid

from backendcore.common.hashing import hash_str_and_salt
import backendcore.users.query as uqry
import backendcore.security.utils as utl
from backendcore.security.settings import PW_RESET_TOK_TTL


def correct_pw(email: str, pw: str) -> True:
    """
    Checks that the user's entered password is correct.
    """
    user = uqry.fetch_user(email)
    if not user:
        return False
    return pw_matches(
        user[uqry.PASSWORD],
        pw,
        user[uqry.SALT],
    )


def pw_matches(password_hash, password, salt):
    return password_hash == hash_str_and_salt(password, salt)


def create_pw_reset_token(email: str):
    """
    Generates a password reset token and saves it to the user.
    """
    if not uqry.user_exists(email):
        return None
    token = _gen_token()
    salt = utl.gen_salt()
    hashed_token = hash_str_and_salt(token, salt)
    uqry.update_pw_reset_token(email, salt, hashed_token)
    return token


def _gen_token() -> str:
    return str(uuid.uuid4())


def reset_pw(email: str, token: str, new_pw: str):
    """
    Resets the user's password.
    """
    if not is_valid_reset_tok(email, token):
        raise ValueError("Invalid authorization token.")
    salt = utl.gen_salt()
    hashed_pw = hash_str_and_salt(new_pw, salt)
    uqry.update_pw(email, salt, hashed_pw)


def is_valid_reset_tok(email: str, token: str) -> bool:
    user = uqry.fetch_user(email)
    if not user:
        return False
    pw_res_tok = user.get(uqry.PW_RES_TOK)
    issue_dt = utl.naive_dt_from_db(
        time_rec=user.get(uqry.PW_RES_TOK_ISS_TIME))
    salt = user.get(uqry.PW_RES_SALT)
    if not pw_res_tok or not salt:
        return False
    hashed_token = hash_str_and_salt(token, salt)
    if hashed_token != pw_res_tok:
        return False
    return utl.naive_now() - issue_dt <= PW_RESET_TOK_TTL
