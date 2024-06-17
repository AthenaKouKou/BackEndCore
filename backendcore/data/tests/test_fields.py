from copy import deepcopy

import backendcore.data.fields as flds
from backendcore.data.fields import (
    LTV,
    LTV_0_DESCR,
    LTV_DISP_NAME,
    TEST_FIELDS,
    YEAR,
)

RANGE_EXAMPLE = LTV
NOT_RANGE_EXAMPLE = YEAR


def test_get_choice_descr():
    assert flds.get_choice_descr(TEST_FIELDS, RANGE_EXAMPLE, 0) == LTV_0_DESCR


def test_get_disp_name():
    assert flds.get_disp_name(TEST_FIELDS, LTV) == LTV_DISP_NAME


def test_get_disp_name_no_such_fld():
    assert not flds.get_disp_name(TEST_FIELDS, 'This is not a field name!')


def test_get_choice():
    assert isinstance(flds.get_choice(TEST_FIELDS, YEAR, 2018), dict)


def test_get_range_choice():
    assert isinstance(flds.get_range_choice(TEST_FIELDS, RANGE_EXAMPLE, 40), int)


def test_is_range_fld():
    assert flds.is_range_fld(TEST_FIELDS, RANGE_EXAMPLE)


def test_is_not_range_fld():
    assert not flds.is_range_fld(TEST_FIELDS, NOT_RANGE_EXAMPLE)


def test_get_low_val():
    for choice in flds.get_full_choices_dict(TEST_FIELDS, RANGE_EXAMPLE):
        assert isinstance(flds.get_low_val(TEST_FIELDS, RANGE_EXAMPLE, choice),
                          (int, float))


def test_get_low_val_not_range():
    for key in flds.get_choices(TEST_FIELDS, NOT_RANGE_EXAMPLE):
        assert flds.get_low_val(TEST_FIELDS, NOT_RANGE_EXAMPLE, key) is None


def test_get_high_val():
    for key in flds.get_choices(TEST_FIELDS, RANGE_EXAMPLE):
        assert isinstance(flds.get_high_val(TEST_FIELDS, RANGE_EXAMPLE, key), (int, float))


def test_get_high_val_not_range():
    for key in flds.get_choices(TEST_FIELDS, NOT_RANGE_EXAMPLE):
        assert flds.get_high_val(TEST_FIELDS, NOT_RANGE_EXAMPLE, key) is None


def test_is_valid_choice():
    for fld in TEST_FIELDS:
        for choice in flds.get_choices(TEST_FIELDS, fld):
            assert flds.is_valid_choice(TEST_FIELDS, fld, choice)


def test_is_not_valid_choice():
    assert not flds.is_valid_choice(TEST_FIELDS, RANGE_EXAMPLE, 'Not a valid choice!')


def test_get_choices():
    assert isinstance(flds.get_choices(TEST_FIELDS, RANGE_EXAMPLE), dict)


def test_rm_extra_flds():
    wanted_flds = deepcopy(TEST_FIELDS)
    existing_flds = deepcopy(TEST_FIELDS)
    del wanted_flds[flds.LTV]
    new_flds = flds.rm_extra_flds(wanted_flds, existing_flds)
    assert flds.LTV not in new_flds
    assert flds.YEAR in new_flds
