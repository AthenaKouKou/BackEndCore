
"""
Tests our convert to JSON package.
"""

import json

import common.to_json as tjs


def test_to_json():
    """
    This will blow up if not valid JSON.
    """
    jret = json.dumps(tjs.to_json(tjs.TestObj()), indent=4)
    assert isinstance(jret, str)


def test_excludes():
    ret = tjs.to_json(tjs.TestObj(), excludes=['rational'])
    assert 'rational' not in ret


def test_other_flds():
    ret = tjs.to_json(tjs.TestObj())
    assert tjs.OTHER_FLD_NM in ret
