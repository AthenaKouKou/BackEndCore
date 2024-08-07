
"""
A utility for filling in a form in a notebook or
from the command line.
"""
from backendcore.common.constants import (  # noqa F401
    PASSWORD,
)

from backendcore.data.fields import (  # noqa 401
    CHOICES,
    DESCR,
    DISP_NAME,
    FLD_TYPE,
    HI_VAL,
    INT,
    LIST,
    LOW_VAL,
)

BOOL = 'bool'
DEFAULT = 'default'
DISABLED = 'disabled'
FLD_NM = 'fld_nm'
INPUT_TYPE = 'input_type'
INSTRUCTIONS = 'instructions'
MARKDOWN = 'markdown'
MULTI = 'multiple'  # choice field that allows > 1 choice
OPT = 'optional'
PARAM_TYPE = 'param_type'
QSTN = 'question'
RANGE = 'range'  # designates a field that selects a range of values
RECOMMENDED_PAGE = 'recommended_page'
REQ_LEN = 'req_len'
SUBFIELDS = 'subfields'
TYPECAST = 'typecast'
URL = 'url'
# two parameter types:
PATH = 'path'
QUERY_STR = 'query_string'
# some input types:
DATE = 'date'
FILE_LOADER = 'file_loader'
NUMERIC = 'numeric'  # a string, but only numbers allowed
# for strings, we might want non-default input box sizes:
FLD_LEN = 'fld_len'
PARAMS = 'params'
# sometimes we don't want 'None' as the default in a pick list:
ALL = 'All'
NONE = 'None'
# when submitting files, we can set valid file types
FILE_TYPES = 'fileTypes'
DOCX = '.docx'
MD = '.md'
HTML = '.html'
TXT = '.txt'

# Display settings
HELPER = 'helperText'
MID_VAL = 'mid_val'
DISP_ON = 'display_on'
FULL_WIDTH = 'full_width'

TEST_FLD = 'test field'

TEST_FLD_DESCRIPS = [
    {
        FLD_NM: TEST_FLD,
        DEFAULT: 'test default',
        PARAM_TYPE: QUERY_STR,
        QSTN: 'Why do we never get an answer?',
    }
]


BOOL_CHOICES = {
    True: 'Yes',
    False: 'No',
}


def get_form_descr(fld_descrips: list) -> dict:
    descr = {}
    for fld in fld_descrips:
        if fld.get(PARAM_TYPE, '') == QUERY_STR:
            fld_nm = fld[FLD_NM]
            descr[fld_nm] = fld[QSTN]
            if CHOICES in fld:
                descr[fld_nm] += f'\nChoices: {fld[CHOICES]}'
    return descr


def get_fld_names(fld_descrips: list) -> list:
    fld_nms = []
    for fld in fld_descrips:
        fld_nms.append(fld[FLD_NM])  # every field MUST have a name!
    return fld_nms


def get_query_fld_names(fld_descrips: list) -> list:
    fld_nms = []
    for fld in fld_descrips:
        if fld[PARAM_TYPE] == QUERY_STR:
            fld_nms.append(fld[FLD_NM])  # every field MUST have a name!
    return fld_nms


def get_input(dflt, opt, qstn):
    """
    So we can mock patch this.
    """
    return input(f'{dflt}{opt}{qstn} ')


def form(fld_descrips):
    print('For optional fields just hit Enter if you do not want a value.')
    print('For fields with a default just hit Enter if you want the default.')
    fld_vals = {}
    for fld in fld_descrips:
        opt = ''
        dflt = ''
        if CHOICES in fld:
            print(f'Options: {fld[CHOICES]}')
        if OPT in fld:
            opt = '(OPTIONAL) '
        if DEFAULT in fld:
            dflt = f'(DEFAULT: {fld["default"]}) '
        # no question means don't ask the user:
        if QSTN in fld:
            fld_vals[fld[FLD_NM]] = get_input(dflt, opt, fld[QSTN])
            if TYPECAST in fld:
                if fld[TYPECAST] == INT:
                    fld_vals[fld[FLD_NM]] = int(fld_vals[fld[FLD_NM]])
        else:
            fld_vals[fld[FLD_NM]] = ''
        # See if we should fill in default val:
        if DEFAULT in fld and not fld_vals[fld[FLD_NM]]:
            fld_vals[fld[FLD_NM]] = fld["default"]
    return fld_vals


def main():
    result = form(TEST_FLD_DESCRIPS)
    print(result)


if __name__ == "__main__":
    main()
