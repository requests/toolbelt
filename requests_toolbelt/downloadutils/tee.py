"""Tee function implementations."""

_DEFAULT_CHUNKSIZE = 65536


def tee(response, fileobject, chunksize=_DEFAULT_CHUNKSIZE):
    """Stream the response both to the generator and a file.

    This will stream the response body while writing the bytes to
    ``fileobject``.

    Example usage:

    .. code-block:: python

        resp = requests.get(url, stream=True)
        with open('save_file', 'w+b') as save_file:
            for chunk in tee(resp, save_file):
                # do stuff with chunk

    :param response: Response from requests.
    :type response: requests.Response
    :param fileobject: Writable file-like object.
    :type fileobject: file, io.BytesIO
    :param int chunksize: (optional), Size of chunk to attempt to stream.
    """
    for chunk in response.raw.stream(amt=chunksize):
        fileobject.write(chunk)
        yield chunk


def tee_to_file(response, filename, chunksize=_DEFAULT_CHUNKSIZE):
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
    :param str fileoname: Name of file in which we write the response content.
    :param int chunksize: (optional), Size of chunk to attempt to stream.
    """
    with open(filename, 'wb') as fd:
        for chunk in tee(response, fd, chunksize):
            yield chunk
