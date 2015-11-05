"""The module containing the code for ForgetfulCookieJar."""
import requests
from requests.cookies import RequestsCookieJar


class ForgetfulCookieJar(RequestsCookieJar):
    def set_cookie(self, *args, **kwargs):
        return
