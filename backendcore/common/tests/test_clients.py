from unittest.mock import patch
import pytest

import backendcore.common.clients as cl
import backendcore.common.valid as vld

BAD_CODE = 'Surely not a good client code'


def test_get_client_code():
    assert cl.get_client_code() in cl.VALID_CODES


def test_get_client_db():
    for code in cl.CODES_W_DB:
        cl.client_code = code
        assert cl.get_client_db() in cl.VALID_DBS


def test_get_client_no_db():
    cl.client_code = cl.CLIENT_HAS_NO_DB
    assert cl.get_client_db() is None


def test_get_client_db_bad_code():
    cl.client_code = BAD_CODE
    with pytest.raises(ValueError):
        cl.get_client_db()


def test_get_sales_email():
    cl.client_code = cl.CLIENT_HAS_EMAIL
    assert vld.is_valid_email(cl.get_sales_email())


def test_get_no_sales_email():
    cl.client_code = cl.CLIENT_HAS_NO_EMAIL
    cl.get_sales_email() is None


def test_get_sales_email_bad_code():
    cl.client_code = BAD_CODE
    with pytest.raises(ValueError):
        cl.get_sales_email()
