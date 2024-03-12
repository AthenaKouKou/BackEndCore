from copy import deepcopy

from backendcore.data.form_filler import (
    CHOICES,
    DESCR,
    DISP_NAME,
    HI_VAL,
    LOW_VAL,
)

BAR = 'bar'
CHECKBOX = 'checkbox'
CLICK = 'click'
DSRC_LINK = 'datasources'
FLD_TYPE = 'type'
FLOAT = 'float'
DEC_PLACES = 'decimalPlaces'
GRAPH = 'graph'
HIDDEN = 'hidden'
HOVER = 'hover'
INT = 'int'
IS_KEY_FLD = 'isKeyField'
LINE = 'line'
LINK = 'link'
LINK_TYPE = 'link-type'
LINK_ACTIVATE = 'link-activate'
MAP = 'map'
MARKDOWN = 'markdown'  # field contains markdown
ORIGIN = '$ORIGIN'
# sometimes we don't want sorting on a field; set this to True:
NO_SORT = 'noSort'
STR = 'string'
VAL = '$VAL'

# Common field names:
MORE_INFO = 'more_info'
MORE_INFO_DISP_NM = 'More info'

"""
A sample of what the data for these functions should look like,
also used for testing:
"""
LTV = 'ltv'
YEAR = 'year'
LTV_DISP_NAME = 'Loan-to-Value Ratio'
LTV_0_DESCR = 'Under 65%'

TEST_FIELDS = {
    YEAR: {
        DISP_NAME: 'Year',
        DESCR: 'The calendar year the data submission covers',
        CHOICES: {
            2018: {DESCR: '2018', },
            2019: {DESCR: '2019', },
            2020: {DESCR: '2020', },
            2021: {DESCR: '2021', },
        },
    },
    LTV: {
        DISP_NAME: LTV_DISP_NAME,
        DESCR: 'The ratio of the total amount of debt secured by the '
               + 'property to the value of the property relied on in '
               + 'making the credit decision.',
        CHOICES: {
            0: {
                DESCR: LTV_0_DESCR,
                LOW_VAL: 0,
                HI_VAL: 64.99,
            },
            65: {
                DESCR: '65% to 70%',
                LOW_VAL: 65,
                HI_VAL: 69.99,
            },
            70: {
                DESCR: '70% to 75%',
                LOW_VAL: 70,
                HI_VAL: 74.99,
            },
            75: {
                DESCR: '75% to 80%',
                LOW_VAL: 75,
                HI_VAL: 79.99,
            },
            80: {
                DESCR: '80% to 85%',
                LOW_VAL: 80,
                HI_VAL: 84.99,
            },
            85: {
                DESCR: '85% to 90%',
                LOW_VAL: 85,
                HI_VAL: 89.99,
            },
            90: {
                DESCR: '90% to 95%',
                LOW_VAL: 90,
                HI_VAL: 94.99,
            },
            95: {
                DESCR: '95% to 100%',
                LOW_VAL: 95,
                HI_VAL: 99.99,
            },
            100: {
                DESCR: 'Over 100%',
                LOW_VAL: 100,
                HI_VAL: 100_000_000,  # just some big number!
            },
        },
    },
}


def get_fld_names(flds: dict) -> list:
    return list(flds.keys())


def get_disp_name(flds: dict, fld_nm: str):
    ret = ''
    fld = flds.get(fld_nm, None)
    if fld:
        ret = fld.get(DISP_NAME, fld_nm)
    return ret


def get_full_choices_dict(flds: dict, fld_nm: str) -> dict:
    if fld_nm in flds:
        return flds[fld_nm].get(CHOICES, {})
    else:
        return None


def get_choices(flds: dict, fld_nm: str) -> dict:
    """
    For dropdowns for choices.
    """
    choices = {}
    if fld_nm in flds:
        # we do a deepcopy so we don't change values in flds!
        choices = deepcopy(get_full_choices_dict(flds, fld_nm))
        for key in choices:
            choices[key] = choices[key][DESCR]
    return choices


def get_choice(flds: dict, fld_nm: str, choice):
    return flds[fld_nm][CHOICES].get(choice, None)


def get_choice_descr(flds: dict, fld_nm: str, choice):
    choice_dict = get_choice(flds, fld_nm, choice)
    return choice_dict.get(DESCR, choice)


def is_valid_choice(flds: dict, fld_nm: str, choice) -> bool:
    return choice in get_choices(flds, fld_nm)


def is_range_fld(flds: dict, fld_nm):
    """
    If ANY value is a range, all must be.
    """
    choices = get_full_choices_dict(flds, fld_nm)
    if choices:
        for choice in choices:
            # we could just as well check for HI_VAL!
            if LOW_VAL in choices[choice]:
                return True
    return False


def get_low_val(flds: dict, fld_nm: str, choice):
    if is_range_fld(flds, fld_nm):
        choice = int(choice)
        return get_choice(flds, fld_nm, choice)[LOW_VAL]
    else:
        return None


def get_high_val(flds: dict, fld_nm: str, choice):
    if is_range_fld(flds, fld_nm):
        choice = int(choice)
        return get_choice(flds, fld_nm, choice)[HI_VAL]
    else:
        return None


def get_range_choice(flds: dict, fld_nm: str, choice):
    if is_range_fld(flds, fld_nm):
        ranges = list(get_choices(flds, fld_nm).keys())
        for curr_range in ranges:
            if isinstance(choice, str):
                return None
            if (
                choice >= get_low_val(flds, fld_nm, curr_range)
                and
                choice <= get_high_val(flds, fld_nm, curr_range)
            ):
                return curr_range
    return None
