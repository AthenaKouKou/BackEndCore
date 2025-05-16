"""
Aggregate all of the api namespaces.
"""
from flask_restx import Api

from backendcore.api.sec_manager import api as sec_manager
from backendcore.api.user_data import api as user_data
from backendcore.api.user_data import ( # noqa F401
    NEW_PW,
    signup,
    EMAIL,
    FIRST_NAME,
    LAST_NAME,
    ORG,
    PW_RESET_TOK,
    SAMPLE_PASSWORD,
    SAMPLE_SIGNUP_FLDS,
    USER_ID,
    VALID_KEY,
)

api = Api(
    title='BackEndCore Test Server',
    version='1.0',
    description='An index server.',
    contact={
        'email': 'gcallah@mac.com',
        'name': 'Gene Callahan',
    },
)

api.add_namespace(sec_manager)
api.add_namespace(user_data)


def get_api_obj():
    return api
