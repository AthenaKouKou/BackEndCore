"""
Test module for api_send.py
"""
from unittest.mock import patch

import backendcore.emailer.api_send as asend

TEST_TO = 'gcallah@mac.com'
TEST_SUBJ = 'Test Email'
TEST_CONTENT = 'Some nonsense!'


@patch('backendcore.emailer.api_send.send_mail', autospec=True, return_val='Not none')
def test_send_mail(mock_send_mail):
    ret = asend.send_mail(TEST_TO, TEST_SUBJ, TEST_CONTENT,
                          from_email=asend.DEF_SENDER)
    assert ret is not None
