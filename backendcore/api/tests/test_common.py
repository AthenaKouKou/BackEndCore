
"""
Tests for api_common.py.
"""
import pytest

import backendcore.api.common as acmn


def test_make_md_link():
    assert acmn.make_md_link('text', 'url') == '[text](url)'


def test_get_args_from_str():
    args = acmn.get_args_from_str('arg1=val1&arg2=val2')
    assert args['arg1'] == 'val1'
    assert args['arg2'] == 'val2'


def test_bad_args_from_str():
    with pytest.raises(ValueError):
        acmn.get_args_from_str('arg1&arg2')


def test_list_from_sep_args():
    assert acmn.list_from_sep_args('1,2,3') == ['1', '2', '3']


def test_list_from_sep_args_diff_sep():
    assert acmn.list_from_sep_args('1/2/3', sep='/') == ['1', '2', '3']
