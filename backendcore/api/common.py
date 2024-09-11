"""
Common functions for API handling.
"""
from backendcore.api.constants import AUTH

GET_FROM_JSON = ['POST', 'PUT', 'PATCH']

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
    return request.headers.get(AUTH, None)