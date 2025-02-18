import backendcore.common.common as cmn

def test_get_client_code():
    assert cmn.get_client_code() is not None
