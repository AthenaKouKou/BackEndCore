import backendcore.emailer.contact_form as cf


def test_get_form():
    assert isinstance(cf.get_form(), list)
