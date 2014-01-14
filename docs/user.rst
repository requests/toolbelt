.. _user:

User Guide
==========

The ``requests-toolbelt`` contains a number of unrelated tools and utilities
for helping with use-cases that are not directly supported by the core
``requests`` library. This section of the documentation contains descriptions
of the various utilities included in the toolbelt, and how to use them.

Streaming Multipart Data Encoder
--------------------------------

Requests has `support for multipart uploads`_, but the API means that using
that functionality to build exactly the Multipart upload you want can be
difficult or impossible. Additionally, when using Requests' Multipart upload
functionality all the data must be read into memory before being sent to the
server. In extreme cases, this can make it impossible to send a file as part of
a ``multipart/form-data`` upload.

The toolbelt contains a class that allows you to build multipart request bodies
in exactly the format you need, and to avoid reading files into memory. An
example of how to use it is like this:

::

    from requests_toolbelt import MultipartEncoder
    import requests

    m = MultipartEncoder(
        fields={'field0': 'value', 'field1': 'value',
                'field2': ('filename', open('file.py'), 'text/plain')}
        )

    r = requests.post('http://httpbin.org/post', data=m,
                      headers={'Content-Type': m.content_type})

The ``MultipartEncoder`` has the ``.to_string()`` convenience method, as well.
This method renders the multipart body into a string. This is useful when
developing your code, allowing you to confirm that the multipart body has the
form you expect before you send it on.

.. _support for multipart uploads: http://docs.python-requests.org/en/latest/user/quickstart/#post-a-multipart-encoded-file


User-Agent Constructor
----------------------

Having well-formed user-agent strings is important for the proper functioning
of the web. Make server administators happy by generating yourself a nice
user-agent string, just like Requests does! The output of the user-agent
generator looks like this::

    >>> import requests_toolbelt
    >>> requests_toolbelt.user_agent('mypackage', '0.0.1')
    'mypackage/0.0.1 CPython/2.7.5 Darwin/13.0.0'

The Python type and version, and the platform type and version, will accurately
reflect the system that your program is running on. You can drop this easily
into your program like this::

    from requests_toolbelt import user_agent
    from requests import Session

    s = Session()
    s.headers = {
        'User-Agent': user_agent('my_package', '0.0.1')
        }

    r = s.get('https://api.github.com/users')

This will override the default Requests user-agent string for all of your HTTP
requests, replacing it with your own.
