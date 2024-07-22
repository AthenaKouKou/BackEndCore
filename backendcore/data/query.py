"""
Some common functions dealing with our data caches.
The actual caches appear in the modules dealing with the relevant data entity.
"""
import re
from copy import deepcopy

import backendcore.data.db_connect as dbc

from backendcore.common.constants import (
    CODE,
    NAME,
)


def fetch_list(db_nm: str, collect_nm: str, sort_fld=NAME):
    """
    Fetch all of some docs: returns a list.
    """
    db_nm = dbc.setup_connection(db_nm)
    return dbc.fetch_all(db_nm, collect_nm, no_id=True,
                         sort=dbc.ASC, sort_fld=sort_fld)


def list_to_dict(key, recs: list, del_key=False) -> dict:
    """
    Sometimes it is more convenient to have a dictionary
    than a list!
    """
    new_dict = {}
    new_recs = []
    if del_key:
        new_recs = deepcopy(recs)
    else:
        new_recs = recs
    for rec in new_recs:
        new_dict[rec[key]] = rec
        if del_key:
            del new_dict[rec[key]][key]
    return new_dict


def make_combined_key(record, primary_key, secondary_key) -> tuple:
    return (record[primary_key], record[secondary_key])


def make_combined_key_str(record, primary_key, secondary_key) -> str:
    return str(record[primary_key]) + str(record[secondary_key])


def list_to_dict_multi_key(primary_key, secondary_key, recs: list,
                           stringify=False) -> dict:
    """
    Similar to list_to_dict, but creates the dictionary key using two key
    values instead of one. If stringify is set to True, the keys are no longer
    tuples of the key values, but rather a string of the values.
    """
    new_dict = {}
    for rec in recs:
        if stringify:
            new_dict[make_combined_key_str(rec, primary_key,
                                           secondary_key)] = rec
        else:
            new_dict[make_combined_key(rec, primary_key, secondary_key)] = rec
    return new_dict


def add(db_nm: str, collect_nm: str, rec: dict):
    db_nm = dbc.setup_connection(db_nm)
    return dbc.insert_doc(db_nm, collect_nm, rec)


def delete_by_code(db_nm: str, collect_nm: str, code: str, code_nm=CODE):
    db_nm = dbc.setup_connection(db_nm)
    return dbc.del_one(db_nm, collect_nm, {code_nm: code})


def regex_search(fld_nm: str, val: str, data: dict):
    """
    We can add consider case later, if we need to.
    """
    matches = {}
    for key, rec in data.items():
        if re.search(val, rec.get(fld_nm, ''), re.IGNORECASE):
            matches[key] = rec
    return matches


def regex_intersect_search(fld_dict, data):
    """
    fld_dict is a dictionary where the keys are the fields being searched, and
    the values are the search valus
    Runs multiple regex searched on several fields, and only returns items that
    match all searches
    """
    matches = {}
    for key, rec in data.items():
        match_flag = True
        for fld_nm, srch in fld_dict.items():
            if not srch:
                srch = ""
            if not re.search(srch, rec.get(fld_nm, ''), re.IGNORECASE):
                match_flag = False
        if match_flag is True:
            matches[key] = rec
    return matches


def fetch_by_fld_val(fld_nm: str,
                     val: str,
                     data_set: dict,
                     test_membership=False) -> dict:
    """
    test_membership is for when we have a list of values.
    """
    recs_by_fld = {}
    for key in data_set:
        rec = data_set[key]
        if test_membership:
            if val in rec.get(fld_nm, []):
                recs_by_fld[key] = rec
        else:
            if val == rec.get(fld_nm, None):
                recs_by_fld[key] = rec
    return recs_by_fld


def get_choices(recs: list, key_nm: str, val_nm: str):
    choices = {}
    for rec in recs:
        choices[rec[key_nm]] = rec[val_nm]
    return choices


def get_fld(recs: dict, key_val, fld_nm: str):
    rec = recs.get(key_val)
    if rec is None:
        return None
    else:
        return rec.get(fld_nm)
