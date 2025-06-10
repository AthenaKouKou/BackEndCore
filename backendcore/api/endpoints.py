"""
This module naturally will import from lots of places, but I do hope we can cut
back some of these imports!
"""
import sys

from flask import Flask
from flask_cors import CORS
from flask_restx import Resource, Namespace
from werkzeug.routing import Rule

from backendcore.emailer.contact_form import ( # noqa F401
    MESSAGE,
    SUBJECT,
    PROJECT,
)

from backendcore.common.constants import (  # noqa F401
    MAP,
    PASSWORD,
    AUTH_KEY,
)
from backendcore.api.constants import (  # noqa F401
    CONTACT,
    CREATE,
    DELETE,
    FIELDS,
    FORM,
    IS_PERMITTED,
    LIST,
    LOGIN,
    MESSAGE,
    READ,
    RESET_PW,
    RETRIEVE,
    SEC_MANAGER,
    SIGNUP,
    TEXT,
    UPDATE,
    USER_DATA,
)

from backendcore.api import (  # noqa F401
    EMAIL,
    FIRST_NAME,
    LAST_NAME,
    NEW_PW,
    ORG,
    PW_RESET_TOK,
    SAMPLE_PASSWORD,
    SAMPLE_SIGNUP_FLDS,
    USER_ID,
    VALID_KEY,
    api,
    signup,
)

ENDPOINTS = 'Endpoints'
HELLO = 'hello'

app = Flask(__name__)
app.config['RESTX_ERROR_404_HELP'] = False
app.config['JSON_SORT_KEYS'] = False

CORS(app)
api.init_app(app)

DEF_PORT = 8000
LOCAL_HOST = '127.0.0.1'

# Endpoint constants
ENDPOINT_STR = 'Available endpoints'

# security manager
SEC_MANAGER_IS_PERMITTED_W_NS = f'/{SEC_MANAGER}/{IS_PERMITTED}'
SEC_MANAGER_RETRIEVE_W_NS = f'/{SEC_MANAGER}/{RETRIEVE}'

# user data
LOGIN_W_NS = f'/{USER_DATA}/{LOGIN}'
PW_RESET_TOK_W_NS = f'/{USER_DATA}/{PW_RESET_TOK}'
RESET_PW_W_NS = f'/{USER_DATA}/{RESET_PW}'
SIGNUP_W_NS = f'/{USER_DATA}/{SIGNUP}'
VALID_KEY_W_NS = f'/{USER_DATA}/{VALID_KEY}'
CONTACT_W_NS = f'/{USER_DATA}/{CONTACT}'
CONTACT_FORM_W_NS = f'{CONTACT_W_NS}/{FORM}'

endpoints = Namespace(ENDPOINTS, 'Getting data about our endpoints.')
api.add_namespace(endpoints)

# For the frontend:
ENDPOINTS_READ = {
}


SUCCESS = 0

print(sys.path)


@api.route(f'/{HELLO}')
class Hello(Resource):
    """
    A simple endpoint to ping and see if the server is running.
    """
    def get(self):
        """
        Responds with {MESSAGE: "Hello, World!"}
        """
        return {MESSAGE: "Hello, World!"}

    def post(self):
        """
        Just testing having post and get in the same class.
        """
        return {MESSAGE: "Hello, World!"}


EP_READ_KEY = 'Endpoint Map'


# Leave this map for frontend.
@endpoints.route(f'/{MAP}')
class EndpointsRead(Resource):
    """
    A mapping of names to endpoints for the front end.
    """
    def get(self):
        """
        Returns a map of meaningful names for endpoints to URLs.
        """
        return {EP_READ_KEY: ENDPOINTS_READ}


@endpoints.route(f'/{READ}')
class Endpoints(Resource):
    """
    This endpoint lists all of our endpoints.
    For this endpoint only, it is OK to have lots of code in here, since
    this endpoint deals with endpoints.
    """
    def get(self):
        """
        List our endpoints and their documentation.
        """
        invalid_rules = [
            "/",
            "/swagger.json",
            "/swaggerui/<path:filename>",
            "/static/<path:filename>"
        ]

        rules = list(rule for rule in app.url_map.iter_rules())
        rules = filter(lambda r: r.rule not in invalid_rules, rules)

        endpoints = dict()
        for rule in rules:
            endpoints[rule.rule] = self._rule_docs(rule)

        return {ENDPOINT_STR: endpoints}

    @staticmethod
    def _rule_docs(rule: Rule):
        """
        For the given rule, assemble all supported HTTP methods and their
        documentation.
        """
        rule_class = app.view_functions[rule.endpoint].view_class
        methods = list(app.view_functions[rule.endpoint].methods)
        methods = map(lambda x: x.lower(), methods)

        method_dict = {}
        for m in methods:
            rule_func = getattr(rule_class, m)
            doc = rule_func.__doc__.strip() if rule_func.__doc__ else None
            method_dict[m] = doc

        return method_dict
