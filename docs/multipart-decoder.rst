.. _multipart-decoder:

Decoding Multipart Responses
============================

Use :class:`~requests_toolbelt.multipart.decoder.MultipartDecoder` to split a
multipart response into individual body parts. Unlike the streaming multipart
encoder, the decoder reads the complete body into memory. Calling
``from_response()`` accesses ``response.content``, even if the request used
``stream=True``.

Decode a Requests response
--------------------------

Pass a Requests response whose ``Content-Type`` is multipart and includes the
boundary parameter:

.. code-block:: python

    import requests
    from requests_toolbelt import MultipartDecoder

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    decoder = MultipartDecoder.from_response(response)

    for part in decoder.parts:
        content_type = part.headers.get(b'Content-Type', b'')
        print(content_type, part.content)

``decoder.parts`` is a tuple of ``BodyPart`` objects in body order. Each part
has its own headers and content; these are separate from the headers of the
outer response. Part header names and values are **bytes**, and header lookup
is case-insensitive. Use byte keys such as ``b'Content-Type'`` rather than
``'Content-Type'``.

Decode an existing byte string
------------------------------

If the body comes from a file or another source, pass the raw bytes and the
complete content type directly. Keep the boundary parameter: the decoder uses
it to locate the parts.

This example needs no HTTP server and includes both text and binary content:

    >>> from requests_toolbelt import MultipartDecoder
    >>> content_type = 'multipart/mixed; boundary=example-boundary'
    >>> body = (
    ...     b'--example-boundary\r\n'
    ...     b'Content-Type: text/plain\r\n\r\n'
    ...     b'hello\r\n'
    ...     b'--example-boundary\r\n'
    ...     b'Content-Type: application/octet-stream\r\n\r\n'
    ...     b'\x00\xff\r\n'
    ...     b'--example-boundary--\r\n'
    ... )
    >>> decoder = MultipartDecoder(body, content_type)
    >>> len(decoder.parts)
    2
    >>> decoder.parts[0].headers[b'content-type']
    b'text/plain'
    >>> decoder.parts[0].text
    'hello'
    >>> decoder.parts[1].content
    b'\x00\xff'

Text encoding and binary parts
------------------------------

``part.content`` always contains bytes. Use it for binary data, for example
when saving an attachment:

.. code-block:: python

    with open('attachment.bin', 'wb') as attachment:
        attachment.write(decoder.parts[1].content)

``part.text`` decodes the content using ``part.encoding``. The default is
``'utf-8'``; the decoder does not choose an encoding from each part's
``Content-Type`` charset. Set the ``encoding`` argument when all text parts
use a different encoding, or set ``part.encoding`` before accessing
``part.text`` when parts use different encodings:

.. code-block:: python

    decoder = MultipartDecoder.from_response(response, encoding='latin-1')
    text_part = decoder.parts[0]
    text_part.encoding = 'utf-8'
    text = text_part.text

The ``encoding`` argument is also used to decode each part's header block, so
header values come back as the same bytes only when it matches the encoding the
headers were written in.

Do not use ``part.text`` for arbitrary binary attachments: decoding can raise
``UnicodeDecodeError`` or interpret binary bytes as text.

Invalid bodies
--------------

A ``Content-Type`` whose main type is not ``multipart`` raises
``NonMultipartContentTypeException``. A part without the blank line that
separates its headers from its content raises
``ImproperBodyPartContentException``. Both can be imported from
``requests_toolbelt``.

API reference
-------------

.. autoclass:: requests_toolbelt.multipart.decoder.MultipartDecoder
    :members: from_response

.. autoclass:: requests_toolbelt.multipart.decoder.BodyPart
    :members: text
