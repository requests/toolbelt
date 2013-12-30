import unittest
from requests_toolbelt import user_agent


class TestUserAgent(unittest.TestCase):
    def test_user_agent_provides_package_name(self):
        assert "my-package" in user_agent("my-package", "0.0.1")

    def test_user_agent_provides_package_version(self):
        assert "0.0.1" in user_agent("my-package", "0.0.1")
