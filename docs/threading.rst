.. _threading:

Using requests with Threading
=============================

.. versionadded:: 0.4.0

The toolbelt provides a simple API for using requests with threading.

A requests Session is documented as threadsafe but there are still a couple
corner cases where it isn't perfectly threadsafe. The best way to use a
Session is to use one per thread.

The implementation provided by the toolbelt is naïve. This means that we use
one session per thread and we make no effort to synchronize attributes (e.g.,
authentication, cookies, etc.). It also means that we make no attempt to
direct a request to a session that has already handled a request to the same
domain. In other words, if you're making requests to multiple domains, the
toolbelt's Pool will not try to send requests to the same domain to the same
thread.

This module provides three classes:

- :class:`~requests_toolbelt.threaded.pool.Pool`
- :class:`~requests_toolbelt.threaded.pool.ThreadResponse`
- :class:`~requests_toolbelt.threaded.pool.ThreadException`

In 98% of the situations you'll want to just use a
:class:`~requests_toolbelt.threaded.pool.Pool` and you'll treat a
:class:`~requests_toolbelt.threaded.pool.ThreadResponse` as if it were a
regular :class:`requests.Response`.

Here's an example:

.. code-block:: python

    # This example assumes Python 3
    import queue
    from requests_toolbelt.threaded import pool

    jobs = queue.Queue()
    urls = [
        # My list of URLs to get
    ]

    for url in urls:
        queue.put({'method': 'GET', 'url': url})

    p = pool.Pool(job_queue=q)
    p.join_all()

    for response in p.responses():
        print('GET {0}. Returned {1}.'.format(response.request_kwargs['url'],
                                              response.status_code))

This is clearly a bit underwhelming. This is why there's a short-cut class
method to create a :class:`~requests_toolbelt.threaded.pool.Pool` from a list
of URLs.

.. code-block:: python

    from requests_toolbelt.threaded import pool

    urls = [
        # My list of URLs to get
    ]

    p = pool.Pool.from_urls(urls)
    p.join_all()

    for response in p.responses():
        print('GET {0}. Returned {1}.'.format(response.request_kwargs['url'],
                                              response.status_code))

If one of the URLs in your list throws an exception, it will be accessible
from the :meth:`~Pool.exceptions` generator.

.. code-block:: python

    from requests_toolbelt.threaded import pool

    urls = [
        # My list of URLs to get
    ]

    p = pool.Pool.from_urls(urls)
    p.join_all()

    for exc in p.exceptions():
        print('GET {0}. Raised {1}.'.format(exc.request_kwargs['url'],
                                            exc.message))

If instead, you want to retry the exceptions that have been raised you can do
the following:

.. code-block:: python

    from requests_toolbelt.threaded import pool

    urls = [
        # My list of URLs to get
    ]

    p = pool.Pool.from_urls(urls)
    p.join_all()

    new_pool = pool.Pool.from_exceptions(p.exceptions())
    new_pool.join_all()

Not all requests are advisable to retry without checking if they should be
retried. You would normally check if you want to retry it.

The :class:`~Pool` object takes 4 other keyword arguments:

- ``initializer``

  This is a callback that will initialize things on every session created. The
  callback must return the session.

- ``auth_generator``

  This is a callback that is called *after* the initializer callback has
  modified the session. This callback must also return the session.

- ``num_processes``

  By passing a positive integer that indicates how many threads to use. It is
  ``None`` by default, and will use the result of
  ``multiproccessing.cpu_count()``.

- ``session``

  You can pass an alternative constructor or any callable that returns a
  :class:`requests.Sesssion` like object. It will not be passed any arguments
  because a :class:`requests.Session` does not accept any arguments.

Finally, if you don't want to worry about Queue or Pool management, you can
try the following:

.. code-block:: python

    from requests_toolbelt import threaded

    requests = [{
        'method': 'GET',
        'url': 'https://httpbin.org/get',
        # ...
    }, {
        # ...
    }, {
        # ...
    }]

    responses_generator, exceptions_generator = threaded.map(requests)
    for response in responses_generator:
       # Do something

API and Module Auto-Generated Documentation
-------------------------------------------

.. automodule:: requests_toolbelt.threaded

.. autoclass:: requests_toolbelt.threaded.pool.Pool
    :members:

.. autoclass:: requests_toolbelt.threaded.pool.ThreadResponse
    :members:

.. autoclass:: requests_toolbelt.threaded.pool.ThreadException
    :members:
