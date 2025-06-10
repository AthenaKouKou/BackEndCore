"""
User data endpoints.
"""
from http import HTTPStatus

from flask import request
from flask_restx import fields, Namespace, Resource
import werkzeug.exceptions as wz


import backendcore.api.common as acmn
from backendcore.api.constants import (
    CONTACT,
    FORM,
    LOGIN,
    RESET_PW,
    SIGNUP,
    USER_DATA,
    USER_ID,
)
from backendcore.common.constants import (
    EMAIL,
    PHONE,
    AUTH_KEY,
)
from backendcore.emailer.contact import process_contact_form
from backendcore.emailer.user_email import normalize_email
import backendcore.emailer.contact_form as ctf
from backendcore.emailer.contact_form import (
    MESSAGE,
    SUBJECT,
    PROJECT,
)
import backendcore.emailer.pw_reset as pwr
import backendcore.security.auth_key as ak
import backendcore.security.password as pw
import backendcore.security.settings as secset
import backendcore.users.login as lgn
import backendcore.users.query as uqry
import backendcore.users.signup as su

from backendcore.users.query import (
    FIRST_NAME,
    LAST_NAME,
    PASSWORD,
    ORG,
)

api = Namespace(USER_DATA, 'Data about our users.')
parser = api.parser()
parser.add_argument(ak.AUTH, location='headers')

NEW_RECIPS_KEY = 'New recipients'
PW_RESET_TOK = 'pw_reset_token'
VALID_KEY = 'valid_key'


signup_fields_dict = {
    EMAIL: fields.String,
    PASSWORD: fields.String,
    FIRST_NAME: fields.String,
    LAST_NAME: fields.String,
    ORG: fields.String,
}


if acmn.signup_requires_phone():
    signup_fields_dict[PHONE] = fields.String

signup_fields = api.model('SignUp', signup_fields_dict)

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
        email = request.json.get(EMAIL, '')
        password = request.json.get(PASSWORD, '')
        if not password:
            raise wz.Unauthorized("Password cannot be blank.")
        auth_key = lgn.login(normalize_email(email), password)
        if auth_key:
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


@api.route(f'/{VALID_KEY}')
@api.expect(parser)
class IsValidKey(Resource):
    """
    Indicates whether the provided auth key is valid.
    """
    @api.doc(security=AUTH_KEY)
    @api.response(HTTPStatus.UNAUTHORIZED.value, 'Unauthorized')
    def get(self):
        """
        If the headers contain a valid key, responds with 200-OK;
        401-unauthorized otherwise.
        """
        auth_key = acmn.get_auth_key_from_request(request)
        if auth_key is None:
            raise wz.Unauthorized('Auth key missing from headers.')
        valid = ak.is_valid_key_only(auth_key)
        if not valid:
            raise wz.Unauthorized(f'Invalid login key: {auth_key=}')
        else:
            return {AUTH_KEY: 'valid'}


@api.route(f'/<{USER_ID}>')
class User(Resource):
    """
    Delete a user if credentials are OK.
    """
    @api.doc(security=ak.AUTH)
    @api.response(HTTPStatus.OK.value, 'OK')
    @api.response(HTTPStatus.UNAUTHORIZED.value, 'Unauthorized')
    @api.expect(parser)
    def delete(self, user_id):
        """
        If the headers contain a valid key, responds with 200-OK;
        401-unauthorized otherwise.
        """
        """
        Temporarily commenting this out until MFC stuff is settled
        hdrs = acmn.get_req_headers(request)
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
        """
        try:
            uqry.delete(user_id)
        except ValueError as e:
            raise wz.NotFound(f'Error deleting user {user_id}: {e}')
        return {MESSAGE: f'User {user_id} deleted'}

    @api.response(HTTPStatus.OK.value, 'OK')
    @api.response(HTTPStatus.NOT_FOUND.value, 'User not found')
    def get(self, user_id):
        """
        Returns 200 if a user exists, 404 otherwise
        """
        if uqry.exists(user_id):
            return {MESSAGE: f'User {user_id} exists'}
        else:
            raise wz.NotFound(f'User {user_id} not found')


CONTACT_FLDS = api.model('Contact', {
    EMAIL: fields.String,
    SUBJECT: fields.String,
    PROJECT: fields.String,
    MESSAGE: fields.String,
})


@api.route(f'/{CONTACT}')
class Contact(Resource):
    """
    Sends an email to our contact email
    """
    @api.expect(CONTACT_FLDS)
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE.value, 'Not acceptable')
    def post(self):
        """
        Receives a new contact request.
        """
        json = request.json
        email = json.get(EMAIL, None)
        subject = json.get(SUBJECT, None)
        project = json.get(PROJECT, None)
        message = json.get(MESSAGE, None)

        try:
            process_contact_form(email, subject, message, project)
            return {CONTACT: True}
        except Exception as err:
            raise wz.NotAcceptable(f'Contact Form error: {str(err)}')


CONTACT_FORM = 'Contact Form'


@api.route(f'/{CONTACT}/{FORM}')
class ContactForm(Resource):
    """
    Get the form to make a contact request
    """
    @api.response(HTTPStatus.OK.value, 'Success')
    def get(self):
        """
        Get the form to make a contact request
        """
        return {CONTACT_FORM: ctf.get_form()}
