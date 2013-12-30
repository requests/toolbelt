import unittest
from mock import patch
from requests_toolbelt import user_agent
from requests_toolbelt.user_agent import _implementation_string


class TestUserAgent(unittest.TestCase):
    def test_user_agent_provides_package_name(self):
        assert "my-package" in user_agent("my-package", "0.0.1")

    def test_user_agent_provides_package_version(self):
        assert "0.0.1" in user_agent("my-package", "0.0.1")


class TestImplementationString(unittest.TestCase):
    @patch('platform.python_implementation')
    @patch('platform.python_version')
    def test_cpython_implementation(self, mock_version, mock_implementation):
        mock_implementation.return_value = 'CPython'
        mock_version.return_value = '2.7.5'
        assert 'CPython/2.7.5' == _implementation_string()
