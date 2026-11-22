import mmap

import pytest

from requests_toolbelt.multipart.encoder import (
    MultipartEncoder, coerce_data, total_len)


def test_mmap_remaining_length_decreases():
    with mmap.mmap(-1, 5) as data:
        data.write(b'hello')
        data.seek(2)
        body = coerce_data(data, 'utf-8')
        assert total_len(body) == 3
        assert body.read(1) == b'l'
        assert total_len(body) == 2
        assert body.read() == b'lo'
        assert total_len(body) == 0


@pytest.mark.parametrize('chunk_size', [-1, 1, 7])
@pytest.mark.parametrize('offset', [0, 2, 5])
def test_multipart_reads_mmap_to_completion(chunk_size, offset):
    with mmap.mmap(-1, 5) as data:
        data.write(b'hello')
        data.seek(offset)
        encoder = MultipartEncoder(
            fields={'file': ('hello.txt', data)}, boundary='test-boundary')
        expected = (
            b'--test-boundary\r\n'
            b'Content-Disposition: form-data; name="file"; '
            b'filename="hello.txt"\r\n\r\n' + b'hello'[offset:] +
            b'\r\n--test-boundary--\r\n')
        assert encoder.len == len(expected)
        chunks = []
        for _ in range(len(expected) + 2):
            chunk = encoder.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
        assert b''.join(chunks) == expected
        assert encoder.read() == b''
        assert not data.closed
