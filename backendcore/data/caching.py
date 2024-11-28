"""
Our interface to a collection of data.
"""
from copy import deepcopy
from functools import wraps

import backendcore.data.db_connect as dbc

from backendcore.common.constants import (
    CODE,
    NAME,
)

import backendcore.data.query as qry


"""
A little utility function.
"""


def can_do_math(record, fld):
    return fld in record and isinstance(record[fld], (int, float))


class DataCollection(object):
    caches: dict = {}

    @classmethod
    def is_registered(cls, cache_name):
        return cache_name in cls.caches

    @classmethod
    def get_cache(cls, cache_name):
        return cls.caches.get(cache_name, None)

    @classmethod
    def clear_collections(cls):
        """
        For tests to clear previous instantiations.
        """
        print('Clearing collections in use.')
        cls.caches: dict = {}

    def __init__(self, db_nm: str, collect_nm: str,
                 cache_nm: str = None,
                 key_fld: str = CODE,
                 sort_fld: str = NAME,
                 sort_order=dbc.ASC,
                 no_id=True):
        # db_nm might be adjusted when testing.
        caches = []
        for cache in self.caches:
            caches.append(str(cache))
        print(f'{caches=}')

        if not cache_nm:
            cache_nm = collect_nm
        if cache_nm in self.caches:
            print(f'{self.caches=}')
            raise ValueError('Attempt to instantiate multiple instances of '
                             + f'{cache_nm=}')
        else:
            self.caches[cache_nm] = self
        self.db_nm = db_nm
        self.collect_nm = collect_nm
        self.key_fld = key_fld
        self.sort_fld = sort_fld
        self.sort_order = sort_order
        self.no_id = no_id
        # our data caches:
        self.data_list = None
        self.data_dict = None

    def __str__(self):
        return str(self.data_list)

    def __len__(self):
        if self.data_list:
            return len(self.data_list)
        else:
            return 0

    def _post_fetch(self):
        """
        This is a hook for sub-classes to override if necessary.
        """
        pass

    def fetch_list(self, filters=None):
        if self.data_list is None:
            if filters is None:
                self.data_list = dbc.fetch_all(self.db_nm,
                                               self.collect_nm,
                                               no_id=self.no_id,
                                               sort=self.sort_order,
                                               sort_fld=self.sort_fld)
            else:
                self.data_list = dbc.select(self.db_nm,
                                            self.collect_nm,
                                            filters=filters,
                                            sort=dbc.ASC,
                                            sort_fld=self.sort_fld,
                                            no_id=self.no_id)
            self._post_fetch()
        return deepcopy(self.data_list)

    def fetch_dict(self, filters=None):
        """
        Sometimes it is more convenient to have a dictionary than a list!
        """
        if self.data_dict is None:
            self.data_dict = qry.list_to_dict(self.key_fld,
                                              self.fetch_list(filters))
        return deepcopy(self.data_dict)

    def fetch_by_key(self, key_val: str):
        """
        The key must be unique in our db, so we can fetch a unique
        record based on just it.
        """
        data_dict = self.fetch_dict()
        return data_dict.get(key_val)

    def fetch_keys(self):
        """
        Fetches a list of the keys
        """
        data_dict = self.fetch_dict()
        return list(data_dict.keys())

    def fetch_by_fld_val(self, fld, val, test_membership=False):
        """
        Fetches records with a field that matches a specific value.
        Returns a dict.
        """
        data_dict = self.fetch_dict()
        return qry.fetch_by_fld_val(fld, val, data_dict, test_membership)

    def exists(self, key_val: str):
        """
        Is a record with this code already in the factor DB?
        Returns True if so, else False.
        """
        return self.fetch_by_key(key_val) is not None

    def get_choices(self):
        """
        For pick lists.
        """
        return qry.get_choices(self.fetch_list(), self.key_fld, self.sort_fld)

    def clear_cache(self):
        self.data_list = None
        self.data_dict = None

    def empty_cache(self):  # for testing only!
        self.data_list = []
        self.data_dict = {}

    def _add_to_cache(self, rec: dict):
        """
        For cases where it is expensive to update the entire cache.
        """
        print(f'adding {rec=} to cache')
        key_val = rec.get(self.key_fld, None)
        if not key_val:
            raise ValueError('Attempt to add rec with missing key to cache')
        if self.data_dict:
            if key_val in self.data_dict:
                raise ValueError(f'Attempt to add dup {key_val} to cache')
        if not self.data_list:
            self.data_list = []
        self.data_list.append(rec)
        if not self.data_dict:
            self.data_dict = {}
        self.data_dict[key_val] = rec

    def add(self, rec: dict, clear_cache=True):
        """
        Creates a new record.
        If a record already has the given key_val, raise ValueError.
        By default we just clear the cache but if it is large we might not
        want to do that.
        """
        key_val = rec.get(self.key_fld, None)
        print(f'{key_val=}')
        if self.exists(key_val):
            print('key exists')
            raise ValueError(f'Attempt to add an existing {key_val=}')
        ret = dbc.insert_doc(self.db_nm, self.collect_nm, rec)
        print(f'Inserted record: {ret=}')
        if clear_cache:
            self.clear_cache()
        return ret

    def update(self, key_val: str, update_dict: dict, by_id: bool = False):
        if not self.exists(key_val):
            raise ValueError(f'Attempt to update a non-existent {key_val=}')
        if by_id:
            search_dict = dbc.create_id_filter(key_val)
        else:
            search_dict = {self.key_fld: key_val}
        ret = dbc.update_doc(self.db_nm,
                             self.collect_nm,
                             search_dict,
                             update_dict)
        self.clear_cache()
        return dbc.update_success(ret)

    def update_fld(self, key_val: str, fld_nm: str, fld_val: str, by_id: bool =
                   False):
        """
        Updates a field in a single record.
        """
        return self.update(key_val, {fld_nm: fld_val}, by_id)

    def delete(self, key_val: str, by_id: bool = False):
        """
        Deletes a record by key_val.
        If the key_val doesn't exist raises ValueError.
        Otherwise, return the DB result of the delete.
        """
        if not self.exists(key_val):
            raise ValueError(f'Attempt to delete a non-existent {key_val=}.')
        if by_id:
            ret = dbc.del_by_id(self.db_nm, self.collect_nm, key_val)
        else:
            ret = dbc.del_one(self.db_nm,
                              self.collect_nm,
                              {self.key_fld: key_val})
        self.clear_cache()
        return ret

    def aggregate(self, pipeline):
        return dbc.aggregate(self.db_nm, self.collect_nm, pipeline)


def get_cache(cache_nm):
    """
    Provide a functional interface to DataCollection.get_cache.
    """
    return DataCollection.get_cache(cache_nm)


def is_registered(cache_nm):
    """
    Provide a functional interface to DataCollection.is_registered.
    """
    return DataCollection.is_registered(cache_nm)


def needs_cache(fn, cache_nm, db_nm, collect_nm,
                key_fld=CODE, sort_order=dbc.ASC,
                sort_fld=NAME, no_id=True):
    """
    Should be used to decorate any function that uses data.collection methods.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # print(f'{cache_nm=}')
        # print(f'{glob_dict.get(cache_nm)=}')
        if not DataCollection.is_registered(cache_nm):
            DataCollection(db_nm,
                           collect_nm,
                           cache_nm=cache_nm,
                           key_fld=key_fld,
                           sort_order=sort_order,
                           sort_fld=sort_fld,
                           no_id=no_id)
        return fn(*args, **kwargs)
    return wrapper
