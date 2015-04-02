"""Module containing the tests for requests_toolbelt.threaded.pool."""
import queue
import unittest

import mock
import pytest

from requests_toolbelt.threaded import pool
from requests_toolbelt.threaded import thread


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

    def test_from_exceptions_populates_a_queue(self):
        """Ensure a Queue is properly populated from exceptions."""
        urls = ["https://httpbin.org/get?n={0}".format(n) for n in range(5)]
        Exc = pool.ThreadException
        excs = (Exc({'method': 'GET', 'url': url}, None) for url in urls)

        job_queue = mock.MagicMock()
        with mock.patch.object(queue, 'Queue', return_value=job_queue):
            with mock.patch.object(thread, 'SessionThread'):
                pool.Pool.from_exceptions(excs)

        assert job_queue.put.call_count == 5
        assert job_queue.put.mock_calls == [
            mock.call({'method': 'GET', 'url': url})
            for url in urls
        ]

    def test_from_urls_constructs_get_requests(self):
        """Ensure a Queue is properly populated from an iterable of urls."""
        urls = ["https://httpbin.org/get?n={0}".format(n) for n in range(5)]

        job_queue = mock.MagicMock()
        with mock.patch.object(queue, 'Queue', return_value=job_queue):
            with mock.patch.object(thread, 'SessionThread'):
                pool.Pool.from_urls(urls)

        assert job_queue.put.call_count == 5
        assert job_queue.put.mock_calls == [
            mock.call({'method': 'GET', 'url': url})
            for url in urls
        ]

    def test_from_urls_constructs_get_requests_with_kwargs(self):
        """Ensure a Queue is properly populated from an iterable of urls."""
        def merge(*args):
            final = {}
            for d in args:
                final.update(d)
            return final

        urls = ["https://httpbin.org/get?n={0}".format(n) for n in range(5)]

        kwargs = {'stream': True, 'headers': {'Accept': 'application/json'}}
        job_queue = mock.MagicMock()
        with mock.patch.object(queue, 'Queue', return_value=job_queue):
            with mock.patch.object(thread, 'SessionThread'):
                pool.Pool.from_urls(urls, kwargs)

        assert job_queue.put.call_count == 5
        assert job_queue.put.mock_calls == [
            mock.call(merge({'method': 'GET', 'url': url}, kwargs))
            for url in urls
        ]

    def test_join_all(self):
        """Ensure that all threads are joined properly."""
        session_threads = []

        def _side_effect(*args, **kwargs):
            thread = mock.MagicMock()
            session_threads.append(thread)
            return thread

        with mock.patch.object(thread, 'SessionThread',
                               side_effect=_side_effect):
            pool.Pool(None).join_all()

        for st in session_threads:
            st.join.assert_called_once_with()
