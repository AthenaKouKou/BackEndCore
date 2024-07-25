"""
Copyright 2021 API MixMaster LLC. All rights reserved.

Test module for time_fmts.py.
"""
import unittest.mock as mock
import datetime as dt
from random import choice

import pytest

import backendcore.common.time_fmts as tfmt

TEST_RUNS = 20
BIG_ENOUGH = 2

RAND_CHARS = ['a', 'v', '4', 'y', 'D', '#', '!', '0', 'W', 'A', 'm', '@', '3']
ABS_ERROR_TOL = 1

# These weekday values were looked up in an online day calculator.
SOME_KNOWN_WEEKDAYS = {
    '1959-04-21': tfmt.TUESDAY,
    '1967-09-25': tfmt.MONDAY,
    '1997-01-20': tfmt.MONDAY,
    '1999-03-03': tfmt.WEDNESDAY,
    '2000-05-24': tfmt.WEDNESDAY,
}


# we're going to sanity check our calculations for some constants:
def test_days_per_month():
    assert tfmt.DAYS_PER_MONTH > 28
    assert tfmt.DAYS_PER_MONTH < 32


def test_weeks_per_month():
    assert tfmt.WEEKS_PER_MONTH > 4
    assert tfmt.WEEKS_PER_MONTH < 5


def test_days_per_qtr():
    assert tfmt.DAYS_PER_QTR > tfmt.DAYS_PER_MONTH * 2
    assert tfmt.DAYS_PER_QTR < tfmt.DAYS_PER_MONTH * 4


def test_weekday():
    for date in SOME_KNOWN_WEEKDAYS:
        assert tfmt.weekday(date) == SOME_KNOWN_WEEKDAYS[date]


def test_weekday_diff():
    """
    See SOME_KNOWN_WEEKDAYS above to understand the outcomes below.
    """
    assert tfmt.weekday_diff('1959-04-21', '1967-09-25') == 1
    assert tfmt.weekday_diff('1967-09-25', '1959-04-21') == -1
    assert tfmt.weekday_diff('1999-03-03', '1967-09-25') == 2
    assert tfmt.weekday_diff('1967-09-25', '1999-03-03') == -2


def test_period_days():
    assert tfmt.period_days(tfmt.DAY) == 1
    assert tfmt.period_days(tfmt.WEEK) == 7
    assert tfmt.period_days(tfmt.MONTH) == pytest.approx(30, .1)
    assert tfmt.period_days(tfmt.QUARTER) == pytest.approx(30 * 3, .1)
    assert tfmt.period_days(tfmt.YEAR) == pytest.approx(365, .3)


def test_is_valid_date1():
    assert tfmt.is_valid_date('01/01/2001')


def test_is_valid_date2():
    assert tfmt.is_valid_date('January 1, 2001')


def test_is_valid_date3():
    assert tfmt.is_valid_date('Jan. 1, 2001')


def test_is_not_valid_date1():
    assert not tfmt.is_valid_date('Floob. 1, 2001')


def test_is_not_valid_date2():
    assert not tfmt.is_valid_date('43/45/2001')


def test_is_not_valid_date3():
    assert not tfmt.is_valid_date('January 35, 2001')


def test_is_valid_date_fmt():
    assert tfmt.is_valid_date_fmt(tfmt.YEAR4_MON_DAY)


def test_is_not_valid_date_fmt():
    assert not tfmt.is_valid_date_fmt('nonsense date format')


def test_get_date_fmt_map():
    assert isinstance(tfmt.get_date_fmt_map(), dict)


def test_two_dig_yr_to_4():
    """
    Should take '99' -> '1999' and '02' -> 2002, etc.
    xx <= current + 1 do '20xx'
    xx > current + 1 do '19xx'
    As written, these tests will fail about 80 years from now!
    """
    assert tfmt.two_dig_yr_to_4('99') == '1999'  # tonight we're gonna party like it's...
    assert tfmt.two_dig_yr_to_4('01') == '2001'


def test_month2qtr():
    """
    Check that we can get right qtr for each month.
    No sense writing separate tests for all 12 months!
    """
    assert tfmt.month2qtr(1) == 1
    assert tfmt.month2qtr(2) == 1
    assert tfmt.month2qtr(3) == 1
    assert tfmt.month2qtr(4) == 2
    assert tfmt.month2qtr(5) == 2
    assert tfmt.month2qtr(6) == 2
    assert tfmt.month2qtr(7) == 3
    assert tfmt.month2qtr(8) == 3
    assert tfmt.month2qtr(9) == 3
    assert tfmt.month2qtr(10) == 4
    assert tfmt.month2qtr(11) == 4
    assert tfmt.month2qtr(12) == 4


def test_qtr2beg_month():
    """
    Check that we can get right beginning for each qtr.
    No sense writing separate tests for all 4 qtrs!
    """
    assert tfmt.qtr2beg_month(1) == 1
    assert tfmt.qtr2beg_month(2) == 4
    assert tfmt.qtr2beg_month(3) == 7
    assert tfmt.qtr2beg_month(4) == 10


def test_month2qtr_beg_month():
    assert tfmt.month2qtr_beg_month(1) == 1
    assert tfmt.month2qtr_beg_month(2) == 1
    assert tfmt.month2qtr_beg_month(3) == 1
    assert tfmt.month2qtr_beg_month(4) == 4
    assert tfmt.month2qtr_beg_month(5) == 4
    assert tfmt.month2qtr_beg_month(6) == 4
    assert tfmt.month2qtr_beg_month(7) == 7
    assert tfmt.month2qtr_beg_month(8) == 7
    assert tfmt.month2qtr_beg_month(9) == 7
    assert tfmt.month2qtr_beg_month(10) == 10
    assert tfmt.month2qtr_beg_month(11) == 10
    assert tfmt.month2qtr_beg_month(12) == 10


def test_beg_current_period_year():
    """
    Test that we can get the beginning of the current year.
    """
    today = dt.date.today()
    assert tfmt.beg_period('Y', 1) == dt.date(today.year, 1, 1)


def test_beg_current_period_month():
    """
    Test that we can get the beginning of the current month.
    """
    today = dt.date.today()
    assert tfmt.beg_period('M', 1) == dt.date(today.year, today.month, 1)


def test_beg_other_period_qtr():
    """
    Test that we can get the beginning of an arbitrary quarter.
    """
    td = dt.date(1917, 2, 15)
    assert tfmt.beg_period('Q', 1, curr_date=td) == dt.date(td.year, 1, 1)


def test_period_conv_factor_y2d():
    """
    Test the period conversion factor for years to days.
    """
    y2d = tfmt.period_conv_factor(tfmt.YEAR, 1, tfmt.DAY, 1)
    assert y2d == pytest.approx(1 / tfmt.DAYS_PER_YEAR)


def test_period_conv_factor_d2y():
    """
    Test the period conversion factor for days to years.
    """
    d2y = tfmt.period_conv_factor(tfmt.DAY, 1, tfmt.YEAR, 1)
    assert d2y == pytest.approx(tfmt.DAYS_PER_YEAR)


def test_period_conv_factor_y2m():
    """
    Test the period conversion factor for years to months.
    """
    y2m = tfmt.period_conv_factor(tfmt.YEAR, 1, tfmt.MONTH, 1)
    assert y2m == pytest.approx(1 / tfmt.MONTHS_PER_YEAR)


def test_period_conv_factor_m2y():
    """
    Test the period conversion factor for months to years.
    """
    m2y = tfmt.period_conv_factor(tfmt.MONTH, 1, tfmt.YEAR, 1)
    assert m2y == tfmt.MONTHS_PER_YEAR


def test_period_conv_factor_y2q():
    """
    Test the period conversion factor for years to quarters.
    """
    y2q = tfmt.period_conv_factor(tfmt.YEAR, 1, tfmt.QUARTER, 1)
    assert y2q == pytest.approx(1 / tfmt.QTRS_PER_YEAR)


def test_period_conv_factor_q2y():
    """
    Test the period conversion factor for quarters to years.
    """
    q2y = tfmt.period_conv_factor(tfmt.QUARTER, 1, tfmt.YEAR, 1)
    assert q2y == tfmt.QTRS_PER_YEAR


def test_period_conv_factor_q2d():
    """
    Test the period conversion factor for quarters to days.
    """
    q2d = tfmt.period_conv_factor(tfmt.QUARTER, 1, tfmt.DAY, 1)
    assert q2d == pytest.approx(1 / tfmt.DAYS_PER_QTR)


def test_period_conv_factor_d2q():
    """
    Test the period conversion factor for days to quarters.
    """
    d2q = tfmt.period_conv_factor(tfmt.DAY, 1, tfmt.QUARTER, 1)
    assert d2q == tfmt.DAYS_PER_QTR


def test_period_conv_factor_y2w():
    """
    Test the period conversion factor for quarters to days.
    """
    y2w = tfmt.period_conv_factor(tfmt.YEAR, 1, tfmt.WEEK, 1)
    assert y2w == pytest.approx(1 / tfmt.WEEKS_PER_YEAR, .1)


def test_period_conv_factor_w2y():
    """
    Test the period conversion factor for days to quarters.
    """
    w2y = tfmt.period_conv_factor(tfmt.WEEK, 1, tfmt.YEAR, 1)
    assert w2y == pytest.approx(tfmt.WEEKS_PER_YEAR, .1)


def test_portion_through_period():
    today = dt.date.today()
    halfway = dt.date(today.year, 6, 1)
    assert 6/12 == pytest.approx(tfmt.portion_through_period('Y', halfway),
                                 ABS_ERROR_TOL)
    thirdway = dt.date(today.year, today.month, 10)
    assert 10/30 == pytest.approx(tfmt.portion_through_period('M', thirdway),
                                  ABS_ERROR_TOL)


def test_freq_diff_pos():
    """
    Longer per 1 than 2 should return > 0.
    """
    assert tfmt.freq_diff(tfmt.MONTH, 1, tfmt.DAY, 1) > 0
    assert tfmt.freq_diff(tfmt.QUARTER, 1, tfmt.WEEK, 1) > 0


def test_freq_diff_neg():
    """
    Shorter per 1 than 2 should return < 0.
    """
    assert tfmt.freq_diff(tfmt.WEEK, 1, tfmt.YEAR, 1) < 0
    assert tfmt.freq_diff(tfmt.MONTH, 1, tfmt.QUARTER, 1) < 0


def test_freq_diff_eq():
    """
    Equal per 1 to 2 should return 0.
    """
    assert tfmt.freq_diff(tfmt.WEEK, 1, tfmt.DAY, 7) == 0
    assert tfmt.freq_diff(tfmt.MONTH, 3, tfmt.QUARTER, 1) == 0


def test_day_of_week_origin():
    date = tfmt.day_of_week_origin(weekday='Monday', ref_date='2021-08-04')
    assert date == '2021-08-09'


def test_is_our_date_fmt():
    """
    Test that we can determine if a string is an ISO-formatted date.
    """
    # test good date
    assert tfmt.is_our_date_fmt('1992-01-01')
    # test not at all date
    assert not tfmt.is_our_date_fmt('hello')
    # test input a 13th month
    assert not tfmt.is_our_date_fmt('1992-13-01')
    # test input a 32nd day
    assert not tfmt.is_our_date_fmt('1992-01-32')


def test_month_name_to_num_str():
    """
    The month names and numbers should be pretty stable, so
    I feel safe hard-coding them here!
    We can pretty much assume if Jan and Dec work, the rest will
    also, pending future trouble.
    """
    month_num = tfmt.month_name_to_num_str('January')
    assert month_num == '01'
    month_num = tfmt.month_name_to_num_str('December')
    assert month_num == '12'


def test_month_name_to_num_bad_month():
    with pytest.raises(ValueError):
        tfmt.month_name_to_num_str("This ain't a month name in any language!")


def test_is_valid_year():
    assert tfmt.is_valid_year(2000)
    assert tfmt.is_valid_year(1880)
    assert not tfmt.is_valid_year('Not  a year')


def test_is_valid_num_str_year():
    assert tfmt.is_valid_num_str_year('2000')
    assert not tfmt.is_valid_num_str_year('Not a year')


def test_is_valid_month():
    assert tfmt.is_valid_month(1)
    assert tfmt.is_valid_month(12)


def test_is_not_valid_month():
    assert not tfmt.is_valid_month(0)
    assert not tfmt.is_valid_month(13)


def test_int_month_to_num_str():
    month_num = tfmt.int_month_to_num_str(1)
    assert month_num == '01'
    month_num = tfmt.int_month_to_num_str(9)
    assert month_num == '09'


def test_month_num_to_num_bad_input():
    with pytest.raises(ValueError):
        tfmt.int_month_to_num_str(474)


def test_pad_num_str_month():
    assert tfmt.pad_num_str_month('1') == '01'
    assert tfmt.pad_num_str_month('12') == '12'


def test_pad_num_str_month_bad_input():
    with pytest.raises(ValueError):
        tfmt.pad_num_str_month('13')


def test_pad_num_str_day():
    assert tfmt.pad_num_str_day('1') == '01'
    assert tfmt.pad_num_str_day('31') == '31'


def test_pad_num_str_day_bad_input():
    with pytest.raises(ValueError):
        assert tfmt.pad_num_str_day("I'm not even a num str.")
    with pytest.raises(ValueError):
        assert tfmt.pad_num_str_day("32")


def test_aware_time_to_naive_time():
    t = dt.datetime(2023, 6, 6)
    tc = tfmt.aware_time_to_naive_time(t)
    assert str(tc).startswith('2023-06-06')


def test_iso_time_from_js_time():
    js_time = '2023-06-06T17:09:01.598Z'
    iso_time = tfmt.iso_time_from_js_time(js_time)
    assert isinstance(iso_time, dt.datetime)
    assert 'Z' not in str(iso_time)

def test_datetime_to_iso():
   test_datetime = tfmt.TEST_OLD_DATETIME
   iso = tfmt.datetime_to_iso(test_datetime)
   assert iso == '2000-01-01T01:01:01.000001'
