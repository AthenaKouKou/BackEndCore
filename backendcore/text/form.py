"""
This module provides a sample query form.
"""

import backendcore.data.form_filler as ff

from backendcore.text.fields import (
    TITLE,
    TITLE_DISP_NAME,
    TEXT,
    TEXT_DISP_NAME,
)

FORM_FLDS = [
    {
        ff.FLD_NM: TITLE,
        ff.QSTN: TITLE_DISP_NAME,
        ff.PARAM_TYPE: ff.QUERY_STR,
    },
    {
        ff.FLD_NM: TEXT,
        ff.QSTN: TEXT_DISP_NAME,
        ff.PARAM_TYPE: ff.QUERY_STR,
    },
]


def get_form() -> list:
    return FORM_FLDS


def get_form_descr():
    """
    For Swagger!
    """
    return ff.get_form_descr(FORM_FLDS)


def get_fld_names() -> list:
    return ff.get_fld_names(FORM_FLDS)


def main():
    print(f'Form: {get_form()=}')
    print(f'Form: {get_form_descr()=}')
    print(f'Field names: {get_fld_names()=}')


if __name__ == "__main__":
    main()
