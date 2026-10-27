"""A competing creator must never lose its existing bytes."""
import os
from io import BytesIO

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

import pytest

from requests_toolbelt.downloadutils import stream
from requests_toolbelt.exceptions import StreamingError


def response():
    result = Mock()
    result.iter_content.return_value = [b"download"]
    return result


def test_competing_file_creation_preserves_winner(tmp_path, monkeypatch):
    target = tmp_path / "download.bin"
    real_os_open = os.open

    def race(path, flags, mode=0o777):
        with open(path, "wb") as winner:
            winner.write(b"competing file")
        return real_os_open(path, flags, mode)

    monkeypatch.setattr(stream.os, "open", race)
    with pytest.raises(StreamingError, match="File already exists"):
        stream.stream_response_to_file(response(), str(target))
    assert target.read_bytes() == b"competing file"


def test_descriptor_is_closed_when_wrapping_fails(tmp_path, monkeypatch):
    target = tmp_path / "download.bin"
    real_os_open = os.open
    real_os_close = os.close
    opened = []
    closed = []

    def record_open(path, flags, mode=0o777):
        opened.append(real_os_open(path, flags, mode))
        return opened[-1]

    def record_close(descriptor):
        closed.append(descriptor)
        real_os_close(descriptor)

    def fail_fdopen(descriptor, mode):
        raise MemoryError("synthetic fdopen failure")

    monkeypatch.setattr(stream.os, "open", record_open)
    monkeypatch.setattr(stream.os, "close", record_close)
    monkeypatch.setattr(stream.os, "fdopen", fail_fdopen)
    with pytest.raises(MemoryError, match="synthetic fdopen failure"):
        stream.stream_response_to_file(response(), str(target))
    assert len(opened) == 1
    assert closed == opened


def test_new_file_and_caller_owned_stream(tmp_path):
    target = tmp_path / "download.bin"
    assert stream.stream_response_to_file(response(), str(target)) == str(target)
    assert target.read_bytes() == b"download"
    supplied = BytesIO()
    assert stream.stream_response_to_file(response(), supplied) is None
    assert not supplied.closed
    assert supplied.getvalue() == b"download"
