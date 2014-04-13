requests toolbelt
=================

This is just a collection of utilities for `python-requests`_, 
but don't really belong in ``requests`` proper.

.. _python-requests: https://github.com/kennethreitz/requests


multipart/form-data Encoder
---------------------------

The main attraction is a streaming multipart form-data object, ``MultipartEncoder``.
Its API looks like this:

.. code-block:: python

    from requests_toolbelt import MultipartEncoder
    import requests

    m = MultipartEncoder(
        fields={'field0': 'value', 
                'field1': 'value',
                'field2': ('filename', open('file.py', 'rb'), 'text/plain')}
        )

    r = requests.post('http://httpbin.org/post', data=m,
                      headers={'Content-Type': m.content_type})


You can also simply use ``multipart/form-data`` encoding for requests that 
don't require files:

.. code-block:: python

    from requests_toolbelt import MultipartEncoder
    import requests

    m = MultipartEncoder(fields={'field0': 'value', 'field1': 'value'})

    r = requests.post('http://httpbin.org/post', data=m,
                      headers={'Content-Type': m.content_type})


Or, just create the string and examine the data:

.. code-block:: python

    # Assuming `m` is one of the above
    m.to_string()  # Always returns unicode


User-Agent constructor
----------------------

Easily construct a requests-style ``User-Agent`` string:

.. code-block:: python

    from requests_toolbelt import user_agent

    headers = { 'User-Agent': user_agent('my_package', '0.0.1') }

    r = requests.get('https://api.github.com/users', headers=headers)


SSLAdapter
----------

The ``SSLAdapter`` is an implementation of `an adaptor proposed by @Lukasa`_. This adapter allows the user to choose one of the SSL
protocols made available in Python's ``ssl`` module for outgoing HTTPS
connections:

.. code-block:: python

    from requests_toolbelt import SSLAdapter
    import requests
    import ssl

    s = requests.Session()
    s.mount('https://', SSLAdapter(ssl.PROTOCOL_TLSv1))

.. _an adaptor proposed by @Lukasa: https://lukasa.co.uk/2013/01/Choosing_SSL_Version_In_Requests/
