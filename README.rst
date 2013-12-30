requests toolbelt
=================

This is just a collection of utilities that some users of python-requests
might need but do not belong in requests proper.

multipart/form-data Encoder
---------------------------

The main attraction is a streaming multipart form-data object. Its API looks
like:

.. code::

    from requests_toolbelt import MultipartEncoder

    import requests


    m = MultipartEncoder(
        fields={'field0': 'value', 'field1': 'value',
                'field2': ('filename', open('file.py'), 'text/plain')}
        )

    r = requests.post('http://httpbin.org/post', data=m,
                      headers={'Content-Type': m.content_type})

You can also use it to just plain use ``multipart/form-data`` encoding for
requests that do not require files

.. code::

    from requests_toolbelt import MultipartEncoder

    import requests


    m = MultipartEncoder(fields={'field0': 'value', 'field1': 'value'})

    r = requests.post('http://httpbin.org/post', data=m,
                      headers={'Content-Type': m.content_type})


You can also just use it to create the string to examine the data

.. code::

    # Assuming `m` is one of the above

    m.to_string()  # Always returns unicode


User-Agent constructor
----------------------

.. code::

    from requests_toolbelt import user_agent

    headers = {
        'User-Agent': user_agent('my_package', '0.0.1')
        }

    r = requests.get('https://api.github.com/users', headers=headers)
