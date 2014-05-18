# -*- coding: utf-8 -*-
import math
import unittest
from requests_toolbelt.multipart.encoder import (
    IDENTITY, MultipartEncoder, MultipartEncoderMonitor
    )


class TestMultipartEncoderMonitor(unittest.TestCase):
    def setUp(self):
        self.fields = {'a': 'b'}
        self.boundary = 'thisisaboundary'
        self.encoder = MultipartEncoder(self.fields, self.boundary)
        self.monitor = MultipartEncoderMonitor(self.encoder)

    def test_content_type(self):
        assert self.monitor.content_type == self.encoder.content_type

    def test_length(self):
        assert len(self.encoder) == len(self.monitor)

    def test_read(self):
        new_encoder = MultipartEncoder(self.fields, self.boundary)
        assert new_encoder.read() == self.monitor.read()

    def test_callback_called_when_reading_everything(self):
        callback = Callback(self.monitor)
        self.monitor.callback = callback
        self.monitor.read()
        assert callback.called == 1

    def test_callback(self):
        callback = Callback(self.monitor)
        self.monitor.callback = callback
        chunk_size = int(math.ceil(len(self.encoder) / 4.0))
        while self.monitor.read(chunk_size):
            pass
        assert callback.called == 5

    def test_bytes_read(self):
        bytes_to_read = len(self.encoder)
        self.monitor.read()
        assert self.monitor.bytes_read == bytes_to_read

    def test_default_callable_is_the_identity(self):
        assert self.monitor.callback == IDENTITY
        assert IDENTITY(1) == 1


class Callback(object):
    def __init__(self, monitor):
        self.called = 0
        self.monitor = monitor

    def __call__(self, monitor):
        self.called += 1
        assert monitor == self.monitor
