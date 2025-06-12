import backendcore.common.clients as cl


def test_get_client_code():
    assert cl.get_client_code() is not None


def test_get_client_db():
    assert cl.get_client_db() is not None


def test_get_sales_email():
    assert cl.get_sales_email() is not None
