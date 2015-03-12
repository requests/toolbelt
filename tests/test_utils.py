"""Tests for the utils module."""
import io
import os
import os.path

import requests
from requests_toolbelt.utils import stream

from . import get_betamax


def test_stream_response_to_file_uses_content_disposition():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    filename = 'github3.py-0.7.1-py2.py3-none-any.whl'
    with recorder.use_cassette('stream_response_to_file'):
        r = s.get(url, headers={'Accept': 'application/octet-stream'})
        stream.stream_response_to_file(r)

    assert os.path.exists(filename)
    os.unlink(filename)


def test_stream_response_to_specific_filename():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    filename = 'github3.py.whl'
    with recorder.use_cassette('stream_response_to_file'):
        r = s.get(url, headers={'Accept': 'application/octet-stream'})
        stream.stream_response_to_file(r, path=filename)

    assert os.path.exists(filename)
    os.unlink(filename)


def test_stream_response_to_file_like_object():
    s = requests.Session()
    recorder = get_betamax(s)
    url = ('https://api.github.com/repos/sigmavirus24/github3.py/releases/'
           'assets/37944')
    file_obj = io.BytesIO()
    with recorder.use_cassette('stream_response_to_file'):
        r = s.get(url, headers={'Accept': 'application/octet-stream'})
        stream.stream_response_to_file(r, path=file_obj)

    assert 0 < file_obj.tell()
