import pickle

import pytest
import requests
from requests.adapters import HTTPAdapter

from requests_toolbelt.adapters.host_header_ssl import HostHeaderSSLAdapter


@pytest.mark.parametrize('strip', [False, True])
def test_custom_header_controls_tls_without_changing_host(monkeypatch, strip):
    adapter = HostHeaderSSLAdapter(use_header='X-TLS-Host', strip_header=strip)
    request = requests.Request('GET', 'https://192.0.2.1:8443/', headers={
        'Host': '192.0.2.1:8443', 'x-tls-host': 'example.org'}).prepare()
    observed = {}

    def send(self, sent_request, **kwargs):
        observed.update(self.poolmanager.connection_pool_kw)
        assert sent_request.url == 'https://192.0.2.1:8443/'
        assert sent_request.headers['Host'] == '192.0.2.1:8443'
        assert ('x-tls-host' in sent_request.headers) is not strip
        return 'response'

    monkeypatch.setattr(HTTPAdapter, 'send', send)
    assert adapter.send(request) == 'response'
    assert observed['assert_hostname'] == 'example.org'
    assert observed['server_hostname'] == 'example.org'


def test_missing_custom_header_clears_previous_tls_override(monkeypatch):
    adapter = HostHeaderSSLAdapter(use_header='X-TLS-Host')
    monkeypatch.setattr(HTTPAdapter, 'send', lambda *args, **kwargs: None)
    first = requests.Request('GET', 'https://192.0.2.1/', headers={
        'X-TLS-Host': 'example.org'}).prepare()
    second = requests.Request('GET', 'https://192.0.2.2/', headers={
        'Host': 'other.example.org'}).prepare()
    adapter.send(first)
    adapter.send(second)
    assert 'assert_hostname' not in adapter.poolmanager.connection_pool_kw
    assert 'server_hostname' not in adapter.poolmanager.connection_pool_kw


def test_default_host_behavior_is_preserved(monkeypatch):
    adapter = HostHeaderSSLAdapter()
    monkeypatch.setattr(HTTPAdapter, 'send', lambda *args, **kwargs: None)
    request = requests.Request('GET', 'https://192.0.2.1/', headers={
        'Host': 'example.org'}).prepare()
    adapter.send(request)
    assert (adapter.poolmanager.connection_pool_kw['assert_hostname'] ==
            'example.org')
    assert request.headers['Host'] == 'example.org'


def test_header_options_survive_pickling():
    adapter = HostHeaderSSLAdapter(use_header='X-TLS-Host', strip_header=True)
    restored = pickle.loads(pickle.dumps(adapter))
    assert restored.use_header == 'X-TLS-Host'
    assert restored.strip_header is True
