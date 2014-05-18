# -*- coding: utf-8 -*-
"""

requests_toolbelt.multipart.encoder
===================================

This holds all of the implementation details of the MultipartEncoder

"""

from requests.utils import super_len
from requests.packages.urllib3.filepost import iter_field_objects
from uuid import uuid4

import contextlib
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

        # Pre-encoded boundary
        self._encoded_boundary = b''.join([
            encode_with(self.boundary, self.encoding),
            encode_with('\r\n', self.encoding)
            ])

        #: Fields provided by the user
        self.fields = fields

        #: Whether or not the encoder is finished
        self.finished = False

        #: Pre-computed parts of the upload
        self.parts = []

        # Pre-computed parts iterator
        self._iter_parts = iter([])

        # The part we're currently working with
        self._current_part = None

        # Cached computation of the body's length
        self._len = None

        # Our buffer
        self._buffer = CustomBytesIO(encoding=encoding)

        # Pre-compute each part's headers
        self._prepare_parts()

        # Load boundary into buffer
        self._write_boundary()

    def __len__(self):
        # If _len isn't already calculated, calculate, return, and set it
        return self._len or self._calculate_length()

    def __repr__(self):
        return '<MultipartEncoder: {0!r}>'.format(self.fields)

    def _calculate_length(self):
        """
        This uses the parts to calculate the length of the body.

        This returns the calculated length so __len__ can be lazy.
        """
        boundary_len = len(self.boundary)  # Length of --{boundary}
        # boundary length + header length + body length + len('\r\n') * 2
        self._len = sum(
            (boundary_len + len(p) + 4) for p in self.parts
            ) + boundary_len + 4
        return self._len

    def _calculate_load_amount(self, read_size):
        """This calculates how many bytes need to be added to the buffer.

        When a consumer read's ``x`` from the buffer, there are two cases to
        satisfy:

            1. Enough data in the buffer to return the requested amount
            2. Not enough data

        This function uses the amount of unread bytes in the buffer and
        determines how much the Encoder has to load before it can return the
        requested amount of bytes.

        :param int read_size: the number of bytes the consumer requests
        :returns: int -- the number of bytes that must be loaded into the
            buffer before the read can be satisfied. This will be strictly
            non-negative
        """
        amount = read_size - len(self._buffer)
        return amount if amount > 0 else 0

    def _load(self, amount):
        """Load ``amount`` number of bytes into the buffer."""
        self._buffer.smart_truncate()
        part = self._current_part or self._next_part()
        while amount == -1 or amount > 0:
            written = 0
            if not part.bytes_left_to_write():
                written += self._write(b'\r\n')
                written += self._write_boundary()
                part = self._next_part()

            if not part:
                written += self._write_closing_boundary()
                self.finished = True
                break

            written += part.write_to(self._buffer, amount)

            if amount != -1:
                amount -= written

    def _next_part(self):
        try:
            p = self._current_part = next(self._iter_parts)
        except StopIteration:
            p = None
        return p

    def _prepare_parts(self):
        """This uses the fields provided by the user and creates Part objects.

        It populates the `parts` attribute and uses that to create a
        generator for iteration.
        """
        fields = iter_field_objects(to_list(self.fields))
        enc = self.encoding
        self.parts = [Part.from_field(f, enc) for f in fields]
        self._iter_parts = iter(self.parts)

    def _write(self, bytes_to_write):
        """Write the bytes to the end of the buffer.

        :param bytes bytes_to_write: byte-string (or bytearray) to append to
            the buffer
        :returns: int -- the number of bytes written
        """
        return self._buffer.append(bytes_to_write)

    def _write_boundary(self):
        """Write the boundary to the end of the buffer."""
        return self._write(self._encoded_boundary)

    def _write_closing_boundary(self):
        """Write the bytes necessary to finish a multipart/form-data body."""
        with reset(self._buffer):
            self._buffer.seek(-2, 2)
            self._buffer.write(b'--\r\n')
        return 2

    def _write_headers(self, headers):
        """Write the current part's headers to the buffer."""
        return self._write(encode_with(headers, self.encoding))

    @property
    def content_type(self):
        return str(
            'multipart/form-data; boundary={0}'.format(self.boundary_value)
            )

    def to_string(self):
        return self.read()

    def read(self, size=-1):
        """Read data from the streaming encoder.

        :param int size: (optional), If provided, ``read`` will return exactly
            that many bytes. If it is not provided, it will return the
            remaining bytes.
        :returns: bytes
        """
        if self.finished:
            return self._buffer.read(size)

        bytes_to_load = size
        if bytes_to_load != -1 and bytes_to_load is not None:
            bytes_to_load = self._calculate_load_amount(int(size))

        self._load(bytes_to_load)
        return self._buffer.read(size)


IDENTITY = lambda monitor: monitor


class MultipartEncoderMonitor(object):

    """
    An object used to monitor the progress of a :class:`MultipartEncoder`.

    The :class:`MultipartEncoder` should only be responsible for preparing and
    streaming the data. For anyone who wishes to monitor it, they shouldn't be
    using that instance to manage that as well. Using this class, they can
    monitor an encoder and register a callback. The callback receives the
    instance of the monitor.

    To use this monitor, you construct your :class:`MultipartEncoder` as you
    normally would.

    .. code-block:: python

        from requests_toolbelt import (MultipartEncoder,
                                       MultipartEncoderMonitor)
        import requests

        def callback(encoder, bytes_read):
            # Do something with this information
            pass

        m = MultipartEncoder(fields={'field0': 'value0'})
        monitor = MultipartEncoderMonitor(m, callback)
        headers = {'Content-Type': montior.content_type}
        r = requests.post('https://httpbin.org/post', data=monitor,
                          headers=headers)

    """

    def __init__(self, encoder, callback=None):
        #: Instance of the :class:`MultipartEncoder` being monitored
        self.encoder = encoder

        #: Optionally function to call after a read
        self.callback = callback or IDENTITY

        #: Number of bytes already read from the :class:`MultipartEncoder`
        #: instance
        self.bytes_read = 0

    def __len__(self):
        return len(self.encoder)

    @property
    def content_type(self):
        return self.encoder.content_type

    def to_string(self):
        return self.read()

    def read(self, size=-1):
        string = self.encoder.read(size)
        self.bytes_read += len(string)
        self.callback(self)
        return string


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
    """Coerce the data to an object with a ``read`` method."""
    if hasattr(data, 'read'):
        return data

    return CustomBytesIO(data, encoding)


@contextlib.contextmanager
def reset(buffer):
    """Keep track of the buffer's current position and write to the end.

    This is a context manager meant to be used when adding data to the buffer.
    It eliminates the need for every function to be concerned with the
    position of the cursor in the buffer.
    """
    original_position = buffer.tell()
    buffer.seek(0, 2)
    yield
    buffer.seek(original_position, 0)


def coerce_data(data, encoding):
    """Ensure that every object's __len__ behaves uniformly."""
    if not isinstance(data, CustomBytesIO):
        if hasattr(data, 'getvalue'):
            return CustomBytesIO(data.getvalue(), encoding)

        if hasattr(data, 'fileno'):
            return FileWrapper(data)

        if not hasattr(data, 'read'):
            return CustomBytesIO(data, encoding)

    return data


def to_list(fields):
    if hasattr(fields, 'items'):
        return list(fields.items())
    return list(fields)


class Part(object):
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body
        self.headers_unread = True

    def __len__(self):
        return len(self.headers) + super_len(self.body)

    @classmethod
    def from_field(cls, field, encoding):
        """Create a part from a Request Field generated by urllib3."""
        headers = encode_with(field.render_headers(), encoding)
        body = coerce_data(field.data, encoding)
        return cls(headers, body)

    def bytes_left_to_write(self):
        """Determine if there are bytes left to write.

        :returns: bool -- ``True`` if there are bytes left to write, otherwise
            ``False``
        """
        to_read = 0
        if self.headers_unread:
            to_read += len(self.headers)

        return (to_read + len(self.body)) > 0

    def write_to(self, buffer, size):
        """Write the requested amount of bytes to the buffer provided.

        The number of bytes written may exceed size on the first read since we
        load the headers ambitiously.

        :param CustomBytesIO buffer: buffer we want to write bytes to
        :param int size: number of bytes requested to be written to the buffer
        :returns: int -- number of bytes actually written
        """
        written = 0
        if self.headers_unread:
            written += buffer.append(self.headers)
            self.headers_unread = False

        while len(self.body) > 0 and (size == -1 or written < size):
            amount_to_read = size
            if size != -1:
                amount_to_read = size - written
            written += buffer.append(self.body.read(amount_to_read))

        return written


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

    def append(self, bytes):
        with reset(self):
            written = self.write(bytes)
        return written

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
