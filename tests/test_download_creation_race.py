"""A competing creator must never lose its existing bytes."""
from io import BytesIO
from unittest.mock import Mock

import pytest

from requests_toolbelt.downloadutils import stream
from requests_toolbelt.exceptions import StreamingError


def response():
    result = Mock()
    result.iter_content.return_value = [b"download"]
    return result


def test_competing_file_creation_preserves_winner(tmp_path, monkeypatch):
    target = tmp_path / "download.bin"
    real_open = open

    def race(path, mode):
        with real_open(path, "xb") as winner:
            winner.write(b"competing file")
        return real_open(path, mode)

    monkeypatch.setattr(stream, "open", race, raising=False)
    with pytest.raises(StreamingError, match="File already exists"):
        stream.stream_response_to_file(response(), str(target))
    assert target.read_bytes() == b"competing file"


def test_new_file_and_caller_owned_stream(tmp_path):
    target = tmp_path / "download.bin"
    assert stream.stream_response_to_file(response(), str(target)) == str(target)
    assert target.read_bytes() == b"download"
    supplied = BytesIO()
    assert stream.stream_response_to_file(response(), supplied) is None
    assert not supplied.closed
    assert supplied.getvalue() == b"download"
