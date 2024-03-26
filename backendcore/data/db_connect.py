"""
This is the interface to our database, whatever our database may be.
"""
import os
import json

import certifi

import pymongo as pm
from pymongo.server_api import ServerApi

from bson.objectid import ObjectId
import bson.json_util as bsutil

import backendcore.env.env_utils as envu

from common.constants import OBJ_ID_NM
import common.log as lg
import common.time_fmts as tfmt


# all of these will eventually be put in the env:
user_nm = os.getenv('MONGO_USER_NM', 'gcallah')
cloud_svc = os.getenv('MONGO_HOST', 'koukoumongo1.yud9b.mongodb.net')
passwd = os.environ.get("MONGO_PASSWD", '')
cloud_mdb = "mongodb+srv"
db_params = "retryWrites=true&w=majority"

LTE = '$lte'
GTE = '$gte'

DATE_KEY = '$date'

DB_ID = '_id'  # what our db uses as an ID
INNER_DB_ID = '$oid'  # it uses a nested structure!
DB_ID_LEN = 24

MAX_DB_INT = 9_223_372_036_854_775_807

API_DB = 'apiDB'
DSRC_DB = 'apiDB'
GEO_DB = 'geoDB'
HMDA_DB = 'hmdaDB'
SFA_DB = 'sfaDB'
TIME_SERIES_DB = 'time_seriesDB'
USER_DB = 'userDB'


TEST_PREFIX = 'test_'

DOC_LIMIT = 100000

# parameter names of mongo client settings
SERVER_API_PARAM = 'server_api'
CONN_TIMEOUT = 'connectTimeoutMS'
SOCK_TIMEOUT = 'socketTimeoutMS'
CONNECT = 'connect'
MAX_POOL_SIZE = 'maxPoolSize'

# Recommended Python Anywhere settings.
# We will use them eveywhere for now, until we determine some
# other site needs different settings.
PA_MONGO = os.getenv('PA_MONGO', True)
PA_SETTINGS = {
    CONN_TIMEOUT: os.getenv('MONGO_CONN_TIMEOUT', 30000),
    SOCK_TIMEOUT: os.getenv('MONGO_SOCK_TIMEOUT', None),
    CONNECT: os.getenv('MONGO_CONNECT', False),
    MAX_POOL_SIZE: os.getenv('MONGO_MAX_POOL_SIZE', 1),
}

MONGO_ID_NM = '_id'
DATE = 'date'

REMOTE = "0"
LOCAL = "1"

DESC = -1
NO_SORT = 0
NO_PROJ = []
ASC = 1

SUCCESS = 0
FAILURE = -1

# DB messages:
DUP = "Can't add duplicate"

# For now, client is a global singleton.
# Maybe one day we will need a... client per thread? I dunno.
client = None


def is_valid_id(rec_id: str):
    return isinstance(rec_id, str) and (len(rec_id) == DB_ID_LEN)


def extract_date(key: str, rec: dict):
    return rec[key][DATE_KEY]


def to_json(doc):
    """
    Turn doc to json.
    """
    return json.loads(bsutil.dumps(doc))


def get_collect(db_nm, collect_nm):
    """
    Just some syntactic sugar:
    """
    return client[db_nm][collect_nm]


def get_db_variant(db_nm):
    """
    Test DB name is always TEST_PREFIX + DB
    """
    if envu.is_flag_on("TEST_DB"):
        db_nm = TEST_PREFIX + db_nm
        print('Using test database')
    return db_nm


def get_server_settings():
    settings = {}
    SERVER_API = os.getenv("MONGO_SERVER_API")
    if SERVER_API:
        settings[SERVER_API_PARAM] = ServerApi(SERVER_API)
    if PA_MONGO:
        settings.update(PA_SETTINGS)
    return settings


def connectDB():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        lg.log_debug("Setting client because it is None.")
        if os.environ.get("LOCAL_MONGO", REMOTE) == LOCAL:
            lg.log_info("Connecting to Mongo locally.")
            client = pm.MongoClient()
        else:
            lg.log_info("Connecting to Mongo remotely.")
            settings = get_server_settings()
            # do we need a default DB?
            # some of the below params are just Mongo default:
            # we don't know what they mean!
            client = pm.MongoClient(f"{cloud_mdb}://{user_nm}:{passwd}@"
                                    + f"{cloud_svc}/{API_DB}?"
                                    + "retryWrites=true&w=majority",
                                    tlsCAFile=certifi.where(),
                                    **settings)
    return client


def setup_connection(db_nm):
    """
    We were repeatedly connecting AND getting the db name...
    so do them together.
    """
    connectDB()
    return get_db_variant(db_nm)


def _id_handler(rec, no_id):
    if rec:
        if no_id:
            del rec[DB_ID]
        else:
            # eliminate the ID nesting:
            rec[DB_ID] = rec[DB_ID][INNER_DB_ID]
    return rec


def fetch_one(db_nm, collect_nm, filters={}, no_id=False):
    """
    Fetch one record that meets filters.
    """
    rec = client[db_nm][collect_nm].find_one(filters)
    rec = to_json(rec)
    rec = _id_handler(rec, no_id)
    return rec


def create_id_filter(_id: str):
    return {MONGO_ID_NM: ObjectId(_id)}


def create_in_filter(fld_nm: str, values: list):
    return {fld_nm: {'$in': values}}


def create_exists_filter(fld_nm: str, predicate: bool = True):
    return {fld_nm: {'$exists': predicate}}


def create_or_filter(filt1: dict, filt2: dict):
    return {'$or': [filt1, filt2]}


def create_and_filter(filt1: dict, filt2: dict):
    return {'$and': [filt1, filt2]}


def fetch_by_id(db_nm, collect_nm, _id: str, no_id=False):
    """
    Fetch the record identified by _id if it exists.
    We convert the passed in string to an ID for our user.
    """
    filter = create_id_filter(_id)
    ret = client[db_nm][collect_nm].find_one(filter)
    rec = to_json(ret)
    rec = _id_handler(rec, no_id)
    return rec


def deleted_one(del_obj):
    return del_obj.deleted_count > 0


def num_deleted(del_obj):
    return del_obj.deleted_count


def del_one(db_nm, collect_nm, filters={}):
    """
    Delete one record that meets filters.
    """
    return client[db_nm][collect_nm].delete_one(filters)


def del_many(db_nm, collect_nm, filters={}):
    """
    Delete one record that meets filters.
    """
    return client[db_nm][collect_nm].delete_many(filters)


def del_by_id(db_nm, collect_nm, _id: str):
    """
    Delete one record identified by id.
    We convert the passed in string to an ID for our user.
    """
    filter = create_id_filter(_id)
    return client[db_nm][collect_nm].delete_one(filter)


def _asmbl_sort_cond(sort=NO_SORT, sort_fld='_id'):
    sort_cond = []
    if sort != NO_SORT:
        sort_cond.append((f'{sort_fld}', sort))
    return sort_cond


def fetch_all(db_nm, collect_nm, sort=NO_SORT, sort_fld=OBJ_ID_NM,
              no_id=False):
    """
    Returns all docs from a collection.
    `sort` can be DESC, NO_SORT, or ASC.
    """
    all_docs = []
    sort_cond = _asmbl_sort_cond(sort=sort, sort_fld=sort_fld)
    for doc in client[db_nm][collect_nm].find(sort=sort_cond).limit(DOC_LIMIT):
        rec = to_json(doc)
        rec = _id_handler(rec, no_id)
        all_docs.append(rec)
    return all_docs


def select_cursor(db_nm, collect_nm, filters={}, sort=NO_SORT,
                  sort_fld='_id', proj=NO_PROJ, limit=MAX_DB_INT):
    """
    A select that directly returns the mongo cursor.
    """
    sort_cond = _asmbl_sort_cond(sort=sort, sort_fld=sort_fld)
    return client[db_nm][collect_nm].find(filters, sort=sort_cond,
                                          projection=proj).limit(limit)


def select(db_nm, collect_nm, filters={}, sort=NO_SORT, sort_fld='_id',
           proj=NO_PROJ, limit=DOC_LIMIT, no_id=False, exclude_flds=None):
    """
    Select records from a collection matching filters.
    """
    selected_docs = []
    cursor = select_cursor(db_nm, collect_nm, filters=filters, sort=sort,
                           proj=proj, limit=limit)
    for doc in cursor:
        rec = to_json(doc)
        rec = _id_handler(rec, no_id)
        if exclude_flds:
            for fld_nm in exclude_flds:
                del rec[fld_nm]
        selected_docs.append(rec)
    return selected_docs


def count_documents(db_nm, collect_nm, filters={}):
    """
    Counts the documents in a collection, with an optional filter applied.
    """
    return client[db_nm][collect_nm].count_documents(filters)


def rename(db_nm: str, collect_nm: str, nm_map: dict):
    """
    Renames specified fields on all documents in a collection.

    Parameters
    ----------
    db_nm: str
        The database name.
    collect_nm: str
        The name of the database collection.
    nm_map: dict
        A dictionary. The keys are the current field names. Each key maps
        to the desired field name:
        {
            "old_nm1": "new_nm1",
            "old_nm2": "new_nm2",
        }
    """
    collect = client[db_nm][collect_nm]
    return collect.update_many({},
                               {'$rename': nm_map})


def insert_doc(db_nm: str, collect_nm: str, doc: dict, with_date=False):
    """
    Returns the str() of the inserted ID, or None on failure.
    `with_date=True` adds the current date to any inserted doc.
    """
    if with_date:
        doc[DATE] = str(tfmt.today())
    ret = client[db_nm][collect_nm].insert_one(doc)
    return str(ret.inserted_id)


def add_fld_to_all(db_nm, collect_nm, new_fld, value):
    collect = get_collect(db_nm, collect_nm)
    return collect.update_many({}, {'$set': {new_fld: value}},
                               upsert=False)


def update_fld(db_nm, collect_nm, filters, fld_nm, fld_val):
    """
    This should only be used when we just want to update a single
    field.
    To update more than one field in a doc, use `update_doc`.
    """
    collect = get_collect(db_nm, collect_nm)
    return collect.update_one(filters, {'$set': {fld_nm: fld_val}})


def update_fld_for_many(db_nm, collect_nm, filters, fld_nm, fld_val):
    """
    This should only be used when we just want to update a single
    field in many records.
    To update more than one field in a doc, use `update_doc`.
    """
    collect = get_collect(db_nm, collect_nm)
    return collect.update_many(filters, {'$set': {fld_nm: fld_val}})


def update_doc(db_nm, collect_nm, filters, update_dict):
    collect = get_collect(db_nm, collect_nm)
    return collect.update_one(filters, {'$set': update_dict})


def upsert_doc(db_nm, collect_nm, filters, update_dict):
    collect = get_collect(db_nm, collect_nm)
    ret = collect.update_one(filters, {'$set': update_dict}, upsert=True)
    rec_id = ret.upserted_id
    if not rec_id:  # we updated, not inserted
        rec = collect.find_one(update_dict)
        rec_id = rec[DB_ID]
    return str(rec_id)


def search_collection(db_nm, collect_nm, fld_nm, regex, active=False):
    """
    Searches a collection for occurences of regex in fld_nm.
    """
    match_list = []
    collect = get_collect(db_nm, collect_nm)
    for doc in collect.find({fld_nm: {"$regex": regex, "$options": 'i'}}):
        append = True
        if active:
            append = doc['active']
        if append:
            match_list.append(to_json(doc))
    return match_list


def append_to_list(db_nm, collect_nm, filter_fld_nm, filter_fld_val,
                   list_nm, new_list_item):
    collect = get_collect(db_nm, collect_nm)
    collect.update_one({filter_fld_nm: filter_fld_val},
                       {'$push': {list_nm: new_list_item}},
                       upsert=True)


def aggregate(db_nm, collect_nm, pipeline):
    return client[db_nm][collect_nm].aggregate(pipeline, allowDiskUse=True)
