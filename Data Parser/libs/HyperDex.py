#HyperDex library

from hyperclient import HyperClientException, Client
from UserException import NoSpaceSelected, InvalidSpaceDefinition


class HyperDex():
    def __init__(self, host="127.0.0.1", port=1982, space=None):
        """
        set up connection with hyperspace
        params:
            host: host of coordinator
            port: port of coordinator
            space: spaceName
        """
        self.host = host
        self.port = port
        self.connect()
        self.set_space(space)

    def connect(self):
        """
        set up connection
        """
        self.connection = Client(self.host, self.port)

    def create_space(self, name, key, attrs, subspace=None, parts=16, tol=2):
        """
        create new space
        params:
            name: spaceName
            key: key
            attrs: string of attributes and types
            subspace: rows to index
            parts: partitions
            tol: tolerate <n> failures
        """
        space_str = """space %s key %s attributes %s subspace %s
                       create %d partitions tolerate %d failures""" % \
                       (name, key, attrs, subspace, parts, tol)
        try:
                self.connection.add_space(space_str)
        except HyperClientException:
                raise InvalidSpaceDefinition(space_str)
        self.set_space(name)
        return

    def set_space(self, space):
        """
        set spaceName
        params:
            space: name to set
        """
        self.spaceName = space

    def insert(self, key, values):
        """
        insert record into space
        params:
            key: id to insert
            values: dict containing attributes and values to insert
        """
        return \
            self.connection.async_put_if_not_exist(self.spaceName, key, values)

    def insert_multiple(self, rows):
        """
        inserst multiple values at once using HyperDex.insert
        params:
            rows: List containing (multiple) ('key', {attr: val, ...})-pairs
        """
        if not self.spaceName:
            raise NoSpaceSelected('Please select a space')
        for k, v in rows:
            self.insert(k. v)

    def add_map(self, key, values):
        """
        add values to map of
        params:
            key: id of record
            values: dict containing key-value pairs
        """
        return self.connection.async_map_add(self.spaceName, key, values)

    def select(self, key):
        """
        get single record out of space
        params:
            key: id of record
        """
        return self.connection.get(self.spaceName, key)

    def select_multiple(self, cond):
        """
        return generator containing multiple items complying with condition
        params:
            cond: dict with conditions for search
        """
        return self.connection.search(self.spaceName, cond)
