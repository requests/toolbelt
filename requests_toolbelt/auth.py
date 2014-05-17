# -*- coding: utf-8 -*-
"""

requests_toolbelt.auth
======================

Various utilities around authentication.

"""

from requests.auth import HTTPDigestAuth, HTTPBasicAuth, AuthBase
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
