"""
Endpoints dealing with security.
"""
from http import HTTPStatus

import werkzeug.exceptions as wz

from flask_restx import Namespace, Resource

from backendcore.api.constants import (
    RETRIEVE,
    IS_PERMITTED,
    SEC_MANAGER,
    SEC_MANAGER_KEY,
)

from backendcore.common.constants import AUTH
from backendcore.emailer.user_email import normalize_email
import backendcore.security.sec_manager2 as sm


api = Namespace(SEC_MANAGER, 'Cyber Security info.')
parser = api.parser()
parser.add_argument(AUTH, location='headers')


@api.route(f'/{RETRIEVE}/<protocol>')
class RetrieveProtocol(Resource):
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Protocol not found')
    def get(self, protocol):
        prot = sm.fetch_by_key(protocol)
        print(f'RetrieveProtocol: {prot=}')
        if not prot:
            raise wz.NotFound(f'No security protocol with {protocol=}')
        return {SEC_MANAGER_KEY: prot.to_json()}


@api.route(f'/{IS_PERMITTED}/<protocol>/<action>/<user>')
@api.expect(parser)
class IsPermitted(Resource):
    @api.response(HTTPStatus.OK.value, 'Success')
    def get(self, protocol, action, user):
        try:
            user = normalize_email(user)
            return {IS_PERMITTED: sm.is_permitted(protocol, action, user)}
        except ValueError as e:
            raise wz.NotAcceptable(str(e))
