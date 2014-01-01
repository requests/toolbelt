from requests.utils import super_len
from requests.packages.urllib3.filepost import (iter_field_objects,
                                                encode_multipart_formdata)
from uuid import uuid4

import io


class MultipartEncoder(object):
    def __init__(self, fields, boundary=None):
        #: Boundary value either passed in by the user or created
        self.boundary_value = boundary or uuid4().hex
        self.boundary = '--{0}'.format(self.boundary_value)

        #: Fields passed in by the user
        self.fields = fields

        # Most recently used data
        self._current_data = None

        # Length of the body
        self._len = None

        # Our buffer
        self._buffer = CustomBytesIO()

        # This a list of two-tuples containing the rendered headers and the
        # data.
        self._fields_list = []

        # Iterator over the fields so we don't lose track of where we are
        self._fields_iter = None

        # Pre-render the headers so we can calculate the length
        self._render_headers()

    def __len__(self):
        if self._len is None:
            self._calculate_length()

        return self._len

    def _calculate_length(self):
        boundary_len = len(self.boundary)  # Length of --{boundary}
        self._len = 0
        for (header, data) in self._fields_list:
            # boundary length + header length + body length + len('\r\n') * 2
            self._len += boundary_len + len(header) + super_len(data) + 4
        # Length of trailing boundary '--{boundary}--\r\n'
        self._len += boundary_len + 4

    @property
    def content_type(self):
        return str('multipart/form-data; boundary={0}'.format(
            self.boundary_value
            ))

    def to_string(self):
        return encode_multipart_formdata(self.fields, self.boundary_value)[0]

    def read(self, size=None):
        return self._read_bytes(size)

    def _load_bytes(self, size):
        written = 0
        orig_position = self._buffer.tell()

        # Consume previously unconsumed data
        written += self._consume_current_data(size)

        while size is None or written < size:
            next_tuple = self._next_tuple()
            if not next_tuple:
                break

            headers, data = next_tuple

            # We have a tuple, write the headers in their entirety.
            # They aren't that large, if we write more than was requested, it
            # should not hurt anyone much.
            written += self._buffer.write(headers.encode())
            self._current_data = data
            if size is not None and written < size:
                self._consume_current_data(size - written)
                #self._buffer.write(self._current_data.read(size - written))
            else:
                self._consume_current_data(None)
                #self._buffer.write(self._current_data.read())

        self._buffer.seek(orig_position, 0)
        self._buffer.smart_truncate()

    def _consume_current_data(self, size):
        written = 0

        if self._current_data is None:
            written = self._buffer.write(self.boundary.encode())
            written += self._buffer.write('\r\n'.encode())

        elif (self._current_data is not None and
                super_len(self._current_data) > 0):
            written = self._buffer.write(self._current_data.read(size))

        if super_len(self._current_data) == 0:
            written += self._buffer.write(
                '\r\n{0}\r\n'.format(self.boundary).encode()
                )

        return written

    def _next_tuple(self):
        next_tuple = tuple()

        try:
            # Try to get another field tuple
            next_tuple = next(self._fields_iter)
        except StopIteration:
            # We reached the end of the list, so write the closing
            # boundary. The last file tuple wrote a boundary like:
            # --{boundary}\r\n, so move back two characters, truncate and
            # write the proper ending.
            self._buffer.seek(-2, 1)
            self._buffer.truncate()
            self._buffer.write('--\r\n'.encode())
            #self._buffer.write('\r\n{0}--\r\n'.format(self.boundary))

        return next_tuple

    def _read_bytes(self, size=None):
        if size is None:
            self._load_bytes(None)  # Almost infinity but not float('inf')
        else:
            size = int(size)  # Ensure it is always an integer
            bytes_length = len(self._buffer)  # Calculate this once

            if size > bytes_length:
                self._load_bytes(size - bytes_length)

        return self._buffer.read(size)

    def _render_headers(self):
        iter_fields = iter_field_objects(self.fields)
        self._fields_list = [
            (f.render_headers(), readable_data(f.data)) for f in iter_fields
            ]
        self._fields_iter = iter(self._fields_list)


def readable_data(data):
    if hasattr(data, 'read'):
        return data
    return CustomBytesIO(data)


class CustomBytesIO(io.BytesIO):
    def __init__(self, buffer=None):
        if hasattr(buffer, 'encode'):
            buffer = buffer.encode()
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
        length = self._get_end()

        if length >= 2 * to_be_read:
            old_bytes = self.read()
            self.seek(0, 0)
            self.truncate()
            self.write(old_bytes)
            self.seek(0, 0)  # We want to be at the beginning
