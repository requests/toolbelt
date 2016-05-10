import requests

from ._compat import urljoin


class Based(object):
    """
    Mix-in for a requests Session where the URL may be relative to
    a base for the session.

    Based on implementation at
    from https://github.com
    /kennethreitz/requests/issues/2554#issuecomment-109341010
    """

    base_url = None

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        return super(Based, self).request(method, url, *args, **kwargs)


class BasedSession(Based, requests.Session):
    """
    A requests.Session with Based mixed-in. Initialize with a
    base URL to resolve URLs relative to that base. e.g.

    >>> session = BasedSession('https://mysite.org/default/')

    Then, when making requests, relative URLs are accepted. To get
    ``https://mysite.org/default/bar/``:

    >>> resp = session.get('bar/')
    """
    def __init__(self, base_url=None):
        if base_url:
            self.base_url = base_url
        super(BasedSession, self).__init__()
