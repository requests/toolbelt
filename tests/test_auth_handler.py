from requests.auth import HTTPBasicAuth
from requests_toolbelt.auth_handler import AuthHandler
from requests_toolbelt.auth_handler import NullAuthStrategy


def test_turns_tuples_into_basic_auth():
    a = AuthHandler({'example.com': ('foo', 'bar')})
    strategy = a.get_strategy_for('http://example.com')
    assert not isinstance(strategy, NullAuthStrategy)
    assert isinstance(strategy, HTTPBasicAuth)


def test_uses_null_strategy_for_non_matching_domains():
    a = AuthHandler({'api.example.com': ('foo', 'bar')})
    strategy = a.get_strategy_for('http://example.com')
    assert isinstance(strategy, NullAuthStrategy)


def test_normalizes_domain_keys():
    a = AuthHandler({'API.github.COM': ('foo', 'bar')})
    assert 'api.github.com' in a.strategies
    assert 'API.github.COM' not in a.strategies


def test_can_add_new_strategies():
    a = AuthHandler({'example.com': ('foo', 'bar')})
    a.add_strategy('api.github.com', ('fiz', 'baz'))
    assert isinstance(
        a.get_strategy_for('https://api.github.com'),
        HTTPBasicAuth
        )
