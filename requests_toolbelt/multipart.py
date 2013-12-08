from uuid import uuid4
from requests.packages.urllib3.filepost import (iter_field_objects,
                                                encode_multipart_formdata)

import io


class MultipartEncoder(object):
    def __init__(self, fields=None, boundary=None):
        self.boundary = boundary or uuid4().hex
        self.fields = fields
        self._field_iter = iter_field_objects(self.fields)
        self._bytes_io = CustomBytesIO()

    @property
    def content_type(self):
        return str('multipart/form-data; boundary={0}'.format(self.boundary))

    def to_string(self):
        return encode_multipart_formdata(self.fields, self.boundary)[0]

    def read(self, size=None):
        return self._read_bytes(size)

    def _read_bytes(self, size=None):
        if size is None:
            return self._read_remaining()

        size = int(size)  # Ensure it is always an integer
        bytes_length = len(CustomBytesIO)  # Calculate this once

        if size > bytes_length:
            self._load_bytes(size - bytes_length)

        return self._bytes_io.read(size)


class CustomBytesIO(io.BytesIO):
    def __init__(self, buffer=None):
        super(CustomBytesIO, self).__init__(buffer)

    def __len__(self):
        current_pos = self.tell()
        self.seek(0, 2)
        l = self.tell()
        self.seek(current_pos, 0)
        return l - current_pos
