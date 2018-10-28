# -*- coding: utf-8 -*-
"""Tests for the SSLContextAdapter."""

import pickle
from ssl import SSLContext, PROTOCOL_TLSv1

import mock
import pytest
import requests
from requests.adapters import HTTPAdapter
from requests_toolbelt.adapters.ssl_context import SSLContextAdapter


@pytest.mark.skipif(requests.__build__ < 0x020400,
                    reason="Test case for newer requests versions.")
@mock.patch.object(HTTPAdapter, 'init_poolmanager')
def test_ssl_context_arg_is_passed_on_newer_requests(init_poolmanager):
    ssl_context = SSLContext(PROTOCOL_TLSv1)
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


@pytest.mark.skipif(requests.__build__ >= 0x020400,
                    reason="Test case for older requests versions.")
@mock.patch.object(HTTPAdapter, 'init_poolmanager')
def test_ssl_context_arg_is_not_passed_on_older_requests(init_poolmanager):
    ssl_context = SSLContext(PROTOCOL_TLSv1)
    SSLContextAdapter(
        pool_connections=10,
        pool_maxsize=5,
        max_retries=0,
        pool_block=True,
        ssl_context=ssl_context
    )
    init_poolmanager.assert_called_once_with(
        10, 5, block=True
    )


def test_adapter_has_ssl_context_attr():
    ssl_context = SSLContext(PROTOCOL_TLSv1)
    adapter = SSLContextAdapter(ssl_context=ssl_context)

    assert adapter.ssl_context is ssl_context


def test_adapter_loses_ssl_context_after_pickling():
    ssl_context = SSLContext(PROTOCOL_TLSv1)
    adapter = SSLContextAdapter(ssl_context=ssl_context)
    adapter = pickle.loads(pickle.dumps(adapter))

    assert adapter.ssl_context is None
