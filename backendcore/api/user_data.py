
"""
User data endpoints.
"""
from http import HTTPStatus

from flask import request
from flask_restx import fields, Namespace, Resource
import werkzeug.exceptions as wz


import backendcore.api.common as acmn
from backendcore.api.constants import (
    LOGIN,
    MESSAGE,
    SIGNUP,
    USER_DATA,
)
from backendcore.common.constants import EMAIL, PHONE, AUTH_KEY
from backendcore.emailer.user_email import normalize_email
import backendcore.emailer.pw_reset as pwr
import backendcore.security.auth_key as ak
import backendcore.security.settings as secset
import backendcore.security.password as pw
import backendcore.users.login as lgn
import backendcore.users.signup as su
import backendcore.users.query as uqry

from backendcore.users.query import (
    FIRST_NAME,
    LAST_NAME,
    PASSWORD,
    ORG,
)

from server.utils import get_req_headers

api = Namespace(USER_DATA, 'Data about our users.')
parser = api.parser()
parser.add_argument(ak.AUTH, location='headers')

FIRST_TEMP = 'first_id'
LAST_TEMP = 'last_id'
NEW_RECIPS_KEY = 'New recipients'
PW_RESET_TOK = 'pw_reset_token'
RECIP_EMAIL = 'recip_email'
RESET_PW = 'reset_pw'
USER_ID = 'user_id'
VALID_KEY = 'valid_key'
EDIT_GRP_USERS = 'edit_grp_users'


signup_fields = api.model('SignUp', {
    EMAIL: fields.String,
    PASSWORD: fields.String,
    FIRST_NAME: fields.String,
    LAST_NAME: fields.String,
    ORG: fields.String,
    PHONE: fields.String,
})

SAMPLE_PASSWORD = 'valid_password'

SAMPLE_SIGNUP_FLDS = {
    EMAIL: 'valid_email@validurl.com',
    PASSWORD: SAMPLE_PASSWORD,
    FIRST_NAME: 'George',
    LAST_NAME: 'Stephanopolous',
    ORG: 'Your Company',
}


def signup(email, passwd, fname, lname, org=None):
    """
    Little func to share with tests.
    """
    return su.signup(email, passwd, fname, lname, org=org)


@api.route(f'/{SIGNUP}')
class SignUp(Resource):
    """
    For signing up a user.
    """
    @api.expect(signup_fields)
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.CONFLICT.value, 'Conflict')
    def post(self):
        """
        Create user and return an auth key.
        The major failure we anticipate is when the user already exists.
        """
        args = request.json
        try:
            first = args.get(FIRST_NAME, '')
            last = args.get(LAST_NAME, '')
            auth_key = signup(normalize_email(args[EMAIL]), args[PASSWORD],
                              first, last, args.get(ORG))
            return {AUTH_KEY: auth_key}
        except ValueError as e:
            raise wz.Conflict(f'Could not sign up user: {str(e)}')


login_fields = api.model('Login', {
    EMAIL: fields.String,
    PASSWORD: fields.String
})


@api.route(f'/{LOGIN}')
class Login(Resource):
    """
    For user login.
    """
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.UNAUTHORIZED.value, 'Unauthorized')
    @api.expect(login_fields)
    def post(self):
        """
        Login and return an auth key.
        """
        if auth_key := lgn.login(normalize_email(request.json[EMAIL]),
                                 request.json[PASSWORD]):
            return {AUTH_KEY: auth_key}
        else:
            raise wz.Unauthorized("Your email or password is invalid.")


TEST_ENV = 'test'


@api.route(f'/{PW_RESET_TOK}/<email>')
class ReqPwReset(Resource):
    """
    Handles requests for a token to reset a user's password.
    """
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE.value, 'Not acceptable')
    @api.doc(params={TEST_ENV:
                     'In a testing environment. (OPTIONAL; default: false)'})
    def get(self, email):
        """
        Sends password reset link to user.
        """
        email = normalize_email(email)
        args = acmn.get_args_from_req(request)
        tok = pw.create_pw_reset_token(email)
        if not tok:
            raise wz.NotAcceptable(f"Can't create password reset: {email=}")
        seconds = secset.get_pw_reset_ttl_seconds()
        testing_env = args.get(TEST_ENV, False)
        if testing_env == '0':
            testing_env = False
        try:
            pwr.send_pw_reset(tok, email, seconds, testing_env=testing_env)
        except ValueError as e:
            raise wz.NotAcceptable('Perhaps you forgot to set base url env '
                                   + f'var? {e}')
        return {MESSAGE: 'Password reset token sent.'}


NEW_PW = 'new_password'


reset_pw_fields = api.model('ResetPassword', {
    USER_ID: fields.String,
    PW_RESET_TOK: fields.String,
    NEW_PW: fields.String,
})


@api.route(f'/{RESET_PW}')
class ResetPassword(Resource):
    """
    Resets a user's password.
    """
    @api.expect(reset_pw_fields)
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE.value, 'Not acceptable')
    def patch(self):
        """
        Resets the user's password if they have a valid token.
        """
        try:
            args = request.json
            return pw.reset_pw(args.get(USER_ID, ''),
                               args.get(PW_RESET_TOK, ''),
                               args.get(NEW_PW, ''))
        except Exception as err:
            raise wz.NotAcceptable(f'Password reset error: {str(err)}')


is_valid_key_fields = api.model('IsValidKey', {
    USER_ID: fields.String,
})


@api.route(f'/{VALID_KEY}')
@api.expect(parser)
class IsValidKey(Resource):
    """
    Indicates whether the provided auth key is valid.
    """
    @api.doc(security=AUTH_KEY)
    @api.expect(is_valid_key_fields)
    @api.response(HTTPStatus.UNAUTHORIZED.value, 'Unauthorized')
    def post(self):
        """
        If the headers contain a valid key, responds with 200-OK;
        401-unauthorized otherwise.
        """
        hdrs = get_req_headers(request)
        if AUTH_KEY not in hdrs:
            raise wz.Unauthorized('Auth key missing from headers.')
        else:
            auth_key = hdrs[AUTH_KEY]
        """
        Temporarily commented out until the issue w/ frontend login is resolved
        args = request.json
        if args is None or USER_ID not in args:
            raise wz.Unauthorized('User_id missing from headers.')
        valid = ak.is_valid_key(args[USER_ID], hdrs[AUTH_KEY])
        """
        valid = ak.is_valid_key_only(auth_key)
        if not valid:
            raise wz.Unauthorized(f'Invalid login key: {auth_key=}')
        else:
            return {AUTH_KEY: 'valid'}


@api.route('/<user_id>')
@api.expect(parser)
class DeleteUser(Resource):
    """
    Delete a user if credentials are OK.
    """
    @api.doc(security=ak.AUTH)
    @api.response(HTTPStatus.OK.value, 'OK')
    @api.response(HTTPStatus.UNAUTHORIZED.value, 'Unauthorized')
    def delete(self, user_id):
        """
        If the headers contain a valid key, responds with 200-OK;
        401-unauthorized otherwise.
        """
        hdrs = get_req_headers(request)
        if ak.AUTH not in hdrs:
            raise wz.Unauthorized('Login key missing from headers.')
        else:
            auth_key = hdrs[ak.AUTH]
        valid = ak.is_valid_key(user_id, auth_key)
        if not valid:
            raise wz.Unauthorized(f'Invalid login: {user_id=}')
        else:
            try:
                uqry.delete(user_id)
            except ValueError as e:
                raise wz.NotFound(e)
            return {MESSAGE: f'User {user_id} deleted'}
