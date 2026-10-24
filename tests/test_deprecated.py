"""Tests for the response decoding helpers."""

import pytest
import requests

from requests_toolbelt.utils.deprecated import get_unicode_from_response


@pytest.mark.parametrize('header, content, expected', [
    ('unknown-codec', b'<meta charset="utf-8">caf\xc3\xa9',
     '<meta charset="utf-8">caf\xe9'),
    (None, b'<meta charset="unknown-codec"><meta charset="utf-8">caf\xc3\xa9',
     '<meta charset="unknown-codec"><meta charset="utf-8">caf\xe9'),
    ('unknown-codec', b'<meta charset="unknown-codec">plain text',
     '<meta charset="unknown-codec">plain text'),
    ('utf-8', b'caf\xc3\xa9', 'caf\xe9'),
    ('utf-8', b'caf\xff', 'caf\ufffd'),
    (None, b'plain text', 'plain text'),
])
def test_unknown_codec_fallback(header, content, expected):
    response = requests.Response()
    response._content = content
    if header:
        response.headers['Content-Type'] = 'text/html; charset=' + header
        response.encoding = header

    assert get_unicode_from_response(response) == expected
