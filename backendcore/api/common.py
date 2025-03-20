"""
Common functions for API handling.
"""
from os import getenv

from backendcore.api.constants import (
    USER_ID,
)

from backendcore.common.constants import (
    AUTH_KEY,
    AUTH,
)

import backendcore.users.query as uqry

GET_FROM_JSON = ['POST', 'PUT', 'PATCH']

EMAIL = 'email'
PARAM_SEP = '&'
KEY_VAL_SEP = '='
KEY = 0
VAL = 1


def make_md_link(text: str, url: str):
    return f'[{text}]({url})'


def list_from_sep_args(args, sep=','):
    """
    Return a list from some (comma?) separated args.
    """
    return args.split(sep)


def get_args_from_req(request) -> dict:
    """
    Gets the relevant args from the request.
    If the request method is GET, we get the args from the url parameters.
    If the request method is in GET_FROM_JSON,
    we get the args from the request body.
    """
    if request.method == 'GET':
        args = request.args.to_dict()
    elif request.method in GET_FROM_JSON:
        args = request.json
    else:
        raise TypeError(f"Method {request.method} not allowed.")
    return args


def get_args_from_str(param_str: str):
    """
    Split up an HTML-style param string into a dict.
    """
    args = {}
    try:
        params = param_str.split(PARAM_SEP)
        for param in params:
            key_val = param.split(KEY_VAL_SEP)
            args[key_val[KEY]] = key_val[VAL]
    except Exception as err:
        raise ValueError(f'Bad param string: {param_str=}; {err=}')
    return args


def get_auth_key_from_request(request) -> str:
    """
    Gets the auth key from the request's header.
    """
    auth_key = request.headers.get(AUTH, None)
    if auth_key is None:
        auth_key = request.headers.get(AUTH_KEY, None)
    return auth_key


def get_auth_key_and_user(request):
    user_id = None
    if hasattr(request, 'json'):
        jdata = request.json
        auth_key = get_auth_key_from_request(request)
        user_id = jdata.get(USER_ID, None)
        if not user_id:
            user_id = jdata.get(EMAIL, None)
    if not user_id:
        user_id = uqry.fetch_id_by_auth_key(auth_key)
    return (auth_key, user_id)


REQ_EMAIL = 'REQ_EMAIL'


def signup_requires_phone():
    """
    Checks if the current server requires a phone number for signup
    """
    req_phone = getenv(REQ_EMAIL, None)
    return req_phone is not None


def get_req_headers(request):
    return dict(request.headers)
