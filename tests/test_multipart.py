import unittest
from requests_toolbelt.multipart import CustomBytesIO, MultipartEncoder


class TestCustomBytesIO(unittest.TestCase):
    def setUp(self):
        self.instance = CustomBytesIO()

    def test_writable(self):
        assert hasattr(self.instance, 'write')
        assert self.instance.write('example') == 7

    def test_readable(self):
        assert hasattr(self.instance, 'read')
        assert self.instance.read() == ''
        assert self.instance.read(10) == ''

    def test_can_read_after_writing_to(self):
        self.instance.write('example text')
        self.instance.read() == 'example text'

    def test_can_read_some_after_writing_to(self):
        self.instance.write('example text')
        self.instance.read(6) == 'exampl'

    def test_can_get_length(self):
        self.instance.write('example')
        self.instance.seek(0, 0)
        assert len(self.instance) == 7


class TestMultipartEncoder(unittest.TestCase):
    def test_to_string(self):
        instance = MultipartEncoder([
            ('field', 'value'),
            ('other_field', 'other_value')
            ], boundary='this-is-a-boundary')
        assert instance.to_string() == (
            '--this-is-a-boundary\r\n'
            'Content-Disposition: form-data; name="field"\r\n\r\n'
            'value\r\n'
            '--this-is-a-boundary\r\n'
            'Content-Disposition: form-data; name="other_field"\r\n\r\n'
            'other_value\r\n'
            '--this-is-a-boundary--\r\n'
        )

    def test_content_type(self):
        instance = MultipartEncoder({}, boundary='this-is-a-boundary')
        expected = 'multipart/form-data; boundary=this-is-a-boundary'
        assert instance.content_type == expected


if __name__ == '__main__':
    unittest.main()
