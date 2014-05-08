# -*- coding: utf-8 -*-
"""

requests_toolbelt.multipart.encoder
===================================

This holds all of the implementation details of the MultipartEncoder

"""

from requests.utils import super_len
from requests.packages.urllib3.filepost import iter_field_objects
from uuid import uuid4

import io


class MultipartEncoder(object):

    """

    The ``MultipartEncoder`` oject is a generic interface to the engine that
    will create a ``multipart/form-data`` body for you.

    The basic usage is::

        import requests
        from requests_toolbelt import MultipartEncoder

        encoder = MultipartEncoder({'field': 'value',
                                    'other_field', 'other_value'})
        r = requests.post('https://httpbin.org/post', data=encoder,
                          headers={'Content-Type': encoder.content_type})

    If you do not need to take advantage of streaming the post body, you can
    also do::

        r = requests.post('https://httpbin.org/post',
                          data=encoder.to_string(),
                          headers={'Content-Type': encoder.content_type})

    If you want the encoder to use a specific order, you can use an
    OrderedDict or more simply, a list of tuples::

        encoder = MultipartEncoder([('field', 'value'),
                                    ('other_field', 'other_value')])

    """

    def __init__(self, fields, boundary=None, encoding='utf-8'):
        #: Boundary value either passed in by the user or created
        self.boundary_value = boundary or uuid4().hex

        # Computed boundary
        self.boundary = '--{0}'.format(self.boundary_value)

        #: Encoding of the data being passed in
        self.encoding = encoding

        #: Fields provided by the user
        self.fields = fields

        #: Pre-computed parts of the upload
        self.computed_fields = []

        # Pre-computed fields iterator
        self._iter_computed = iter([])

        # Cached computation of the body's length
        self._len = None

        # Pre-compute each part's headers
        self._precompute_headers()

    def __len__(self):
        # If _len isn't already calculated, calculate it and set it
        return self._len or self._calculate_length()

    def __repr__(self):
        return '<MultipartEncoder: {0!r}>'.format(self.fields)

    def _precompute_headers(self):
        """This uses the fields provided by the user and computes the headers.

        It populates the `computed_fields` attribute and uses that to create a
        generator for iteration.
        """
        fields = iter_field_objects(to_list(self.fields))
        enc = self.encoding
        self.computed_fields = [
            (f.render_headers(), readable_data(f.data, enc)) for f in fields
            ]
        self._iter_computed = iter(self.computed_fields)

    def _calculate_length(self):
        """
        This uses the computed fields to calculate the length of the body.

        This returns the calculated length so __len__ can be lazy.
        """
        self._len = 0
        boundary_len = len(self.boundary)  # Length of --{boundary}
        for (header, data) in self._fields_list:
            # boundary length + header length + body length + len('\r\n') * 2
            self._len += boundary_len + len(header) + super_len(data) + 4
        # Length of trailing boundary '--{boundary}--\r\n'
        self._len += boundary_len + 4
        return self._len

    @property
    def content_type(self):
        return str('multipart/form-data; boundary={0}'.format(
            self.boundary_value
            ))

    def to_string(self):
        return self.read()

    def read(self, size=None):
        """Read data from the streaming encoder.

        :param int size: (optional), If provided, ``read`` will return exactly
            that many bytes. If it is not provided, it will return the
            remaining bytes.
        :returns: bytes
        """
        pass


def encode_with(string, encoding):
    """Encoding ``string`` with ``encoding`` if necessary.

    :param str string: If string is a bytes object, it will not encode it.
        Otherwise, this function will encode it with the provided encoding.
    :param str encoding: The encoding with which to encode string.
    :returns: encoded bytes object
    """
    if string and not isinstance(string, bytes):
        return string.encode(encoding)
    return string


def readable_data(data, encoding):
    if hasattr(data, 'read'):
        return data

    return CustomBytesIO(data, encoding)


def coerce_data(data, encoding):
    if not isinstance(data, CustomBytesIO):
        if hasattr(data, 'getvalue'):
            return CustomBytesIO(data.getvalue(), encoding)

        if hasattr(data, 'fileno'):
            return FileWrapper(data)

    return data


def to_list(fields):
    if hasattr(fields, 'items'):
        return list(fields.items())
    return list(fields)


class CustomBytesIO(io.BytesIO):
    def __init__(self, buffer=None, encoding='utf-8'):
        buffer = encode_with(buffer, encoding)
        super(CustomBytesIO, self).__init__(buffer)

    def _get_end(self):
        current_pos = self.tell()
        self.seek(0, 2)
        length = self.tell()
        self.seek(current_pos, 0)
        return length

    def __len__(self):
        length = self._get_end()
        return length - self.tell()

    def smart_truncate(self):
        to_be_read = len(self)
        already_read = self._get_end() - to_be_read

        if already_read >= to_be_read:
            old_bytes = self.read()
            self.seek(0, 0)
            self.truncate()
            self.write(old_bytes)
            self.seek(0, 0)  # We want to be at the beginning


class FileWrapper(object):
    def __init__(self, file_object):
        self.fd = file_object

    def __len__(self):
        return super_len(self.fd) - self.fd.tell()

    def read(self, length=-1):
        return self.fd.read(length)
