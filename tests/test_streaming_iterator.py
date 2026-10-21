import io
import unittest

from requests_toolbelt.streaming_iterator import StreamingIterator

import pytest

@pytest.fixture(params=[True, False])
def get_iterable(request):
    '''
    When this fixture is used, the test is run twice -- once with the iterable
    being a file-like object, once being an iterator.
    '''
    is_file = request.param
    def inner(chunks):
        if is_file:
            return io.BytesIO(b''.join(chunks))
        return iter(chunks)
    return inner


class TestStreamingIterator(object):
    @pytest.fixture(autouse=True)
    def setup(self, get_iterable):
        self.chunks = [b'here', b'are', b'some', b'chunks']
        self.size = 17
        self.uploader = StreamingIterator(self.size, get_iterable(self.chunks))

    def test_read_returns_all_chunks_in_one(self):
        assert self.uploader.read() == b''.join(self.chunks)

    @pytest.mark.parametrize('size', [1, 4, 7, 17, 50])
    def test_read_all_preserves_bytes_after_sized_read(self, size):
        first = self.uploader.read(size)
        remaining = self.uploader.read()

        assert first + remaining == b''.join(self.chunks)
        assert self.uploader.read() == b''
        assert self.uploader.read(8192) == b''

    def test_read_all_consumes_buffer_after_iterator_is_exhausted(self):
        first = self.uploader.read(self.size - 1)
        remaining = self.uploader.read(-1)

        assert first + remaining == b''.join(self.chunks)
        assert remaining == b's'
        assert self.uploader.read() == b''
        assert self.uploader.read(1) == b''

    def test_read_returns_empty_string_after_exhausting_the_iterator(self):
        for i in range(0, 4):
            self.uploader.read(8192)

        assert self.uploader.read() == b''
        assert self.uploader.read(8192) == b''


class TestStreamingIteratorWithLargeChunks(object):
    @pytest.fixture(autouse=True)
    def setup(self, get_iterable):
        self.letters = [b'a', b'b', b'c', b'd', b'e']
        self.chunks = (letter * 2000 for letter in self.letters)
        self.size = 5 * 2000
        self.uploader = StreamingIterator(self.size, get_iterable(self.chunks))

    def test_returns_the_amount_requested(self):
        chunk_size = 1000
        bytes_read = 0
        while True:
            b = self.uploader.read(chunk_size)
            if not b:
                break
            assert len(b) == chunk_size
            bytes_read += len(b)

        assert bytes_read == self.size

    def test_returns_all_of_the_bytes(self):
        chunk_size = 8192
        bytes_read = 0
        while True:
            b = self.uploader.read(chunk_size)
            if not b:
                break
            bytes_read += len(b)

        assert bytes_read == self.size


@pytest.mark.parametrize('chunks', [[], [b''], [b'', b'']])
def test_empty_stream_read_all_after_zero_read(get_iterable, chunks):
    uploader = StreamingIterator(0, get_iterable(chunks))
    assert uploader.read(0) == b''
    assert uploader.read() == b''
    assert uploader.read() == b''
    assert uploader.read(1) == b''


class TestStreamingIteratorEmptyChunks(unittest.TestCase):
    chunks = (
        (b'', b'ab', b'cd'),
        (b'ab', b'', b'cd'),
        (b'ab', b'', b'', b'cd'),
        (b'ab', b'cd', b''),
        (b'', b'', b''),
    )

    def test_sized_reads_do_not_treat_empty_chunks_as_eof(self):
        for chunks in self.chunks:
            for size in (1, 2, 8192):
                expected = b''.join(chunks)
                stream = StreamingIterator(len(expected), iter(chunks))
                actual = b''.join(iter(lambda: stream.read(size), b''))
                self.assertEqual(actual, expected, (chunks, size))
                self.assertEqual(stream.read(size), b'')

    def test_read_all_handles_empty_chunks(self):
        for chunks in self.chunks:
            expected = b''.join(chunks)
            stream = StreamingIterator(len(expected), iter(chunks))
            self.assertEqual(stream.read(), expected)
            self.assertEqual(stream.read(), b'')
            self.assertEqual(stream.read(1), b'')

    def test_zero_read_does_not_consume_iterator(self):
        chunks = iter((b'', b'abc'))
        stream = StreamingIterator(3, chunks)
        self.assertEqual(stream.read(0), b'')
        self.assertEqual(next(chunks), b'')
        self.assertEqual(stream.read(3), b'abc')

    def test_read_all_preserves_buffer_with_empty_chunks(self):
        stream = StreamingIterator(8, iter((b'', b'abcdef', b'', b'gh')))
        self.assertEqual(stream.read(2), b'ab')
        self.assertEqual(stream.read(), b'cdefgh')
        self.assertEqual(stream.read(), b'')
        self.assertEqual(stream.read(1), b'')

    def test_finite_empty_iterator_has_stable_eof(self):
        stream = StreamingIterator(0, iter((b'', b'', b'')))
        for size in (1, 8192, 0, -1, 1):
            self.assertEqual(stream.read(size), b'')

    def test_file_like_behavior_is_unchanged(self):
        for data in (b'', b'abcd'):
            for size in (1, 2, 8192):
                stream = StreamingIterator(len(data), io.BytesIO(data))
                self.assertEqual(stream.read(0), b'')
                actual = b''.join(iter(lambda: stream.read(size), b''))
                self.assertEqual(actual, data)
                self.assertEqual(stream.read(), b'')

    def test_invalid_chunks_still_raise(self):
        for chunk, error in ((None, TypeError), (42, AttributeError)):
            stream = StreamingIterator(1, iter((chunk,)))
            self.assertRaises(error, stream.read, 1)
