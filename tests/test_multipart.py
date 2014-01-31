import unittest
import io
from requests_toolbelt.multipart import CustomBytesIO, MultipartEncoder


class LargeFileMock(object):
    def __init__(self):
        # Let's keep track of how many bytes we've given
        self.bytes_read = 0
        # Our limit (1GB)
        self.bytes_max = 1024 * 1024 * 1024
        # Fake name
        self.name = 'fake_name.py'

    def __len__(self):
        return self.bytes_max

    def read(self, size=None):
        if self.bytes_read >= self.bytes_max:
            return b''

        if size is None:
            length = self.bytes_max - self.bytes_read
        else:
            length = size

        length = int(length)

        self.bytes_read += length

        return b'a' * length


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

    def test_streams_its_data(self):
        large_file = LargeFileMock()
        parts = {'some field': 'value',
                 'some file': large_file,
                 }
        encoder = MultipartEncoder(parts)
        read_size = 1024 * 1024 * 128
        while True:
            read = encoder.read(read_size)
            if not read:
                break

        assert encoder._buffer.tell() <= read_size

    def test_length_is_correct(self):
        assert len(self.instance.to_string()) == len(self.instance)

    def test_encodes_with_readable_data(self):
        s = io.BytesIO(b'value')
        m = MultipartEncoder([('field', s)], boundary=self.boundary)
        assert m.read() == (
            '--this-is-a-boundary\r\n'
            'Content-Disposition: form-data; name="field"\r\n\r\n'
            'value\r\n'
            '--this-is-a-boundary--\r\n'
        ).encode()

    def test_reads_open_file_objects(self):
        with open('setup.py', 'rb') as fd:
            m = MultipartEncoder([('field', 'foo'), ('file', fd)])
            assert m.read() is not None

    def test_reads_open_file_objects_with_a_specified_filename(self):
        with open('setup.py', 'rb') as fd:
            m = MultipartEncoder(
                [('field', 'foo'), ('file', ('filename', fd, 'text/plain'))]
                )
            assert m.read() is not None


if __name__ == '__main__':
    unittest.main()
