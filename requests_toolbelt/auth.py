# -*- coding: utf-8 -*-
"""

requests_toolbelt.auth
======================

Various utilities around authentication.

"""
import re

from requests.auth import HTTPDigestAuth, HTTPBasicAuth, AuthBase
from requests.auth import parse_dict_header
from requests.cookies import extract_cookies_to_jar, RequestsCookieJar


class GuessAuth(AuthBase):
    """Guesses the auth type by the WWW-Authentication header."""
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.auth = None
        self.pos = None

    def handle_401(self, r, **kwargs):
        """Resends a request with auth headers, if needed."""

        www_authenticate = r.headers.get('www-authenticate', '').lower()

        if 'basic' in www_authenticate:
            if self.pos is not None:
                r.request.body.seek(self.pos)

            # Consume content and release the original connection
            # to allow our new request to reuse the same one.
            r.content
            r.raw.release_conn()
            prep = r.request.copy()
            if not hasattr(prep, '_cookies'):
                prep._cookies = RequestsCookieJar()
            extract_cookies_to_jar(prep._cookies, r.request, r.raw)
            prep.prepare_cookies(prep._cookies)

            self.auth = HTTPBasicAuth(self.username, self.password)
            prep = self.auth(prep)
            _r = r.connection.send(prep, **kwargs)
            _r.history.append(r)
            _r.request = prep

            return _r

        if 'digest' in www_authenticate:
            self.auth = HTTPDigestAuth(self.username, self.password)
            # Digest auth would resend the request by itself. We can take a
            # shortcut here.
            return self.auth.handle_401(r, **kwargs)

    def __call__(self, request):
        if self.auth is not None:
            return self.auth(request)

        try:
            self.pos = request.body.tell()
        except AttributeError:
            pass

        request.register_hook('response', self.handle_401)
        return request


class HTTPProxyDigestAuth(HTTPDigestAuth):
    """HTTP digest authentication between proxy"""
    def __init__(self, *args, **kwargs):
        """
        Attributes:
            stale_rejects: The number of rejects indicate that:
            the client may wish to simply retry the request
            with a new encrypted response, without reprompting the user for a
            new username and password. i.e., retry build_digest_header
        """
        super(HTTPProxyDigestAuth, self).__init__(*args, **kwargs)
        self.stale_rejects = 0

    def handle_407(self, r, **kwargs):
        """Handle HTTP 407 only once, otherwise give up

        Args:
            r: current response

        Returns:
            responses, along with the new response
        """
        if r.status_code == 407 and self.stale_rejects < 2:
            pat = re.compile(r'digest ', flags=re.IGNORECASE)
            if not "proxy-authenticate" in r.headers:
                raise IOError("proxy server violated RFC 7235:"
                    "407 response MUST contain header proxy-authenticate")
            self.chal = parse_dict_header(
                pat.sub('', r.headers['proxy-authenticate'], count=1))

            # if we present the user/passwd and still get rejected
            # http://tools.ietf.org/html/rfc2617#section-3.2.1
            if 'Proxy-Authorization' in r.request.headers and\
                'stale' in self.chal:
                if self.chal['stale'].lower() == 'true': # try again
                    self.stale_rejects += 1
                elif self.chal['stale'].lower() == 'false': # wrong user/passwd
                    raise IOError("User or password is invalid")

            # Consume content and release the original connection
            # to allow our new request to reuse the same one.
            r.content
            r.close()
            prep = r.request.copy()
            extract_cookies_to_jar(prep._cookies, r.request, r.raw)
            prep.prepare_cookies(prep._cookies)

            prep.headers['Proxy-Authorization'] = self.build_digest_header(
                prep.method, prep.url)
            _r = r.connection.send(prep, **kwargs)
            _r.history.append(r)
            _r.request = prep

            return _r
        else: # give up authenticate
            return r

    def __call__(self, r):
        # if we have nonce, then just use it, otherwise server will tell us
        if self.last_nonce:
            r.headers['Proxy-Authorization'] =\
                self.build_digest_header(r.method, r.url)
        r.register_hook('response', self.handle_407)
        return r
