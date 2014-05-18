# -*- coding: utf-8 -*-
"""

requests_toolbelt.streaming_iterator
====================================

This holds the implementation details for the :class:`StreamingIterator`. It
is designed for the case where you, the user, know the size of the upload but
need to provide the data as an iterator. This class will allow you to specify
the size and stream the data without using a chunked transfer-encoding.

"""

from .multipart.encoder import CustomBytesIO, encode_with


class StreamingIterator(object):

    """
    This class provides a way of allowing iterators with a known size to be
    streamed instead of chunked.

    """

    def __init__(self, size, iterator, encoding='utf-8'):
        #: The expected size of the upload
        self.size = int(size)

        if self.size < 0:
            raise ValueError(
                'The size of the upload must be a positive integer'
                )

        #: The iterator used to generate the upload data
        self.iterator = iterator

        #: Encoding the iterator is using
        self.encoding = encoding

        # The buffer we use to provide the correct number of bytes requested
        # during a read
        self._buffer = CustomBytesIO()

    def __len__(self):
        return self.size

    def _get_bytes(self):
        try:
            return encode_with(next(self.iterator), self.encoding)
        except StopIteration:
            return b''

    def _load_bytes(self, size):
        self._buffer.smart_truncate()
        amount_to_load = size - len(self._buffer)
        bytes_to_append = True

        while amount_to_load > 0 and bytes_to_append:
            bytes_to_append = self._get_bytes()
            amount_to_load -= self._buffer.append(bytes_to_append)

    def read(self, size=-1):
        size = int(size)
        if size == -1:
            return b''.join(self.iterator)

        self._load_bytes(size)
        return self._buffer.read(size)
        # Otherwise we're trying to read a specific size
        try:
            return next(self.iterator)
        except StopIteration:
            return b''
