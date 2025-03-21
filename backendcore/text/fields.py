from backendcore.data.form_filler import (
    # DESCR,
    DISP_NAME,
)
import backendcore.data.fields as cflds

EDITOR = 'Editor'
EDITOR_DISP_NAME = EDITOR
LAST_EDIT = 'last_edit'
LAST_EDIT_DISP_NAME = 'Last Edit Date'
TITLE = 'title'
TITLE_DISP_NAME = 'Title'
TEXT = 'text'
TEXT_DISP_NAME = 'Text'

TEST_FLD_NM = TITLE
TEST_FLD_DISP_NM = TITLE_DISP_NAME


FIELDS = {
    TITLE: {
        DISP_NAME: TITLE_DISP_NAME,
    },
    TEXT: {
        DISP_NAME: TEXT_DISP_NAME,
        cflds.MARKDOWN: 1,
    },
    EDITOR: {
        DISP_NAME: EDITOR_DISP_NAME,
    },
    LAST_EDIT: {
        DISP_NAME: LAST_EDIT_DISP_NAME,
    },
}


def get_flds() -> dict:
    return FIELDS


def get_fld_names() -> list:
    return cflds.get_fld_names(FIELDS)


def get_disp_name(fld_nm: str) -> dict:
    return cflds.get_disp_name(FIELDS, fld_nm)


def main():
    print(f'{get_flds()=}')


if __name__ == '__main__':
    main()
