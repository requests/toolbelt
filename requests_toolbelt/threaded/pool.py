"""Module that provides the thread pool for ``requests_toolbelt.threaded``."""
import os

import requests

from . import thread


class Pool(object):
    """Pool that manages the threads containing sessions.

    .. todo:: Document format for a queue

    :param queue: The queue you're expected to use to which you should add
        items.
    :type queue: queue.Queue
    :param initializer:
    :type initializer: collections.Callable
    :param auth_generator:
    :type auth_generator: collections.Callable
    :param int num_processes:
    :param session:
    :type session: requests.Session
    """

    def __init__(self, queue, initializer=None, auth_generator=None,
                 num_processes=None, session=requests.Session):
        if num_processes is None:
            num_processes = os.cpu_count() or 1

        if num_processes < 1:
            raise ValueError("Number of processes should at least be 1.")

        self._queue = queue
        self._processes = num_processes
        self._initializer = initializer or initializer_identity
        self._auth = auth_generator or identity
        self._pool = [
            thread.SessionThread(self._new_session(), self.queue)
            for _ in range(self.processes)
        ]
        self._session = session

    def _new_session(self):
        return self._initializer(self._session(), self._auth)


def identity(session_obj):
    return session_obj


def initializer_identity(session_obj, auth_generator):
    return auth_generator(session_obj)
