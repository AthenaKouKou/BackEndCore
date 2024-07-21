
"""
Place to see if (generic) inputs are valid.
Things like emails and urls.
NOT things like API records that are DMM specific.
"""

import validators as vld


def is_valid_url(url):
    return vld.url(url)


def is_valid_email(email):
    return vld.email(email)
