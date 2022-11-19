.. _receiving-and-handling-data:

Receiving and Handling Multipart Data
=====================================

If you need, on occasion, to build a service to receive and handle ``multipart/form-data``, 
such as an endpoint to receive data from an HTML form submission, the requests_toolbelt 
package offers the capability of decoding the inbound :class:`bytes` data into a python
:class:`dict`. This capability is provided by the :class:`requests_toolbelt.multipart.MultipartDecoder`

MultipartDecoder
----------------

Parses the multipart payload of a bytestring into a tuple of ``Response``-like ``BodyPart`` objects.
The basic usage is::

.. code-block:: python
        from requests_toolbelt import MultipartDecoder

        decoder = MultipartDecoder(content, content_type)
        for part in decoder.parts:
            print(part.headers['content-type'])

If the multipart content is from a response, there's the option of using the ``from_response`` class method:

.. code-block:: python
        import requests
        from requests_toolbelt import MultipartDecoder

        response = requests.get(url)
        decoder = MultipartDecoder.from_response(response)
        for part in decoder.parts:
            print(part.headers['content-type'])

For both these usages, there is an optional ``encoding`` parameter. This is
a string, which is the name of the unicode codec to use (default is
``'utf-8'``.

.. autoclass:: requests_toolbelt.multipart.encoder.MultipartDecoder
    