import pytest
import requests

from requests_toolbelt.adapters import host_header_ssl as hhssl


@pytest.fixture
def session():
    """Create a session with our adapter mounted."""
    s = requests.Session()
    s.mount('https://', hhssl.HostHeaderSSLAdapter())
    return s


# Let's not spam example.org:
@pytest.mark.skip
class TestHostHeaderSSLAdapter(object):
    """Tests for our HostHeaderSNIAdapter."""

    def test_ssladapter(self, session):
        # normal mode
        r = session.get('https://example.org')
        assert r.status_code == 200

        # accessing IP address directly
        r = session.get('https://93.184.216.34',
                        headers={"Host": "example.org"})
        assert r.status_code == 200

        # vHost
        r = session.get('https://93.184.216.34',
                        headers={'Host': 'example.com'})
        assert r.status_code == 200

    def test_stream(self, session):
        session.get('https://54.175.219.8/stream/20',
                    headers={'Host': 'httpbin.org'},
                    stream=True)

    def test_case_insensitive_header(self, session):
        r = session.get('https://93.184.216.34',
                        headers={'hOSt': 'example.org'})
        assert r.status_code == 200

    def test_case_header_with_port(self, session):
        r = session.get('https://93.184.216.34',
                        headers={'Host': 'example.org:443'})
        assert r.status_code == 200

    def test_plain_requests(self):
        # test whether the reason for this adapter remains
        # (may be implemented into requests in the future)
        with pytest.raises(requests.exceptions.SSLError):
            requests.get(url='https://93.184.216.34',
                         headers={'Host': 'example.org'})
