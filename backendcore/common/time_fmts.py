"""
Copyright 2021 API MixMaster LLC. All rights reserved.
Date and time formatting.
"""
import datetime as dt

# for validating string dates:
from dateutil.parser import parse
import numpy as np
import pytz

from backendcore.common.constants import STD_DATE_FORMAT

SECOND = 'S'
MINUTE = 'Min'
HOUR = 'H'
DAY = 'D'
WEEK = 'W'
MONTH = 'M'
BEG_MONTH = 'MS'
END_MONTH = 'M'
QUARTER = 'Q'
YEAR = 'Y'
ANNUAL = 'A'
BEG_YEAR = 'YS'
END_YEAR = 'Y'

# this is awkward but an improvement on using raw constants;
# the string will be like '7D' or '3M'
FREQ_LOC = 0
UNIT_LOC = 1

# VALID_PERIODS is used for testing:
VALID_PERIODS = [DAY, WEEK, MONTH, QUARTER, YEAR]

# an initial cut at providing a variety of date formats:
DAY_MON_YEAR4 = '%d/%m/%Y'
DAY_MON_YEAR2 = '%d/%m/%y'
MON_DAY_YEAR4 = '%m/%d/%Y'
MON_DAY_YEAR2 = '%m/%d/%y'
YEAR4_MON_DAY = '%Y-%m-%d'
YEAR2_MON_DAY = '%y-%m-%d'
YEAR4_MON = '%Y-%m'
YEAR2_MON = '%y-%m'
YEAR4_ONLY = '%Y'
YEAR2_ONLY = '%y'
NP_FULL_DATE_FMT = 'D'
# now pick our default date format:
OUR_DATE_FMT = YEAR4_MON_DAY

TYPE_TO_DATE_FORMAT = {
    DAY: YEAR4_MON_DAY,
    WEEK: YEAR4_MON_DAY,
    MONTH: YEAR4_MON,
    QUARTER: YEAR4_MON,
    YEAR: YEAR4_ONLY,
}

HOURS_PER_DAY = 24
MINS_PER_HOUR = 60
SECONDS_PER_MIN = 60
MINS_PER_DAY = HOURS_PER_DAY * MINS_PER_HOUR
SECONDS_PER_DAY = MINS_PER_DAY + SECONDS_PER_MIN

DAYS_PER_WEEK = 7
MONTHS_PER_QTR = 3
MONTHS_PER_YEAR = 12
QTRS_PER_YEAR = 4
# These next two are good approximations.
DAYS_PER_YEAR = 365.25
WEEKS_PER_YEAR = 52.18

DAYS_PER_MONTH = DAYS_PER_YEAR / MONTHS_PER_YEAR
WEEKS_PER_MONTH = DAYS_PER_MONTH / DAYS_PER_WEEK
WEEKS_PER_QTR = WEEKS_PER_MONTH * MONTHS_PER_QTR
DAYS_PER_QTR = DAYS_PER_MONTH * MONTHS_PER_QTR

PERIOD_DAYS = {
    DAY: 1,
    WEEK: DAYS_PER_WEEK,
    MONTH: DAYS_PER_MONTH,
    QUARTER: DAYS_PER_QTR,
    YEAR: DAYS_PER_YEAR
}

LONGEST_PERIOD = 366  # the longest # days we deal with in a period

MAX_NUM_DAYS = 31

DESIRED_YR_LEN = 4
DESIRED_MON_LEN = 2
DESIRED_DAY_LEN = 2

FUTURE_DATA_YRS = 1  # just a guess! adjust based on data.


DATE_FMT_MAP = {
    YEAR4_MON_DAY: '4 digit year-month number-day number',
    YEAR2_MON_DAY: '2 digit year-month number-day number',
    YEAR4_MON: '4 digit year-month number',
    YEAR2_MON: '2 digit year-month number',
    YEAR4_ONLY: '4 digit year',
    YEAR2_ONLY: '2 digit year',
    DAY_MON_YEAR4: 'day number/month number/4 digit year',
    DAY_MON_YEAR2: 'day number/month number/2 digit year',
    MON_DAY_YEAR4: 'month number/day number/4 digit year',
    MON_DAY_YEAR2: 'month number/day number/2 digit year',
}

# integer values for days of the week:
MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

# timezone stuff:
OUR_TZ_STR = 'est'
OUR_TZ = pytz.timezone('US/Eastern')


TEST_OLD_DATETIME = dt.datetime(2000, 1, 1, 1, 1, 1, 1)


def period_days(unit: str, freq=1) -> float:
    return freq * PERIOD_DAYS[unit]


def is_valid_date(date_str):
    try:
        parse(date_str)
    except ValueError:
        return False
    return True


def is_valid_date_fmt(fmt):
    return fmt in DATE_FMT_MAP


def get_date_fmt_map():
    return DATE_FMT_MAP


def date(year: int, month: int, day: int) -> dt.date:
    return dt.date(year, month, day)


def today() -> dt.date:
    """
    Returns "local" date
    """
    return dt.date.today()


def now() -> dt.datetime:
    """
    Returns current UTC time
    """
    return dt.datetime.now(dt.UTC)


def two_dig_yr_to_4(yr2: str) -> str:
    """
    Decide what 4 digit year should correspond to a 2-digit year.
    xx <= current + N do '20xx'
    xx > current + N do '19xx'
    We judge it slighlty more likely we get 2022
    data in 2021 than 1922 data... can adjust N as
    we find misguesses.
    This code only has a 79-year lifespan!
    """
    last2 = int(yr2)
    cutoff_yr = (today().year + FUTURE_DATA_YRS) % 100
    if last2 > cutoff_yr:
        return '19' + str(last2)
    else:
        # zfill() in case last2 < 10
        return '20' + str(last2).zfill(2)


def period_conv_factor(old_unit: str,
                       old_freq: int,
                       new_unit: str,
                       new_freq: int):
    """
    Factor used to proportionally convert values from one time period to
    another.
    """
    np_days = period_days(new_unit, new_freq)
    op_days = period_days(old_unit, old_freq)
    return np_days / op_days


def portion_through_period(unit: str, curr_date=None):
    """
    Returns the portion curr_date is through the time period.
    For example, if curr_date is halfway through the year, return 0.5.
    We will default to today if there is no curr_date.
    """
    if curr_date is None:
        curr_date = today()
    elif isinstance(curr_date, dt.datetime):
        curr_date = curr_date.date()
    delta = curr_date - beg_period(unit, 1, curr_date=curr_date)
    return delta.days / period_days(unit, 1)


def freq_diff(unit1: str, freq1: int, unit2: str, freq2: int) -> int:
    """
    Returns
    -------
    int
        positive if period 1 is longer than period 2
        negative if period 1 is shorter than period 2
        0 if they are of equal
    """
    return period_days(unit1, freq1) - period_days(unit2, freq2)


def fmt_dt(d: dt.date, fmt: str):
    return d.strftime(fmt)


def get_date_fmt(stype):
    """
    Post-condition: return will be a valid Python format string,
        or None if date_code is not valid.
    """
    return TYPE_TO_DATE_FORMAT.get(stype.get_unit(), None)


def get_today():
    return dt.date.today().strftime(STD_DATE_FORMAT)


def month2qtr(month: int):
    return ((month - 1) // MONTHS_PER_QTR) + 1


def qtr2beg_month(qtr: int):
    return ((qtr - 1) * MONTHS_PER_QTR) + 1


def month2qtr_beg_month(month: int):
    return qtr2beg_month(month2qtr(month))


def beg_period(unit: str, freq: int, curr_date=None) -> dt.date:
    """
    Return the date beginning the period that "date" belongs to.

    For example, If the period is "1M" and today is Feb 27th 2020, we return
    the date for Feb 1st, 2020

    `freq` looks like a useless parameter here!
    """
    if not curr_date:
        curr_date = today()
    if unit == YEAR:
        beg = dt.date(curr_date.year, 1, 1)
    elif unit == QUARTER:
        month = month2qtr_beg_month(curr_date.month)
        beg = dt.date(curr_date.year, month, 1)
    elif unit == MONTH:
        beg = dt.date(curr_date.year, curr_date.month, 1)
    elif (unit == DAY) or (unit == WEEK):
        beg = dt.date(curr_date.year, curr_date.month, curr_date.day)
    else:
        raise ValueError(f'Bad unit for beg_period: {unit=}')
    return beg


DOW_TO_ISO_CODE = {
    'monday': 1,
    'tuesday': 2,
    'wednesday': 3,
    'thursday': 4,
    'friday': 5,
    'saturday': 6,
    'sunday': 7
}


def day_of_week_origin(weekday: str, ref_date: str) -> str:
    """
    Find the next date after the reference date that falls on the specified
    weekday.

    Parameters
    ----------
    weekday: str
      The non-abbreviated name of the weekday (e.g. "Monday", "Tuesday", etc)
      Title, lower, and upper cases are all accepted.
    ref_date: str
      Expected format is YYYY-MM-DD.
    """
    weekday_code = DOW_TO_ISO_CODE[weekday.lower()]
    ref_date = dt.datetime.strptime(ref_date, OUR_DATE_FMT).date()
    while ref_date.isoweekday() != weekday_code:
        ref_date += dt.timedelta(days=1)
    return str(ref_date)


def is_weekly(unit: str, freq: int) -> bool:
    return f'{freq}{unit}' == f'7{DAY}'


def weekday_diff(date1, date2):
    """
    Returns the number of days of the week between two dates.
    """
    return weekday(date1) - weekday(date2)


def weekday(date_str):
    """
    Returns an integer, where Monday = 0 and Sunday = 6.
    """
    date = dt.date.fromisoformat(date_str)
    return date.weekday()


def np_dt_to_str(dt: np.datetime64):
    """
    Casts a numpy datetime to a ISO formated date string: YYYY-MM-DD.
    """
    return str(np.datetime_as_string(dt, NP_FULL_DATE_FMT))


def is_our_date_fmt(date_str: str):
    """
    Tests that the given string matches our default date format.
    """
    try:
        dt.datetime.strptime(date_str, OUR_DATE_FMT)
        return True
    except ValueError:
        return False


def is_valid_num_str_year(year_str: str) -> bool:
    try:
        int_year = int(year_str)
    except ValueError:
        return False
    return is_valid_year(int_year)


def is_valid_year(int_year):
    return isinstance(int_year, int)


def month_name_to_num_str(month_nm: str) -> str:
    try:
        month_num = str(dt.datetime.strptime(month_nm, '%B').month)
    except Exception:
        raise ValueError(f'Bad arg to month_name_to_num_str: {month_nm=}')
    return month_num.zfill(DESIRED_MON_LEN)


def pad_num_str_month(month_str: str) -> str:
    if is_valid_num_str_month(month_str):
        return month_str.zfill(DESIRED_MON_LEN)
    else:
        raise ValueError(f'Bad arg to pad_num_str_month: {month_str=}')


def is_valid_month(month_num: int) -> bool:
    return month_num > 0 and month_num <= MONTHS_PER_YEAR


def is_valid_num_str_month(month_str: str) -> bool:
    try:
        int_month = int(month_str)
    except ValueError:
        return False
    return is_valid_month(int_month)


def int_month_to_num_str(month_num: int) -> str:
    """
    Converts an int month number to a numeric string
    """
    if not is_valid_month(month_num):
        raise ValueError(f'Bad arg to int_month_to_str_num: {month_num=}')
    return str(month_num).zfill(DESIRED_MON_LEN)


def pad_num_str_day(day_num: str) -> str:
    if is_valid_num_str_day(day_num):
        return day_num.zfill(DESIRED_DAY_LEN)
    else:
        raise ValueError(f'Bad arg to pad_num_str_day: {day_num=}')


def is_valid_day(day_num: int) -> bool:
    return day_num > 0 and day_num <= MAX_NUM_DAYS


def is_valid_num_str_day(day_str) -> bool:
    try:
        int_day = int(day_str)
    except ValueError:
        return False
    return is_valid_day(int_day)


def aware_time_to_naive_time(t: dt.datetime):
    if not t.tzinfo:
        tc = t
    else:
        tc = t.astimezone(OUR_TZ)
        tc = tc.replace(tzinfo=None)
    return tc


def tz_convert(t: dt.datetime, tz=pytz.utc):
    '''
    Convert a timestamp to the target timezone.
    If the timestamp is naive, the timezone is set to the target timezone.
    '''
    if not t.tzinfo:
        tc = t.replace(tzinfo=tz)
    else:
        tc = t.astimezone(tz)
    return tc


def iso_time_from_js_time(js_time: str):
    """
    Javascript uses a 'Z' where ISO uses '+00:00'.
    """
    issue_time = js_time.replace('Z', '+00:00')
    return dt.datetime.fromisoformat(issue_time)


def datetime_to_iso(t: dt.datetime) -> str:
    """
    Converts datetime to ISO 8601 str
    """
    return t.isoformat()


def get_current_rfc_datetime_str() -> str:
    """
    Returns the current datetime in an ISO 8601/RFC 3339 compliant string.
    """
    datetime = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    return datetime_to_iso(datetime)


def is_iso_datetime_str(dt_str: str) -> bool:
    try:
        # Did we get a valid datetime object?
        dt.datetime.fromisoformat(dt_str)
    except Exception:
        return False
    return True


def is_rfc_datetime_str(dt_str: str) -> bool:
    """
    Checks if the string passed in is ISO 8601/RFC 3339 compliant.
    """
    # Did we get a valid datetime object? Is there a timezone?
    if not is_iso_datetime_str(dt_str):
        return False
    tz = dt.datetime.fromisoformat(dt_str).tzinfo
    if not tz:
        return False
    return True


def iso_datetime_str_to_date_str(dt_str: str) -> str:
    """
    Takes a datetime string and tries to turn it into just a date.
    """
    datetime = dt.datetime.fromisoformat(dt_str)
    date = str(datetime.date())
    return date


def days_between_date_strings(
    first_date_str: str,
    second_date_str: str,
) -> int:
    """
    Takes two date strings, and returns the number of days between them.
    We do not need to take timezones into account as we are assuming they both
    utilize the same time zone, and the number of days would be the same
    regardless of timezone.
    """
    first_date = dt.datetime.fromisoformat(first_date_str).date()
    second_date = dt.datetime.fromisoformat(second_date_str).date()
    day_difference = (second_date - first_date).days
    return day_difference


def main():
    t = dt.datetime.now()
    print(t.isoformat())
    tc = tz_convert(t, pytz.timezone('est'))
    print(tc.isoformat())
    t = dt.datetime.now(tz=pytz.utc)
    tc = aware_time_to_naive_time(t)
    print(tc)


if __name__ == '__main__':
    main()
