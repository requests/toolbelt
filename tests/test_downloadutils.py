"""Tests for the utils module."""
import io
import os
import os.path
import shutil
import tempfile

import requests
from requests_toolbelt.downloadutils import stream
from requests_toolbelt.downloadutils import tee
try:
    from unittest import mock
except ImportError:
    import mock
import pytest

from . import get_betamax


preserve_bytes = {'preserve_exact_body_bytes': True}


def test_get_download_file_path_uses_content_disposition():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    filename = 'github3.py-0.7.1-py2.py3-none-any.whl'
    with recorder.use_cassette('stream_response_to_file', **preserve_bytes):
        r = s.get(url, headers={'Accept': 'application/octet-stream'})
        path = stream.get_download_file_path(r, None)
        r.close()
        assert path == filename

def test_get_download_file_path_directory():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    filename = 'github3.py-0.7.1-py2.py3-none-any.whl'
    with recorder.use_cassette('stream_response_to_file', **preserve_bytes):
        r = s.get(url, headers={'Accept': 'application/octet-stream'})
        path = stream.get_download_file_path(r, tempfile.tempdir)
        r.close()
        assert path == os.path.join(tempfile.tempdir, filename)


def test_get_download_file_path_specific_file():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    with recorder.use_cassette('stream_response_to_file', **preserve_bytes):
        r = s.get(url, headers={'Accept': 'application/octet-stream'})
        path = stream.get_download_file_path(r, '/arbitrary/file.path')
        r.close()
        assert path == '/arbitrary/file.path'


def test_stream_response_to_file_uses_content_disposition():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    filename = 'github3.py-0.7.1-py2.py3-none-any.whl'
    with recorder.use_cassette('stream_response_to_file', **preserve_bytes):
        r = s.get(url, headers={'Accept': 'application/octet-stream'},
                  stream=True)
        stream.stream_response_to_file(r)

    assert os.path.exists(filename)
    os.unlink(filename)


def test_stream_response_to_specific_filename():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    filename = 'github3.py.whl'
    with recorder.use_cassette('stream_response_to_file', **preserve_bytes):
        r = s.get(url, headers={'Accept': 'application/octet-stream'},
                  stream=True)
        stream.stream_response_to_file(r, path=filename)

    assert os.path.exists(filename)
    os.unlink(filename)


def test_stream_response_to_directory():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')

    td = tempfile.mkdtemp()
    try:
        filename = 'github3.py-0.7.1-py2.py3-none-any.whl'
        expected_path = os.path.join(td, filename)
        with recorder.use_cassette('stream_response_to_file', **preserve_bytes):
            r = s.get(url, headers={'Accept': 'application/octet-stream'},
                      stream=True)
            stream.stream_response_to_file(r, path=td)

        assert os.path.exists(expected_path)
    finally:
        shutil.rmtree(td)


def test_stream_response_to_existing_file():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    filename = 'github3.py.whl'
    with open(filename, 'w') as f_existing:
        f_existing.write('test')

    with recorder.use_cassette('stream_response_to_file', **preserve_bytes):
        r = s.get(url, headers={'Accept': 'application/octet-stream'},
                  stream=True)
    try:
        stream.stream_response_to_file(r, path=filename)
    except stream.exc.StreamingError as e:
        assert str(e).startswith('File already exists:')
    else:
        assert False, "Should have raised a FileExistsError"
    finally:
        os.unlink(filename)


def test_stream_response_to_file_like_object():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    file_obj = io.BytesIO()
    with recorder.use_cassette('stream_response_to_file', **preserve_bytes):
        r = s.get(url, headers={'Accept': 'application/octet-stream'},
                  stream=True)
        stream.stream_response_to_file(r, path=file_obj)

    assert 0 < file_obj.tell()


def test_stream_response_to_file_chunksize():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')

    class FileWrapper(io.BytesIO):
        def __init__(self):
            super(FileWrapper, self).__init__()
            self.chunk_sizes = []

        def write(self, data):
            self.chunk_sizes.append(len(data))
            return super(FileWrapper, self).write(data)

    file_obj = FileWrapper()

    chunksize = 1231

    with recorder.use_cassette('stream_response_to_file', **preserve_bytes):
        r = s.get(url, headers={'Accept': 'application/octet-stream'},
                  stream=True)
        stream.stream_response_to_file(r, path=file_obj, chunksize=chunksize)

    assert 0 < file_obj.tell()

    assert len(file_obj.chunk_sizes) >= 1
    assert file_obj.chunk_sizes[0] == chunksize


@pytest.fixture
def streamed_response(chunks=None):
    chunks = chunks or [b'chunk'] * 8
    response = mock.MagicMock()
    response.raw.stream.return_value = chunks
    return response


def test_tee(streamed_response):
    response = streamed_response
    expected_len = len('chunk') * 8
    fileobject = io.BytesIO()
    assert expected_len == sum(len(c) for c in tee.tee(response, fileobject))
    assert fileobject.getvalue() == b'chunkchunkchunkchunkchunkchunkchunkchunk'


def test_tee_rejects_StringIO():
    fileobject = io.StringIO()
    with pytest.raises(TypeError):
        # The generator needs to be iterated over before the exception will be
        # raised
        sum(len(c) for c in tee.tee(None, fileobject))


def test_tee_to_file(streamed_response):
    response = streamed_response
    expected_len = len('chunk') * 8
    assert expected_len == sum(
        len(c) for c in tee.tee_to_file(response, 'tee.txt')
        )
    assert os.path.exists('tee.txt')
    os.remove('tee.txt')


def test_tee_to_bytearray(streamed_response):
    response = streamed_response
    arr = bytearray()
    expected_arr = bytearray(b'chunk' * 8)
    expected_len = len(expected_arr)
    assert expected_len == sum(
        len(c) for c in tee.tee_to_bytearray(response, arr)
        )
    assert expected_arr == arr


def test_tee_to_bytearray_only_accepts_bytearrays():
    with pytest.raises(TypeError):
        tee.tee_to_bytearray(None, object())


@pytest.mark.parametrize('header,expected', [
    ("attachment; filename*=UTF-8''caf%C3%A9.txt", u'caf\u00e9.txt'),
    ("attachment; filename*=UTF-8'tr'%C4%B0stanbul.txt", u'\u0130stanbul.txt'),
    ("attachment; filename*=ISO-8859-1'en'%A3rates.txt", u'\u00a3rates.txt'),
    ("attachment; FILENAME*=UTF-8''report+notes.txt", 'report+notes.txt'),
    ("attachment; filename=fallback.txt; filename*=UTF-8''caf%C3%A9.txt",
     u'caf\u00e9.txt'),
    ("attachment; filename*=UTF-8''caf%C3%A9.txt; filename=fallback.txt",
     u'caf\u00e9.txt'),
    ("attachment; filename*=UTF-8''..%2Ffolder%2Freport.txt", 'report.txt'),
    ("attachment; filename*=UTF-8''..%5Cfolder%5Creport.txt", 'report.txt'),
    ("attachment; filename*=UTF-8''C%3Areport.txt", 'report.txt'),
])
def test_extended_download_filename(header, expected):
    response = requests.Response()
    response.headers['Content-Disposition'] = header
    assert stream.get_download_file_path(response, None) == expected


@pytest.mark.parametrize('extended', [
    "missing-separators", "unknown''file.txt", "UTF-8''%FF.txt",
    "UTF-8''bad%ZZ.txt", "UTF-8''bad%.txt", "UTF-8''bad%00.txt",
    "UTF-8''..", "UTF-8''",
])
def test_invalid_extended_filename_falls_back(extended):
    header = 'attachment; filename=fallback.txt; filename*=' + extended
    assert stream._get_filename(header) == 'fallback.txt'


def test_stream_response_to_extended_filename(tmpdir):
    response = requests.Response()
    response.headers['Content-Disposition'] = (
        "attachment; filename*=UTF-8''caf%C3%A9.txt")
    response._content = b'file contents'
    response._content_consumed = True
    filename = stream.stream_response_to_file(response, str(tmpdir))
    assert filename == os.path.join(str(tmpdir), u'caf\u00e9.txt')
    with open(filename, 'rb') as downloaded:
        assert downloaded.read() == b'file contents'
