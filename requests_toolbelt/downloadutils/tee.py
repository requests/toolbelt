"""Tee function implementations."""
import io

_DEFAULT_CHUNKSIZE = 65536


def tee(response, fileobject, chunksize=_DEFAULT_CHUNKSIZE,
        decode_content=None):
    """Stream the response both to the generator and a file.

    This will stream the response body while writing the bytes to
    ``fileobject``.

    Example usage:

    .. code-block:: python

        resp = requests.get(url, stream=True)
        with open('save_file', 'wb') as save_file:
            for chunk in tee(resp, save_file):
                # do stuff with chunk

    .. code-block:: python

        import io

        resp = requests.get(url, stream=True)
        fileobject = io.BytesIO()

        for chunk in tee(resp, fileobject):
            # do stuff with chunk

    :param response: Response from requests.
    :type response: requests.Response
    :param fileobject: Writable file-like object.
    :type fileobject: file, io.BytesIO
    :param int chunksize: (optional), Size of chunk to attempt to stream.
    :param bool decode_content: (optional), If True, this will decode the
        compressed content of the response.
    :raises: TypeError if the fileobject wasn't opened with the right mode
        or isn't a BytesIO object.
    """
    # We will be streaming the raw bytes from over the wire, so we need to
    # ensure that writing to the fileobject will preserve those bytes. On
    # Python3, if the user passes an io.StringIO, this will fail, so we need
    # to check for BytesIO instead.
    if not ('b' in getattr(fileobject, 'mode', '') or
            isinstance(fileobject, io.BytesIO)):
        raise TypeError('tee() will write bytes directly to this fileobject'
                        ', it must be opened with the "b" flag if it is a file'
                        ' or inherit from io.BytesIO.')

    for chunk in response.raw.stream(amt=chunksize,
                                     decode_content=decode_content):
        fileobject.write(chunk)
        yield chunk


def tee_to_file(response, filename, chunksize=_DEFAULT_CHUNKSIZE,
                decode_content=None):
    """Stream the response both to the generator and a file.

    This will open a file named ``filename`` and stream the response body
    while writing the bytes to the opened file object.

    Example usage:

    .. code-block:: python

        resp = requests.get(url, stream=True)
        for chunk in tee_to_file(resp, 'save_file'):
            # do stuff with chunk

    :param response: Response from requests.
    :type response: requests.Response
    :param str filename: Name of file in which we write the response content.
    :param int chunksize: (optional), Size of chunk to attempt to stream.
    :param bool decode_content: (optional), If True, this will decode the
        compressed content of the response.
    """
    with open(filename, 'wb') as fd:
        for chunk in tee(response, fd, chunksize, decode_content):
            yield chunk
