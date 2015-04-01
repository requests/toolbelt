"""Module containing the tests for requests_toolbelt.threaded.pool."""
import unittest

import mock
import pytest

from requests_toolbelt.threaded import pool


class TestPool(unittest.TestCase):

    """Collection of tests for requests_toolbelt.threaded.pool.Pool."""

    def test_requires_positive_number_of_processes(self):
        """Show that the number of processes has to be > 0."""
        with pytest.raises(ValueError):
            pool.Pool(None, num_processes=0)

        with pytest.raises(ValueError):
            pool.Pool(None, num_processes=-1)

    def test_number_of_processes_can_be_arbitrary(self):
        """Show that the number of processes can be set."""
        p = pool.Pool(None, num_processes=100)
        assert p._processes == 100
        assert len(p._pool) == 100

        p = pool.Pool(None, num_processes=1)
        assert p._processes == 1
        assert len(p._pool) == 1

    def test_initializer_is_called(self):
        """Ensure that the initializer function is called."""
        initializer = mock.MagicMock()
        pool.Pool(None, num_processes=1, initializer=initializer)
        assert initializer.called is True
        initializer.assert_called_once_with(mock.ANY)

    def test_auth_generator_is_called(self):
        """Ensure that the auth_generator function is called."""
        auth_generator = mock.MagicMock()
        pool.Pool(None, num_processes=1, auth_generator=auth_generator)
        assert auth_generator.called is True
        auth_generator.assert_called_once_with(mock.ANY)

    def test_session_is_called(self):
        """Ensure that the session function is called."""
        session = mock.MagicMock()
        pool.Pool(None, num_processes=1, session=session)
        assert session.called is True
        session.assert_called_once_with()
