# -*- coding: utf-8 -*-
import requests
import unittest
import mock

from requests_toolbelt.auth.guess import GuessAuth, GuessProxyAuth
from requests_toolbelt.auth.http_proxy_digest import HTTPProxyDigestAuth
from . import get_betamax
import betamax


class TestGuessAuth(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()
        self.recorder = get_betamax(self.session)

    def cassette(self, name):
        return self.recorder.use_cassette(
            'httpbin_guess_auth_' + name,
            match_requests_on=['method', 'uri', 'digest-auth']
        )

    def test_basic(self):
        with self.cassette('basic'):
            r = self.session.request(
                'GET', 'http://httpbin.org/basic-auth/user/passwd',
                auth=GuessAuth('user', 'passwd'))

        assert r.json() == {'authenticated': True, 'user': 'user'}

    def test_digest(self):
        with self.cassette('digest'):
            r = self.session.request(
                'GET', 'http://httpbin.org/digest-auth/auth/user/passwd',
                auth=GuessAuth('user', 'passwd'))

        assert r.json() == {'authenticated': True, 'user': 'user'}

    def test_no_auth(self):
        with self.cassette('none'):
            url = 'http://httpbin.org/get?a=1'
            r = self.session.request('GET', url,
                                     auth=GuessAuth('user', 'passwd'))

            j = r.json()
            assert j['args'] == {'a': '1'}
            assert j['url'] == url
            assert 'user' not in r.text
            assert 'passwd' not in r.text


class TestGuessProxyAuth(unittest.TestCase):

    @mock.patch('requests_toolbelt.auth.http_proxy_digest.HTTPProxyDigestAuth.handle_407')
    def test_handle_407_header_digest(self, mock_handle_407):
        r = requests.Response()
        r.headers['Proxy-Authenticate'] = 'Digest nonce="d2b19757d3d656a283c99762cbd1097b", opaque="1c311ad1cc6e6183b83bc75f95a57893", realm="me@kennethreitz.com", qop=auth'

        guess_auth = GuessProxyAuth(None, None, "user", "passwd")
        guess_auth.handle_407(r)

        mock_handle_407.assert_called_with(r)

    @mock.patch('requests.auth.HTTPProxyAuth.__call__')
    @mock.patch('requests.cookies.extract_cookies_to_jar')
    def test_handle_407_header_basic(self, extract_cookies_to_jar, proxy_auth_call):
        req = mock.Mock()
        r = mock.Mock()
        r.headers = dict()
        r.request.copy.return_value = req

        proxy_auth_call.return_value = requests.Response()

        kwargs = {}
        r.headers['Proxy-Authenticate'] = 'Basic realm="Fake Realm"'
        guess_auth = GuessProxyAuth(None, None, "user", "passwd")
        guess_auth.handle_407(r, *kwargs)

        proxy_auth_call.assert_called_with(req)


class ProxyAuthHeaderMatcher(betamax.BaseMatcher):
    name = 'proxy-auth-header'
    def match(self, request, recorded_request):
        requested = self.get_proxy_auth(request.headers)
        recorded = self.get_proxy_auth(recorded_request['headers'])
        return requested == recorded

    def get_proxy_auth(self, headers):
        from betamax.cassette.util import from_list
        auth = from_list(headers.get('Proxy-Authorization', ''))
        if not auth.startswith('Digest '):
            return auth
        else:
            # exclude cnonce and response, same as DigestAuthMatcher does
            excludes = ('cnonce', 'response')
            parts = auth.strip('Digest ').split(', ')
            return 'Digest ' + ', '.join(p for p in parts if not p.startswith(excludes))
betamax.Betamax.register_request_matcher(ProxyAuthHeaderMatcher)


class TestHTTPProxyDigestAuth(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()
        self.recorder = get_betamax(self.session)

    def cassette(self, name):
        return self.recorder.use_cassette(
            'httpbin_get_proxy_' + name + '_challenge',
            match_requests_on=['method', 'uri', 'proxy-auth-header']
        )

    def test_matched_challenge(self):
        with self.cassette("digest"):
            r = self.session.request(
                'GET', 'http://httpbin.org/get',
                auth=HTTPProxyDigestAuth('user', 'passwd'))

        assert r.status_code == 200
        assert r.json().get("headers", {}).get("Via") == "1.1 proxydigest (squid/3.3.9)"

    def test_mismatched_challenge(self):
        # Digest authentication won't help with an NTLM challenge, so it
        # should let the challenge pass rather than fall over responding to it.
        with self.cassette("ntlm"):
            r = self.session.request(
                'GET', 'http://httpbin.org/get',
                auth=HTTPProxyDigestAuth('user', 'passwd'))

        assert r.status_code == 407
