requests toolbelt
=================

This is just a collection of utilities for `python-requests`_, but don't 
really belong in ``requests`` proper. The minimum tested requests version is 
``2.1.0``. In reality, the toolbelt should work with ``2.0.1`` as well, but 
some idiosyncracies prevent effective or sane testing on that version.

``pip install requests-toolbelt`` to get started!


multipart/form-data Encoder
---------------------------

The main attraction is a streaming multipart form-data object, ``MultipartEncoder``.
Its API looks like this:

.. code-block:: python

    from requests_toolbelt import MultipartEncoder
    import requests

    m = MultipartEncoder(
        fields={'field0': 'value', 'field1': 'value',
                'field2': ('filename', open('file.py', 'rb'), 'text/plain')}
        )

    r = requests.post('http://httpbin.org/post', data=m,
                      headers={'Content-Type': m.content_type})


You can also use ``multipart/form-data`` encoding for requests that don't
require files:

.. code-block:: python

    from requests_toolbelt import MultipartEncoder
    import requests

    m = MultipartEncoder(fields={'field0': 'value', 'field1': 'value'})

    r = requests.post('http://httpbin.org/post', data=m,
                      headers={'Content-Type': m.content_type})


Or, you can just create the string and examine the data:

.. code-block:: python

    # Assuming `m` is one of the above
    m.to_string()  # Always returns unicode


User-Agent constructor
----------------------

You can easily construct a requests-style ``User-Agent`` string::

    from requests_toolbelt import user_agent

    headers = {
        'User-Agent': user_agent('my_package', '0.0.1')
        }

    r = requests.get('https://api.github.com/users', headers=headers)


SSLAdapter
----------

The ``SSLAdapter`` was originally published on `Cory Benfield's blog`_. 
This adapter allows the user to choose one of the SSL protocols made available 
in Python's ``ssl`` module for outgoing HTTPS connections:

.. code-block:: python

    from requests_toolbelt import SSLAdapter
    import requests
    import ssl

    s = requests.Session()
    s.mount('https://', SSLAdapter(ssl.PROTOCOL_TLSv1))

cookies/ForgetfulCookieJar
--------------------------

The ``ForgetfulCookieJar`` prevents a particular requests session from storing 
cookies:

.. code-block:: python

    from requests-toolbelt.cookies import ForgetfulCookieJar

    session = requests.Session()
    session.cookies = ForgetfulCookieJar()

Known Issues
------------

On Python 3.3.0 and 3.3.1, the standard library's ``http`` module will fail
when passing an instance of the ``MultipartEncoder``. This is fixed in later
minor releases of Python 3.3. Please consider upgrading to a later minor
version or Python 3.4. *There is absolutely nothing this library can do to
work around that bug.*

Contributing
------------

Please read the `suggested workflow
<https://toolbelt.readthedocs.org/en/latest/contributing.html>`_ for
contributing to this project.

.. _Cory Benfield's blog: https://lukasa.co.uk/2013/01/Choosing_SSL_Version_In_Requests/
.. _python-requests: https://github.com/kennethreitz/requests
