# -*- coding: utf-8 -*-
"""Utilities for dealing with streamed requests."""
import ntpath
import os.path
import re

try:
    from urllib.parse import unquote_to_bytes
except ImportError:  # Python 2
    from urllib import unquote as unquote_to_bytes

from .. import exceptions as exc

# Regular expressions stolen from werkzeug/http.py
# cd2c97bb0a076da2322f11adce0b2731f9193396 L62-L64
_QUOTED_STRING_RE = r'"[^"\\]*(?:\\.[^"\\]*)*"'
_OPTION_HEADER_PIECE_RE = re.compile(
    r';\s*(%s|[^\s;=]+)\s*(?:=\s*(%s|[^;]+))?\s*' % (_QUOTED_STRING_RE,
                                                     _QUOTED_STRING_RE)
)
_DEFAULT_CHUNKSIZE = 512


def _get_filename(content_disposition):
    filename = None
    for match in _OPTION_HEADER_PIECE_RE.finditer(content_disposition):
        k, v = match.groups()
        if k.lower() == 'filename' and v is not None and filename is None:
            # Keep the ordinary filename as a fallback for invalid filename*.
            filename = os.path.split(v)[1]
        elif k.lower() == 'filename*' and v is not None:
            try:
                charset, language, encoded = v.strip().split("'", 2)
                # Invalid escapes must not silently become literal filenames.
                if re.search(r'%(?![0-9a-fA-F]{2})', encoded):
                    continue
                value = unquote_to_bytes(encoded).decode(charset)
            except (ValueError, LookupError, UnicodeError):
                continue
            # Strip path components after decoding, including Windows paths.
            value = os.path.basename(ntpath.basename(value))
            if value and value not in ('.', '..') and '\x00' not in value:
                return value
    return filename


def get_download_file_path(response, path):
    """
    Given a response and a path, return a file path for a download.

    If a ``path`` parameter is a directory, this function will parse the
    ``Content-Disposition`` header on the response to determine the name of the
    file as reported by the server, and return a file path in the specified
    directory.

    RFC 5987 encoded ``filename*`` values take precedence over ``filename``.
    Invalid extended values fall back to the ordinary filename.

    If ``path`` is empty or None, this function will return a path relative
    to the process' current working directory.

    If path is a full file path, return it.

    :param response: A Response object from requests
    :type response: requests.models.Response
    :param str path: Directory or file path.
    :returns: full file path to download as
    :rtype: str
    :raises: :class:`requests_toolbelt.exceptions.StreamingError`
    """
    path_is_dir = path and os.path.isdir(path)

    if path and not path_is_dir:
        # fully qualified file path
        filepath = path
    else:
        response_filename = _get_filename(
            response.headers.get('content-disposition', '')
        )
        if not response_filename:
            raise exc.StreamingError('No filename given to stream response to')

        if path_is_dir:
            # directory to download to
            filepath = os.path.join(path, response_filename)
        else:
            # fallback to downloading to current working directory
            filepath = response_filename

    return filepath


def stream_response_to_file(response, path=None, chunksize=_DEFAULT_CHUNKSIZE):
    """Stream a response body to the specified file.

    Either use the ``path`` provided or use the name provided in the
    ``Content-Disposition`` header.

    .. warning::

        If you pass this function an open file-like object as the ``path``
        parameter, the function will not close that file for you.

    .. warning::

        This function will not automatically close the response object
        passed in as the ``response`` parameter.

    If a ``path`` parameter is a directory, this function will parse the
    ``Content-Disposition`` header on the response to determine the name of the
    file as reported by the server, and return a file path in the specified
    directory. If no ``path`` parameter is supplied, this function will default
    to the process' current working directory.

    .. code-block:: python

        import requests
        from requests_toolbelt import exceptions
        from requests_toolbelt.downloadutils import stream

        r = requests.get(url, stream=True)
        try:
            filename = stream.stream_response_to_file(r)
        except exceptions.StreamingError as e:
            # The toolbelt could not find the filename in the
            # Content-Disposition
            print(e.message)

    You can also specify the filename as a string. This will be passed to
    the built-in :func:`open` and we will read the content into the file.

    .. code-block:: python

        import requests
        from requests_toolbelt.downloadutils import stream

        r = requests.get(url, stream=True)
        filename = stream.stream_response_to_file(r, path='myfile')

    If the calculated download file path already exists, this function will
    raise a StreamingError.

    Instead, if you want to manage the file object yourself, you need to
    provide either a :class:`io.BytesIO` object or a file opened with the
    `'b'` flag. See the two examples below for more details.

    .. code-block:: python

        import requests
        from requests_toolbelt.downloadutils import stream

        with open('myfile', 'wb') as fd:
            r = requests.get(url, stream=True)
            filename = stream.stream_response_to_file(r, path=fd)

        print('{} saved to {}'.format(url, filename))

    .. code-block:: python

        import io
        import requests
        from requests_toolbelt.downloadutils import stream

        b = io.BytesIO()
        r = requests.get(url, stream=True)
        filename = stream.stream_response_to_file(r, path=b)
        assert filename is None

    :param response: A Response object from requests
    :type response: requests.models.Response
    :param path: *(optional)*, Either a string with the path to the location
        to save the response content, or a file-like object expecting bytes.
    :type path: :class:`str`, or object with a :meth:`write`
    :param int chunksize: (optional), Size of chunk to attempt to stream
        (default 512B).
    :returns: The name of the file, if one can be determined, else None
    :rtype: str
    :raises: :class:`requests_toolbelt.exceptions.StreamingError`
    """
    pre_opened = False
    fd = None
    filename = None
    if path and callable(getattr(path, 'write', None)):
        pre_opened = True
        fd = path
        filename = getattr(fd, 'name', None)
    else:
        filename = get_download_file_path(response, path)
        if os.path.exists(filename):
            raise exc.StreamingError("File already exists: %s" % filename)
        fd = open(filename, 'wb')

    for chunk in response.iter_content(chunk_size=chunksize):
        fd.write(chunk)

    if not pre_opened:
        fd.close()

    return filename
