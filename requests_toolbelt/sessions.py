import requests

from ._compat import urljoin


class Based:
    """
    Mix-in for a requests Session where the URL may be relative to
    a base for the session.

    Based on implementation at
    from https://github.com/kennethreitz/requests/issues/2554#issuecomment-109341010
    """

    base_url = None

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        return super(Based, self).request(method, url, *args, **kwargs)


class BasedSession(Based, requests.Session):
    def __init__(self, base_url=None):
        if base_url:
            self.base_url = base_url
        super(BasedSession, self).__init__()
