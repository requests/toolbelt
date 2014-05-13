# -*- coding: utf-8 -*-
"""

requests_toolbelt.streaming_iterator
====================================

This holds the implementation details for the :class:`StreamingIterator`. It
is designed for the case where you, the user, know the size of the upload but
need to provide the data as an iterator. This class will allow you to specify
the size and stream the data without using a chunked transfer-encoding.

"""


class StreamingIterator(object):

    """
    This class provides a way of allowing iterators with a known size to be
    streamed instead of chunked.

    """

    def __init__(self, size, iterator):
        self.size = int(size)
        if self.size < 0:
            raise ValueError(
                'The size of the upload must be a positive integer'
                )
        self.iterator = iterator

    def __len__(self):
        return self.size

    def read(self, size=-1):
        if size == -1:
            return b''.join(self.iterator)

        # Otherwise we're trying to read a specific size
        try:
            return next(self.iterator)
        except StopIteration:
            return b''
