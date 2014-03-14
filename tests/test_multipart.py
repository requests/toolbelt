import unittest
import io
import random
from requests_toolbelt.multipart import CustomBytesIO, MultipartEncoder
from requests.packages.urllib3.filepost import encode_multipart_formdata


class LargeFileMock(object):
    def __init__(self, file_size):
        # Let's keep track of how many bytes we've given
        self.bytes_read = 0
        # Our limit (1GB)
        self.bytes_max = file_size
        # Fake name
        self.name = 'fake_name.py'

    def __len__(self):
        return self.bytes_max - self.bytes_read

    def read(self, size=None):
        readable_max = self.bytes_max - self.bytes_read
        if readable_max <= 0:
            return b''

        if size is None or size < 0:
            length = readable_max
        else:
            length = min(size, readable_max)

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

    def test_accepts_encoded_strings_with_unicode(self):
        """Accepts a string with encoded unicode characters."""
        s = b'this is a unicode string: \xc3\xa9 \xc3\xa1 \xc7\xab \xc3\xb3'
        self.instance = CustomBytesIO(s)
        assert self.instance.read() == s


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
        encoded = encode_multipart_formdata(self.parts, self.boundary)[0]
        assert encoded == self.instance.read()

    def test_streams_its_data(self):
        large_file = LargeFileMock(123456789)
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

    def test_streams_its_data_with_correct_length(self):
        for i in range(0, 1000):
            file_size = random.randint(0, 12345)
            if random.random() < 0.1:
                file_size = 0  # sometimes we check with an empty file
            self.check_read_file_with_chunks(file_size, read_size=1)
            self.check_read_file_with_chunks(file_size, read_size=2)
            self.check_read_file_with_chunks(file_size, read_size=3)
            read_size = random.randint(0, 2*file_size)
            self.check_read_file_with_chunks(file_size, read_size=1)
            for read_size in range(file_size - 10, file_size + 200):
                if read_size < -1 or read_size == 0:
                    continue
                self.check_read_file_with_chunks(file_size, read_size)

    def check_read_file_with_chunks(self, file_size, read_size):
        print "===== Testing with file_size=",file_size,"read_size=",read_size
        boundary="deterministic-test-boundary"
        a_file = LargeFileMock(file_size)
        parts = {'some_field': 'this is the value...',
                 'some_file': a_file.read(),
        }
        expected_bytes = encode_multipart_formdata(parts, boundary)[0]
        content_length = len(expected_bytes)

        # Now read from our encoder :
        a_file = LargeFileMock(file_size)
        parts = {'some_field': 'this is the value...',
                 'some_file': a_file,
        }
        encoder = MultipartEncoder(parts, boundary=boundary)
        raw_bytes_count = 0
        while True:
            data = encoder.read(read_size)
            if not data:
                break
            print "read",len(data),"bytes : ",repr(data)
            assert data == expected_bytes[raw_bytes_count:raw_bytes_count+len(data)]
            raw_bytes_count += len(data)
        if raw_bytes_count != content_length:
            print "Test failed with file_size=",file_size,"and read_size=",read_size
        assert raw_bytes_count == content_length

    def test_length_is_correct(self):
        encoded = encode_multipart_formdata(self.parts, self.boundary)[0]
        assert len(encoded) == len(self.instance)

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

    def test_reads_open_file_objects_using_to_string(self):
        with open('setup.py', 'rb') as fd:
            m = MultipartEncoder([('field', 'foo'), ('file', fd)])
            assert m.to_string() is not None

    def test_handles_encoded_unicode_strings(self):
        m = MultipartEncoder([
            ('field',
             b'this is a unicode string: \xc3\xa9 \xc3\xa1 \xc7\xab \xc3\xb3')
        ])
        assert m.read() is not None

    def test_handles_uncode_strings(self):
        s = b'this is a unicode string: \xc3\xa9 \xc3\xa1 \xc7\xab \xc3\xb3'
        m = MultipartEncoder([
            ('field', s.decode('utf-8'))
        ])
        assert m.read() is not None


if __name__ == '__main__':
    unittest.main()
