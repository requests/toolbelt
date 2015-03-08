"""Module that provides the thread pool for ``requests_toolbelt.threaded``."""
import multiprocessing
try:
    import queue  # Python 3
except ImportError:
    import Queue as queue

import requests

from . import thread


class Pool(object):
    """Pool that manages the threads containing sessions.

    .. todo:: Document format for a queue

    :param queue:
        The queue you're expected to use to which you should add items.
    :type queue: queue.Queue
    :param initializer:
        Function used to initialize an instance of ``session``.
    :type initializer: collections.Callable
    :param auth_generator:
        Function used to generate new auth credentials for the session.
    :type auth_generator: collections.Callable
    :param int num_threads:
        Number of threads to create.
    :param session:
    :type session: requests.Session
    """

    def __init__(self, job_queue, initializer=None, auth_generator=None,
                 num_processes=None, session=requests.Session):
        if num_processes is None:
            num_processes = multiprocessing.cpu_count() or 1

        if num_processes < 1:
            raise ValueError("Number of processes should at least be 1.")

        self._job_queue = job_queue
        self._response_queue = queue.Queue()
        self._exc_queue = queue.Queue()
        self._processes = num_processes
        self._initializer = initializer or _identity
        self._auth = auth_generator or _identity
        self._session = session
        self._pool = [
            thread.SessionThread(self._new_session(), self._job_queue,
                                 self._response_queue, self._exc_queue)
            for _ in range(self._processes)
        ]

    def _new_session(self):
        return self._auth(self._initializer(self._session()))

    def exceptions(self):
        """Iterate over all the exceptions in the pool.

        :returns: Generator of :class:`~ThreadException`
        """
        while True:
            exc = self.get_exception()
            if exc is None:
                break
            yield exc

    def get_exception(self):
        """Get an exception from the pool.

        :rtype: :class:`~ThreadException`
        """
        try:
            return ThreadException.from_queue(
                self._exc_queue.get_nowait()
            )
        except queue.Empty:
            return None

    def get_response(self):
        """Get a response from the pool.

        :rtype: :class:`~ThreadResponse`
        """
        try:
            return ThreadResponse.from_queue(
                self._response_queue.get_nowait()
            )
        except queue.Empty:
            return None

    def responses(self):
        """Iterate over all the responses in the pool.

        :returns: Generator of :class:`~ThreadResponse`
        """
        while True:
            resp = self.get_response()
            if resp is None:
                break
            yield resp

    def join_all(self):
        """Join all the threads to the master thread."""
        for session_thread in self._pool:
            session_thread.join()


class ThreadProxy(object):
    proxied_attr = None

    def __getattr__(self, attr):
        """Proxy attribute accesses to the proxied object."""
        get = object.__getattribute__
        if attr not in self.attrs:
            response = get(self, self.proxied_attr)
            return getattr(response, attr)
        else:
            return get(self, attr)

    @classmethod
    def from_queue(cls, qtuple):
        """Create an instance of ``cls`` from a queue result."""
        request_kwargs, proxied_obj = qtuple
        return cls(request_kwargs, proxied_obj)


class ThreadResponse(ThreadProxy):
    proxied_attr = 'response'
    attrs = frozenset(['request_kwargs', 'response'])

    def __init__(self, request_kwargs, response):
        self.request_kwargs = request_kwargs
        self.response = response


class ThreadException(ThreadProxy):
    proxied_attr = 'exception'
    attrs = frozenset(['request_kwargs', 'exception'])

    def __init__(self, request_kwargs, exception):
        self.request_kwargs = request_kwargs
        self.exception = exception


def _identity(session_obj):
    return session_obj
