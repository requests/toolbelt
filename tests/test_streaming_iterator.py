from requests_toolbelt.streaming_iterator import StreamingIterator

import unittest


class TestStreamingIterator(unittest.TestCase):
    def setUp(self):
        self.chunks = ['here', 'are', 'some', 'chunks']
        self.iterator = iter(self.chunks)
        self.size = 17
        self.uploader = StreamingIterator(self.size, self.iterator)

    def test_read_returns_chunks(self):
        for chunk in self.chunks:
            assert self.uploader.read(8192) == chunk

    def test_read_returns_all_chunks_in_one(self):
        assert self.uploader.read() == ''.join(self.chunks)

    def test_read_returns_empty_string_after_exhausting_the_iterator(self):
        for i in range(0, 4):
            self.uploader.read(8192)

        assert self.uploader.read() == b''
        assert self.uploader.read(8192) == b''
