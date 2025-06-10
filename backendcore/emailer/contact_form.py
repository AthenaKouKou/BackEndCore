import backendcore.data.form_filler as ff
from backendcore.common.constants import EMAIL

SUBJECT = 'subject'
MESSAGE = 'message'
PROJECT = 'project'


CONTACT_FORM_FLDS = [
    {
        ff.FLD_NM: EMAIL,
        ff.QSTN: 'Your email:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,
    },
    {
        ff.FLD_NM: SUBJECT,
        ff.QSTN: 'Subject:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,
    },
    {
        ff.FLD_NM: MESSAGE,
        ff.QSTN: 'Message:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,
    },
    {
        ff.FLD_NM: PROJECT,
        ff.QSTN: 'Describe the project you\'re working on:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: True,
    },
]


def get_form() -> dict:
    return CONTACT_FORM_FLDS
