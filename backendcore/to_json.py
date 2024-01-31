
"""
Converts an arbitrary object from our system to json.
Requirement: Any component that cannot natively be jsonified
             must have a `to_json()` method!
Optional: If the object has an data member named by the
          constant here called `OTHER_FLDS`, then we will
          "lift" those fields up to the top JSON level.
          Also, certain fields can be excluded from the "JSONing"
"""
import json


VALID_JSON_TYPES = [int, str, float, list, dict, bool]

OTHER_FLDS = 'flds'  # for fields the class may not know about
OTHER_FLD_NM = 'foo'


def is_native_json(fld):
    return fld is None or type(fld) in VALID_JSON_TYPES


def to_json(some_obj, excludes=[]):
    """
    A standard way to "JSONify" any object in our system.
    It allows for excluded fields, fields that need `to_json()`
    called on them, and a catch-all OTHER_FLDS that need to be
    lifted up to the top level.
    (OTHER_FLDS should be in a dict with that name.)
    """
    flds = some_obj.__dict__
    jret = {}
    for fld_nm in flds:
        if fld_nm in excludes:
            continue
        elif fld_nm == OTHER_FLDS:
            for inner_fld_nm in flds[OTHER_FLDS]:
                if inner_fld_nm in excludes:
                    continue
                inner_fld = flds[OTHER_FLDS][inner_fld_nm]
                if is_native_json(inner_fld):
                    jret[inner_fld_nm] = inner_fld
                else:
                    jret[inner_fld_nm] = inner_fld.to_json()
        elif is_native_json(flds[fld_nm]):
            jret[fld_nm] = flds[fld_nm]
        else:
            jret[fld_nm] = flds[fld_nm].to_json()
    return jret


class InnerObj():
    def __init__(self):
        self.name = 'Hello'
        self.num = 1

    def to_json(self):
        return to_json(self)


class TestObj():
    def __init__(self):
        self.name = 'Hello'
        self.num = 1
        self.truth = False
        self.rational = 3.14
        self.lstuff = [1, 2, 3, 4, 5]
        self.dstuff = {'a': 1, 'b': 2, 'c': 3}
        self.inner_obj = InnerObj()
        self.flds = {OTHER_FLD_NM: 'bar'}


def main():
    print(json.dumps(to_json(TestObj()), indent=4))


if __name__ == "__main__":
    main()
