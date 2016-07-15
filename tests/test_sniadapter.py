import unittest
import requests

from requests_toolbelt import SNIAdapter


class TestSNIAdapter(unittest.TestCase):

    def setUp(self):
        self.session = requests.Session()
        self.session.mount("https://", SNIAdapter())

    def test_sniadapter(self):
        # normal mode
        r = self.session.get("https://example.org")
        assert r.status_code == 200

        # accessing IP address directly
        r = self.session.get("https://93.184.216.34",
                             headers={"Host": "example.org"})
        assert r.status_code == 200

        # vHost
        r = self.session.get("https://93.184.216.34",
                             headers={"Host": "example.com"})
        assert r.status_code == 200

    def test_stream(self):
        self.session.get("https://54.175.219.8/stream/20",
                         headers={"Host": "httpbin.org"},
                         stream=True)

    def test_case_insensitive_header(self):
        r = self.session.get("https://93.184.216.34",
                             headers={"hOSt": "example.org"})
        assert r.status_code == 200

    def test_plain_requests(self):
        # test whether the reason for this adapter remains
        # (may be implemented into requests in the future)
        with self.assertRaises(requests.exceptions.SSLError):
            requests.get(url="https://93.184.216.34",
                         headers={"Host": "example.org"})

if __name__ == '__main__':
    unittest.main()
