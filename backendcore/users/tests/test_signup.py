"""
Tests user_data/signup.py
"""
import pytest
import os

import backendcore.users.query as uqry

from backendcore.users.signup import signup

LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
NO_LISTS_REASON = os.environ.get('NO_LISTS_REASON')

def test_signup():
    """
    Tests that we can successfully signup a user if valid information is
    given.
    """
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)
    email = 'jkhjkshfjkhsdjf@foo.com'
    try:
        uqry.delete(email)
    except Exception:
        print('User was not in DB')
    signup(
        email=email,
        pw='pw',
        fname='g',
        lname='c'
    )
    assert uqry.fetch_user(email)
    uqry.delete(email)


def test_signup_already_exists():
    """
    Tests that we raise an error if the client tries to signup a user
    who already exists.
    """
    email = 'kahdshgjksdhg@bar.com'
    try:
        uqry.delete(email)
    except Exception:
        print('User was not in DB')

    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        with pytest.raises(ValueError):
            signup(
                email=email,
                pw='someotherpw',
                fname='s',
                lname='c',
            )
        return
    signup(
        email=email,
        pw='someotherpw',
        fname='s',
        lname='c',
    )
    with pytest.raises(ValueError):
        signup(
            email=email,
            pw='someotherpw',
            fname='s',
            lname='c',
        )
    uqry.delete(email)
