# -*- coding: utf-8 -*-
from requests.adapters import DEFAULT_POOLSIZE, DEFAULT_POOLBLOCK
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from requests_toolbelt.adapters.source import SourceAddressAdapter

import pytest


@patch('requests_toolbelt.adapters.source.poolmanager')
def test_source_address_adapter_string(poolmanager):
    SourceAddressAdapter('10.10.10.10')

    poolmanager.PoolManager.assert_called_once_with(
        num_pools=DEFAULT_POOLSIZE,
        maxsize=DEFAULT_POOLSIZE,
        block=DEFAULT_POOLBLOCK,
        source_address=('10.10.10.10', 0)
    )


@patch('requests_toolbelt.adapters.source.poolmanager')
def test_source_address_adapter_tuple(poolmanager):
    SourceAddressAdapter(('10.10.10.10', 80))

    poolmanager.PoolManager.assert_called_once_with(
        num_pools=DEFAULT_POOLSIZE,
        maxsize=DEFAULT_POOLSIZE,
        block=DEFAULT_POOLBLOCK,
        source_address=('10.10.10.10', 80)
    )


@patch('requests_toolbelt.adapters.source.poolmanager')
def test_source_address_adapter_type_error(poolmanager):
    with pytest.raises(TypeError):
        SourceAddressAdapter({'10.10.10.10': 80})

    assert not poolmanager.PoolManager.called


@pytest.mark.parametrize('address', ['127.0.0.1', ('127.0.0.1', 45678)])
@pytest.mark.parametrize('protocol', [0, 2])
@pytest.mark.parametrize('session', [False, True])
def test_source_address_pickle(address, protocol, session):
    import pickle
    import requests

    original = SourceAddressAdapter(
        address, pool_connections=3, pool_maxsize=7, pool_block=True,
        max_retries=2)
    if session:
        value = requests.Session()
        value.mount('http://', original)
        value.mount('https://', original)
    else:
        value = original

    restored = pickle.loads(pickle.dumps(value, protocol=protocol))
    adapter = restored.get_adapter('http://') if session else restored
    assert adapter is not original
    expected = address if isinstance(address, tuple) else (address, 0)
    assert adapter.source_address == expected
    assert adapter._pool_connections == 3
    assert adapter._pool_maxsize == 7
    assert adapter._pool_block is True
    assert adapter.max_retries.total == 2
    assert adapter.poolmanager.connection_pool_kw['source_address'] == expected
    assert adapter.poolmanager is not original.poolmanager
    if session:
        assert restored.get_adapter('https://') is adapter

    proxy = adapter.proxy_manager_for('http://localhost:8080')
    assert proxy.connection_pool_kw['source_address'] == expected
    restored.close()
    value.close()


@pytest.mark.parametrize('address', ['127.0.0.1', ('127.0.0.1', 0)])
def test_pickled_session_binds_source_address(address):
    import pickle
    import threading
    import requests
    try:
        from http.server import BaseHTTPRequestHandler, HTTPServer
    except ImportError:
        from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

    clients = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            clients.append(self.client_address[0])
            self.send_response(200)
            self.send_header('Content-Length', '2')
            self.end_headers()
            self.wfile.write(b'ok')

        def log_message(self, *args):
            pass

    server = HTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever)
    worker.daemon = True
    worker.start()
    original = requests.Session()
    original.trust_env = False
    original.mount('http://', SourceAddressAdapter(address))
    restored = None
    try:
        restored = pickle.loads(pickle.dumps(original, protocol=2))
        response = restored.get('http://127.0.0.1:{}/'.format(
            server.server_address[1]), timeout=3)
        assert response.status_code == 200
        assert response.content == b'ok'
        assert clients == ['127.0.0.1']
    finally:
        if restored is not None:
            restored.close()
        original.close()
        server.shutdown()
        server.server_close()
        worker.join(3)
    assert not worker.is_alive()
