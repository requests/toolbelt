# -*- coding: utf-8 -*-
"""Test proxy digest authentication
"""

import unittest
import mock

import requests
from requests_toolbelt.auth import http_proxy_digest


class TestProxyDigestAuth(unittest.TestCase):
    def setUp(self):
        self.username = "username"
        self.password = "password"
        self.auth = http_proxy_digest.HTTPProxyDigestAuth(
            self.username, self.password
        )
        self.prepared_request = requests.Request(
            'GET',
            'http://host.org/index.html'
        ).prepare()

    def test_with_existing_nonce(self):
        """Test if it will generate Proxy-Authorization header
        when nonce present.
        Digest authentication's correctness will not be tested here.
        """
        self.auth.last_nonce = "bH3FVAAAAAAg74rL3X8AAI3CyBAAAAAA"
        self.auth.chal = {
            'nonce': self.auth.last_nonce,
            'realm': 'testrealm@host.org',
            'qop': 'auth'
        }

        # prepared_request headers should be clear before calling auth
        assert self.prepared_request.headers.get('Proxy-Authorization') is None
        self.auth(self.prepared_request)
        assert self.prepared_request.headers.get('Proxy-Authorization') is not None

    def test_no_challenge(self):
        """Tests that a response containing no authentication challenge is
        left alone.
        """
        connection = MockConnection()
        first_response = connection.make_response(self.prepared_request)
        first_response.status_code = 404

        assert self.auth.last_nonce == ''
        final_response = self.auth.handle_407(first_response)
        assert self.auth.last_nonce == ''
        assert first_response is final_response
        assert final_response.request.headers.get('Proxy-Authorization') is None

    def test_digest_challenge(self):
        """Tests that a response containing a digest authentication challenge
        gives rise to new request with a Proxy-Authorization header.
        Digest authentication's correctness will not be tested here.
        """
        connection = MockConnection()
        first_response = connection.make_response(self.prepared_request)
        first_response.status_code = 407
        first_response.headers['Proxy-Authenticate'] = \
            'Digest'\
            ' realm="Fake Realm", nonce="oS6WVgAAAABw698CAAAAAHAk/HUAAAAA",'\
            ' qop="auth", stale=false'

        assert self.auth.last_nonce == ''
        final_response = self.auth.handle_407(first_response)
        assert self.auth.last_nonce != ''
        assert first_response is not final_response
        assert final_response.request.headers.get('Proxy-Authorization') is not None

    def test_ntlm_challenge(self):
        """Tests that a response containing a non-Digest authentication
        challenge is left alone.
        """
        connection = MockConnection()
        first_response = connection.make_response(self.prepared_request)
        first_response.status_code = 407
        first_response.headers['Proxy-Authenticate'] = 'NTLM'

        assert self.auth.last_nonce == ''
        final_response = self.auth.handle_407(first_response)
        assert self.auth.last_nonce == ''
        assert first_response is final_response
        assert final_response.request.headers.get('Proxy-Authorization') is None


class MockConnection(object):
    def send(self, request, **kwargs):
        return self.make_response(request)

    def make_response(self, request):
        response = requests.Response()
        response.status_code = 200
        response.request = request
        response.raw = mock.MagicMock()
        response.connection = self
        return response

if __name__ == '__main__':
    unittest.main()
