# -*- coding: utf-8 -*-
import unittest
import io
from requests_toolbelt.multipart.encoder import CustomBytesIO, MultipartEncoder
from requests_toolbelt._compat import filepost


class LargeFileMock(object):
    def __init__(self):
        # Let's keep track of how many bytes we've given
        self.bytes_read = 0
        # Our limit (1GB)
        self.bytes_max = 1024 * 1024 * 1024
        # Fake name
        self.name = 'fake_name.py'
        # Create a fileno attribute
        self.fileno = None

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
        length = min([length, self.bytes_max - self.bytes_read])

        self.bytes_read += length

        return b'a' * length

    def tell(self):
        return self.bytes_read


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
        assert self.instance.len == 7

    def test_truncates_intelligently(self):
        self.instance.write(b'abcdefghijklmnopqrstuvwxyzabcd')  # 30 bytes
        assert self.instance.tell() == 30
        self.instance.seek(-10, 2)
        self.instance.smart_truncate()
        assert self.instance.len == 10
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
        encoded = filepost.encode_multipart_formdata(self.parts,
                                                     self.boundary)[0]
        assert encoded == self.instance.read()

    def test_streams_its_data(self):
        large_file = LargeFileMock()
        parts = {'some field': 'value',
                 'some file': large_file,
                 }
        encoder = MultipartEncoder(parts)
        total_size = encoder.len
        read_size = 1024 * 1024 * 128
        already_read = 0
        while True:
            read = encoder.read(read_size)
            already_read += len(read)
            if not read:
                break

        assert encoder._buffer.tell() <= read_size
        assert already_read == total_size

    def test_length_is_correct(self):
        encoded = filepost.encode_multipart_formdata(self.parts,
                                                     self.boundary)[0]
        assert len(encoded) == self.instance.len

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

    def test_regresion_1(self):
        """Ensure issue #31 doesn't ever happen again."""
        fields = {
            "test": "t" * 100
        }

        for x in range(30):
            fields['f%d' % x] = (
                'test', open('tests/test_multipart_encoder.py', 'rb')
                )

        m = MultipartEncoder(fields=fields)
        total_size = m.len

        blocksize = 8192
        read_so_far = 0

        while True:
            data = m.read(blocksize)
            if not data:
                break
            read_so_far += len(data)

        assert read_so_far == total_size

    def test_regression_2(self):
        """Ensure issue #31 doesn't ever happen again."""
        fields = {
            "test": "t" * 8100
        }

        m = MultipartEncoder(fields=fields)
        total_size = m.len

        blocksize = 8192
        read_so_far = 0

        while True:
            data = m.read(blocksize)
            if not data:
                break
            read_so_far += len(data)

        assert read_so_far == total_size

    def test_handles_empty_unicode_values(self):
        """Verify that the Encoder can handle empty unicode strings.

        See https://github.com/sigmavirus24/requests-toolbelt/issues/46 for
        more context.
        """
        fields = [(b'test'.decode('utf-8'), b''.decode('utf-8'))]
        m = MultipartEncoder(fields=fields)
        assert len(m.read()) > 0

    def test_accepts_custom_content_type(self):
        """Verify that the Encoder handles custom content-types.

        See https://github.com/sigmavirus24/requests-toolbelt/issues/52
        """
        fields = [
            (b'test'.decode('utf-8'), (b'filename'.decode('utf-8'),
                                       b'filecontent',
                                       b'application/json'.decode('utf-8')))
        ]
        m = MultipartEncoder(fields=fields)
        output = m.read().decode('utf-8')
        assert output.index('Content-Type: application/json\r\n') > 0

    def test_accepts_custom_headers(self):
        """Verify that the Encoder handles custom headers.

        See https://github.com/sigmavirus24/requests-toolbelt/issues/52
        """
        fields = [
            (b'test'.decode('utf-8'), (b'filename'.decode('utf-8'),
                                       b'filecontent',
                                       b'application/json'.decode('utf-8'),
                                       {'X-My-Header': 'my-value'}))
        ]
        m = MultipartEncoder(fields=fields)
        output = m.read().decode('utf-8')
        assert output.index('X-My-Header: my-value\r\n') > 0


if __name__ == '__main__':
    unittest.main()
