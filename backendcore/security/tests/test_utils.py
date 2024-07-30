from datetime import datetime

from unittest.mock import patch

import backendcore.security.utils as utl


def test_gen_salt():
    assert isinstance(utl.gen_salt(), str)


def test_now():
    assert isinstance(utl.now(), datetime)


@patch('backendcore.data.db_connect.extract_date',
       return_value='2001-01-01', autospec=True)
def test_naive_dt_from_db(mock_extract_date):
    """
    This test should be improved to check the right 'sort' of
    date comes out the other end.
    """
    assert utl.naive_dt_from_db('fake key', 'fake user')
