"""
Contains functions for dealing with environment variables.
"""

import os

FLAG_OFF = '0'
FLAG_ON = '1'

CICD_VAR = 'CI'


def is_flag_on(var: str) -> bool:
    """
    Determines whether a env flag is "on".
    """
    raw_val = os.getenv(var, '')
    try:
        val = int(raw_val)
    except ValueError:
        val = raw_val
    return bool(val)


def is_cicd_env():
    return is_flag_on(CICD_VAR)
