"""
This is the interface to our database, whatever our database may be.
"""
import os

import backendcore.data.databases.mongo_connect as mdb

REMOTE = "0"
LOCAL = "1"

DESC = -1
NO_SORT = 0
NO_PROJ = []
ASC = 1

SUCCESS = 0
FAILURE = -1

# Databases supported:
MONGO = 'MongoDB'
MY_SQL = 'MySQL'
SQLITE = 'SQLite'

# DB messages:
DUP = "Can't add duplicate"

# For now database is a global singleton.
# Maybe one day we will need a... database per thread? I dunno.
database = None


def set_db(db) -> None:
    global database
    database = db


def setup_connection(db_nm):
    """
    Sets up connection to appropriate DB.
    The return of db_nm is an artefact of earlier
    architecture. We should work to make it
    unnecessary.
    """
    global database
    if database is None:
        db_type = os.environ.get('DATABASE', MONGO)
    if db_type == MONGO:
        local = os.environ.get("LOCAL_MONGO", REMOTE) == LOCAL
        database = mdb.MongoDB(local_db=local)
    return db_nm


def fetch_one(db_nm, clct_nm, filters={}, no_id=False):
    """
    Fetch one record that meets filters.
    """
    return database.read_one(db_nm, clct_nm, filters=filters,
                             no_id=no_id)


# def create_in_filter(fld_nm: str, values: list):
#     return {fld_nm: {'$in': values}}


# def create_exists_filter(fld_nm: str, predicate: bool = True):
#     return {fld_nm: {'$exists': predicate}}


# def create_or_filter(filt1: dict, filt2: dict):
#     return {'$or': [filt1, filt2]}


# def create_and_filter(filt1: dict, filt2: dict):
#     return {'$and': [filt1, filt2]}


# def fetch_by_id(db_nm, clct_nm, _id: str, no_id=False):
#     """
#     Fetch the record identified by _id if it exists.
#     We convert the passed in string to an ID for our user.
#     """
#     rec = {}
#     return rec


# def delete_success(del_obj):
#     return del_obj.deleted_count > 0


# def num_deleted(del_obj):
#     return del_obj.deleted_count


# def del_one(db_nm, clct_nm, filters={}):
#     """
#     Delete one record that meets filters.
#     """
#     return database[db_nm][clct_nm].delete_one(filters)


# def del_many(db_nm, clct_nm, filters={}):
#     """
#     Delete one record that meets filters.
#     """
#     return database[db_nm][clct_nm].delete_many(filters)


# def del_by_id(db_nm, clct_nm, _id: str):
#     """
#     Delete one record identified by id.
#     We convert the passed in string to an ID for our user.
#     """
#     filter = create_id_filter(_id)
#     return database[db_nm][clct_nm].delete_one(filter)


# def _asmbl_sort_cond(sort=NO_SORT, sort_fld='_id'):
#     sort_cond = []
#     if sort != NO_SORT:
#         sort_cond.append((f'{sort_fld}', sort))
#     return sort_cond


# def fetch_all(db_nm, clct_nm, sort=NO_SORT, sort_fld=OBJ_ID_NM,
#               no_id=False):
#     """
#     Returns all docs from a collection.
#     `sort` can be DESC, NO_SORT, or ASC.
#     """
#     return all_docs


# def select_cursor(db_nm, clct_nm, filters={}, sort=NO_SORT,
#                   sort_fld='_id', proj=NO_PROJ, limit=MAX_DB_INT):
#     """
#     A select that directly returns the mongo cursor.
#     """
#     sort_cond = _asmbl_sort_cond(sort=sort, sort_fld=sort_fld)
#     return database[db_nm][clct_nm].find(filters, sort=sort_cond,
#                                        projection=proj).limit(limit)


# def select(db_nm, clct_nm, filters={}, sort=NO_SORT, sort_fld='_id',
#            proj=NO_PROJ, limit=DOC_LIMIT, no_id=False, exclude_flds=None):
#     """
#     Select records from a collection matching filters.
#     """
#     selected_docs = []
#     cursor = select_cursor(db_nm, clct_nm, filters=filters, sort=sort,
#                            proj=proj, limit=limit)
#     for doc in cursor:
#         rec = to_json(doc)
#         rec = _id_handler(rec, no_id)
#         if exclude_flds:
#             for fld_nm in exclude_flds:
#                 del rec[fld_nm]
#         selected_docs.append(rec)
#     return selected_docs


# def count_documents(db_nm, clct_nm, filters={}):
#     """
#     Counts the documents in a collection, with an optional filter applied.
#     """
#     return database[db_nm][clct_nm].count_documents(filters)


# def rename(db_nm: str, clct_nm: str, nm_map: dict):
#     """
#     Renames specified fields on all documents in a collection.

#     Parameters
#     ----------
#     db_nm: str
#         The database name.
#     clct_nm: str
#         The name of the database collection.
#     nm_map: dict
#         A dictionary. The keys are the current field names. Each key maps
#         to the desired field name:
#         {
#             "old_nm1": "new_nm1",
#             "old_nm2": "new_nm2",
#         }
#     """
#     collect = database[db_nm][clct_nm]
#     return collect.update_many({},
#                                {'$rename': nm_map})


# def insert_doc(db_nm: str, clct_nm: str, doc: dict, with_date=False):
#     """
#     Returns the str() of the inserted ID, or None on failure.
#     `with_date=True` adds the current date to any inserted doc.
#     """
#     if with_date:
#         print('with_date format is not supported at present time')
#     ret = database[db_nm][clct_nm].insert_one(doc)
#     return str(ret.inserted_id)


# def add_fld_to_all(db_nm, clct_nm, new_fld, value):
#     collect = get_collect(db_nm, clct_nm)
#     return collect.update_many({}, {'$set': {new_fld: value}},
#                                upsert=False)


# def update_fld(db_nm, clct_nm, filters, fld_nm, fld_val):
#     """
#     This should only be used when we just want to update a single
#     field.
#     To update more than one field in a doc, use `update_doc`.
#     """
#     collect = get_collect(db_nm, clct_nm)
#     return collect.update_one(filters, {'$set': {fld_nm: fld_val}})


# def update_fld_for_many(db_nm, clct_nm, filters, fld_nm, fld_val):
#     """
#     This should only be used when we just want to update a single
#     field in many records.
#     To update more than one field in a doc, use `update_doc`.
#     """
#     collect = get_collect(db_nm, clct_nm)
#     return collect.update_many(filters, {'$set': {fld_nm: fld_val}})


# def update_doc(db_nm, clct_nm, filters, update_dict):
#     collect = get_collect(db_nm, clct_nm)
#     return collect.update_one(filters, {'$set': update_dict})


# def upsert_doc(db_nm, clct_nm, filters, update_dict):
#     collect = get_collect(db_nm, clct_nm)
#     ret = collect.update_one(filters, {'$set': update_dict}, upsert=True)
#     rec_id = ret.upserted_id
#     if not rec_id:  # we updated, not inserted
#         rec = collect.find_one(update_dict)
#         rec_id = rec[DB_ID]
#     return str(rec_id)


# def update_success(update_obj):
#     return update_obj.matched_count > 0


# def num_updated(update_obj):
#     return update_obj.modified_count


# def search_collection(db_nm, clct_nm, fld_nm, regex, active=False):
#     """
#     Searches a collection for occurences of regex in fld_nm.
#     """
#     match_list = []
#     collect = get_collect(db_nm, clct_nm)
#     for doc in collect.find({fld_nm: {"$regex": regex, "$options": 'i'}}):
#         append = True
#         if active:
#             append = doc['active']
#         if append:
#             match_list.append(to_json(doc))
#     return match_list


# def append_to_list(db_nm, clct_nm, filter_fld_nm, filter_fld_val,
#                    list_nm, new_list_item):
#     collect = get_collect(db_nm, clct_nm)
#     collect.update_one({filter_fld_nm: filter_fld_val},
#                        {'$push': {list_nm: new_list_item}},
#                        upsert=True)


# def aggregate(db_nm, clct_nm, pipeline):
#     return database[db_nm][clct_nm].aggregate(pipeline, allowDiskUse=True)
