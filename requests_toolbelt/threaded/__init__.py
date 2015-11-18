"""
This module provides the API for ``requests_toolbelt.threaded``.

The module provides a clean and simple API for making requests via a thread
pool. The thread pool will use sessions for increased performance.

A simple use-case is:

.. code-block:: python

    from requests_toolbelt import threaded

    urls_to_get = [{
        'url': 'https://api.github.com/users/sigmavirus24',
        'method': 'GET',
    }, {
        'url': 'https://api.github.com/repos/sigmavirus24/requests-toolbelt',
        'method': 'GET',
    }, {
        'url': 'https://google.com',
        'method': 'GET',
    }]
    responses, errors = threaded.map(urls_to_get)

By default, the threaded submodule will detect the number of CPUs your
computer has and use that if no other number of processes is selected. To
change this, always use the keyword argument ``num_processes``. Using the
above example, we would expand it like so:

.. code-block:: python

    responses, errors = threaded.map(urls_to_get, num_processes=10)

You can also customize how a :class:`requests.Session` is initialized by
creating a callback function:

.. code-block:: python

    from requests_toolbelt import user_agent

    def initialize_session(session):
        session.headers['User-Agent'] = user_agent('my-scraper', '0.1')
        session.headers['Accept'] = 'application/json'

    responses, errors = threaded.map(urls_to_get,
                                     initializer=initialize_session)

Inspiration is blatantly drawn from the standard library's multiprocessing
library. See the following references:

- multiprocessing's `pool source`_

- map and map_async `inspiration`_

.. _pool source:
    https://hg.python.org/cpython/file/8ef4f75a8018/Lib/multiprocessing/pool.py
.. _inspiration:
    https://hg.python.org/cpython/file/8ef4f75a8018/Lib/multiprocessing/pool.py#l340
"""
from . import pool
from .._compat import queue


def map(requests, **kwargs):
    if not all(isinstance(r, dict) for r in requests):
        raise ValueError('map expects a list of dictionaries.')

    # Build our queue of requests
    job_queue = queue.Queue()
    for request in requests:
        job_queue.put(request)

    threadpool = pool.Pool(
        job_queue=job_queue,
        **kwargs
    )
    threadpool.join_all()
    return threadpool.responses(), threadpool.exceptions()
