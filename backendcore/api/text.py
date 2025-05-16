"""
Endpoints for text management.
"""
from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields

import werkzeug.exceptions as wz

from backendcore.common.constants import (
    AUTH,
    # CODE,
)

import backendcore.api.common as acmn
from backendcore.api.constants import (
    DELETE,
    FIELDS,
    FORM,
    MESSAGE,
    READ,
    UPDATE,
)

import backendcore.security.sec_manager2 as sm
from backendcore.security.constants import EDIT_TEXT

from backendcore.users.query import fetch_id_by_auth_key

import backendcore.text.fields as tflds
from backendcore.text.fields import (
    EDITOR,
    TEXT,
    TEXT_DISP_NAME,
)
import backendcore.text.form as tform
import backendcore.text.query as tqry


api = Namespace(TEXT_DISP_NAME, 'Editing text data for our sites.')
parser = api.parser()
parser.add_argument(AUTH, location='headers')

PROTOCOL_NM = EDIT_TEXT

def _get_user_info(request):
    user_id = None
    if request.is_json:
        user_id = request.json.get(EDITOR)
    auth_key = acmn.get_auth_key_from_request(request)
    if not user_id:
        user_id = fetch_id_by_auth_key(auth_key)
    return user_id, auth_key


TEXT_FIELDS = 'Text fields'


@api.route(f'/{FIELDS}')
class TextFields(Resource):
    """
    Get dictionary of all text fields.
    """
    def get(self):
        """
        Get the text fields.
        """
        return {TEXT_FIELDS: tflds.get_flds()}


TEXT_FORM = 'Text add/query/update form'


@api.route(f'/{FORM}')
class TextForm(Resource):
    """
    Get the form for querying text data.
    """
    def get(self):
        """
        Get the form for querying text data.
        """
        return {TEXT_FORM: tform.get_form()}


TEXT_READ = 'Text map'


@api.route(f'/{READ}')
class TextRead(Resource):
    """
    This endpoint serves text data as a dict.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Data not found')
    def get(self):
        """
        Returns text data.
        """
        texts = tqry.fetch_dict()
        return {TEXT_READ: texts}


UPDATE_TEXT_FLDS = api.model('UpdateText', {
    TEXT: fields.String,
    EDITOR: fields.String,
})


@api.route(f'/{UPDATE}/<title>')
@api.expect(parser)
class TextUpdate(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Person not found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(UPDATE_TEXT_FLDS)
    def put(self, title):
        text = request.json.get(TEXT)
        if not text:
            raise wz.NotAcceptable('You must pass text to update.')
        editor, auth_key = _get_user_info(request)
        if not sm.is_permitted(PROTOCOL_NM, sm.UPDATE, user_id=editor,
                               auth_key=auth_key):
            raise wz.Forbidden('Action not permitted.')
        try:
            tqry.update(title, text, editor)
        except ValueError as e:
            raise wz.NotFound(f'{str(e)}')
        return {MESSAGE: 'Text updated.'}


@api.route(f'/{DELETE}/<title>')
@api.expect(parser)
class TextDelete(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Person not found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(api.model('Placeholder', {}))
    def delete(self, title):
        editor, auth_key = _get_user_info(request)
        if not sm.is_permitted(PROTOCOL_NM, sm.DELETE, user_id=editor,
                               auth_key=auth_key):
            raise wz.Forbidden('Action not permitted.')
        try:
            tqry.delete(title)
        except ValueError as e:
            raise wz.NotFound(f'{str(e)}')
        return {MESSAGE: 'Text updated.'}
