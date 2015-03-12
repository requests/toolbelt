# -*- coding: utf-8 -*-
"""Utilities for dealing with streamed requests."""
import collections
import re

from .. import exceptions as exc

# Regular expressions stolen from werkzeug/http.py
# cd2c97bb0a076da2322f11adce0b2731f9193396 L62-L64
_QUOTED_STRING_RE = r'"[^"\\]*(?:\\.[^"\\]*)*"'
_OPTION_HEADER_PIECE_RE = re.compile(
    r';\s*(%s|[^\s;=]+)\s*(?:=\s*(%s|[^;]+))?\s*' % (_QUOTED_STRING_RE,
                                                     _QUOTED_STRING_RE)
)


def _get_filename(content_disposition):
    for match in _OPTION_HEADER_PIECE_RE.finditer(content_disposition):
        k, v = match.groups()
        if k == 'filename':
            return v
    return None


def stream_response_to_file(response, path=None):
    """Stream a response body to the specified file.

    Either use the ``path`` provided or use the name provided in the
    ``Content-Disposition`` header.

    :param response: A Response object from requests
    :type response: requests.models.Response
    :param str path: The full path and file name used to save the response
    """
    pre_opened = False
    fd = None
    if path:
        if isinstance(getattr(path, 'write', None), collections.Callable):
            pre_opened = True
            fd = path
        else:
            fd = open(path, 'wb')
    else:
        filename = _get_filename(response.headers['content-disposition'])
        if filename is None:
            raise exc.StreamingError(
                'No filename given to stream response to.'
            )
        fd = open(filename, 'wb')

    for chunk in response.iter_content(chunk_size=512):
        fd.write(chunk)

    if not pre_opened:
        fd.close()
