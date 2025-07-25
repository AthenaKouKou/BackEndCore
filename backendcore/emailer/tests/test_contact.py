from unittest.mock import patch

import backendcore.emailer.contact as ct

TEST_EMAIL = 'tester@test.com'
TEST_SUBJECT = 'fake subject'
TEST_MESSAGE = 'fake message'
TEST_PROJECT = 'fake project'


@patch('backendcore.emailer.contact.send_contact_email', autospec=True,
       return_val='Not none')
def test_process_contact_form(mock_email):
    # Empty test, TODO
    ct.process_contact_form(TEST_EMAIL, TEST_SUBJECT, TEST_MESSAGE,
                            TEST_PROJECT)
