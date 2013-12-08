from uuid import uuid4
from requests.packages.urllib3.filepost import (iter_field_objects,
                                                encode_multipart_formdata)


class MultipartEncoder(object):
    def __init__(self, fields=None, boundary=None):
        self.boundary = boundary or uuid4().hex
        self.fields = fields
        self._field_iter = iter_field_objects(self.fields)

    @property
    def content_type(self):
        return 'multipart/form-data; boundary={0}'.format(self.boundary)

    def to_string(self):
        return encode_multipart_formdata(self.fields, self.boundary)[0]

    def read(self, size=None):
        raise NotImplementedError('This feature is not implemented yet.')
