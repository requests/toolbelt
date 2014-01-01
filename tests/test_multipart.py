import unittest
from requests_toolbelt.multipart import CustomBytesIO, MultipartEncoder


class TestCustomBytesIO(unittest.TestCase):
    def setUp(self):
        self.instance = CustomBytesIO()

    def test_writable(self):
        assert hasattr(self.instance, 'write')
        assert self.instance.write(b'example') == 7

    def test_readable(self):
        assert hasattr(self.instance, 'read')
        assert self.instance.read() == b''
        assert self.instance.read(10) == b''

    def test_can_read_after_writing_to(self):
        self.instance.write(b'example text')
        self.instance.read() == b'example text'

    def test_can_read_some_after_writing_to(self):
        self.instance.write(b'example text')
        self.instance.read(6) == b'exampl'

    def test_can_get_length(self):
        self.instance.write(b'example')
        self.instance.seek(0, 0)
        assert len(self.instance) == 7

    def test_truncates_intelligently(self):
        self.instance.write(b'abcdefghijklmnopqrstuvwxyzabcd')  # 30 bytes
        assert self.instance.tell() == 30
        self.instance.seek(-10, 2)
        self.instance.smart_truncate()
        assert len(self.instance) == 10
        assert self.instance.read() == b'uvwxyzabcd'
        assert self.instance.tell() == 10


class TestMultipartEncoder(unittest.TestCase):
    def setUp(self):
        self.parts = [('field', 'value'), ('other_field', 'other_value')]
        self.boundary = 'this-is-a-boundary'
        self.instance = MultipartEncoder(self.parts, boundary=self.boundary)

    def test_to_string(self):
        assert self.instance.to_string() == (
            '--this-is-a-boundary\r\n'
            'Content-Disposition: form-data; name="field"\r\n\r\n'
            'value\r\n'
            '--this-is-a-boundary\r\n'
            'Content-Disposition: form-data; name="other_field"\r\n\r\n'
            'other_value\r\n'
            '--this-is-a-boundary--\r\n'
        ).encode()

    def test_content_type(self):
        expected = 'multipart/form-data; boundary=this-is-a-boundary'
        assert self.instance.content_type == expected

    def test_encodes_data_the_same(self):
        assert self.instance.to_string() == self.instance.read()


if __name__ == '__main__':
    unittest.main()
