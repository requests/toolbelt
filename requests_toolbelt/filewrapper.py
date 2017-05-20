# -*- coding: utf-8 -*-
"""Utility to force larger read sizes in httplib.

Currently, when you pass a file object to requests or urllib3, it ends up in
httplib (or http.client, if you're on Python 3). httplib has a fixed amount of
data that it reads from the file object (8192 bytes, or 8KB). This means that
for a 4GB file, it takes about 512 reads (i.e., it goes through a loop 512
times) and writes that many times to the socket. This can take a non-trivial
amount of time.

For people who need faster uploads, there is no way to tell httplib that you
want it to read a larger amount of data. In this case, we have to deliberately
create a wrapper object to force a larger amount of data to be returned than
was requested.


.. warning::

    Keep in mind, this is typically a bad idea when handing someone an object
    that they expect will observe the file protocol.
"""


class HttpFileWrapper(object):
    """A file wrapper that can be passed to requests or urllib3.

    Currently, when you pass a file object to requests or urllib3, it ends up
    in httplib (or http.client, if you're on Python 3). httplib has a fixed
    amount of data that it reads from the file object (8192 bytes, or 8KB).
    This means that for a 4GB file, it takes about 512 reads (i.e., it goes
    through a loop 512 times) and writes that many times to the socket. This
    can take a non-trivial amount of time.

    For people who need faster uploads, there is no way to tell httplib that
    you want it to read a larger amount of data. In this case, we have to
    deliberately create a wrapper object to force a larger amount of data to
    be returned than was requested.


    .. warning::

        Keep in mind, this is typically a bad idea when handing someone an
        object that they expect will observe the file protocol.

    """

    non_proxied_attrs = frozenset([
        'read', '_file_object', '_force_read_size'
    ])

    def __init__(self, file_object, force_read_size):
        self._file_object = file_object
        self._force_read_size = force_read_size

    def __getattr__(self, attr):
        get = object.__getattribute__
        if attr not in self.non_proxied_attrs:
            # If we're not trying to read or retrieve the file object, we are
            # trying to access an attribute on the stored file object.
            file_obj = get(self, '_file_object')
            return getattr(file_obj, attr)
        return get(self, attr)

    def read(self, size=-1):
        """Read data from the wrapped file object.

        If ``size`` is greater than 0 but less than the ``force_read_size``,
        we will return ``force_read_size`` (or less if the file object is
        nearly exhausted).

        If the ``size`` is -1, 0, or greater than ``force_read_size`` we will
        pass the ``size`` value directly to the ``read`` method on the wrapped
        file object.
        """
        force_size = self._force_read_size
        read = self._file_object.read
        if size == -1 or size == 0 or size > force_size:
            return read(size)
        return read(force_size)
