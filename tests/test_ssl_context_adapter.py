# -*- coding: utf-8 -*-
"""Tests for the SSLContextAdapter."""

import pickle
from ssl import SSLContext, PROTOCOL_TLS

import mock
from requests.adapters import HTTPAdapter
from requests_toolbelt.adapters.ssl_context import SSLContextAdapter


@mock.patch.object(HTTPAdapter, 'init_poolmanager')
def test_ssl_context_arg_is_passed(init_poolmanager):
    ssl_context = SSLContext(PROTOCOL_TLS)
    SSLContextAdapter(
        pool_connections=10,
        pool_maxsize=5,
        max_retries=0,
        pool_block=True,
        ssl_context=ssl_context
    )
    init_poolmanager.assert_called_once_with(
        10, 5, block=True, ssl_context=ssl_context
    )


def test_adapter_has_ssl_context_attr():
    ssl_context = SSLContext(PROTOCOL_TLS)
    adapter = SSLContextAdapter(ssl_context=ssl_context)

    assert adapter.ssl_context is ssl_context


def test_adapter_loses_ssl_context_after_pickling():
    ssl_context = SSLContext(PROTOCOL_TLS)
    adapter = SSLContextAdapter(ssl_context=ssl_context)
    adapter = pickle.loads(pickle.dumps(adapter))

    assert adapter.ssl_context is None
