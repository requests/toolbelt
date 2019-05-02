"""This module provides functions for dumping information about responses."""
import collections

from requests import compat


__all__ = ['dump_response', 'dump_all', 'NoopSanitizer', 'HeaderSanitizer']

HTTP_VERSIONS = {
    9: b'0.9',
    10: b'1.0',
    11: b'1.1',
}

_PrefixSettings = collections.namedtuple('PrefixSettings',
                                         ['request', 'response'])


class Sanitizer(object):
    CLEANSED_SUBSTITUTE = "********************"

    def _sanitize_headers(self, headers):
        sanitized_headers = headers.copy()
        for name in headers:
            if self.should_sanitize_header(name):
                sanitized_headers[name] = self.CLEANSED_SUBSTITUTE
            if self.should_strip_header(name):
                del sanitized_headers[name]
        return sanitized_headers

    def request_headers(self, headers):
        """Sanitize the request headers

        :param headers: The request headers
        :type headers: :class:`requests.structures.CaseInsensitiveDict`
        :return: A new headers object
        :rtype: :class:`requests.structures.CaseInsensitiveDict`
        """
        return self._sanitize_headers(headers)

    def request_body(self, body):
        """Sanitize a request body

        :param body: The body of the request
        :type body: `bytes`
        :return: The value to dump for the body
        :rtype: `bytes`
        """
        raise NotImplementedError

    def response_headers(self, headers):
        """Sanitize the response headers

        Modify the headers in place, removing or redacting values

        :param headers: The response headers
        :type headers: :class:`requests.structures.CaseInsensitiveDict`
        """
        return self._sanitize_headers(headers)

    def response_body(self, body):
        """Sanitize a request body

        :param body: The body of the request
        :type body: `bytes`
        :return: The value to dump for the body
        :rtype: `bytes`
        """
        raise NotImplementedError

    def should_sanitize_header(self, name):
        raise NotImplementedError

    def should_strip_header(self, name):
        raise NotImplementedError


class NoopSanitizer(Sanitizer):
    """Performs no sanitation"""

    def should_sanitize_header(self, name):
        return False

    def should_strip_header(self, name):
        return False

    def request_body(self, body):
        return body

    def response_body(self, body):
        return body


class HeaderSanitizer(NoopSanitizer):
    """Redact the values of headers considered sensitive

    This will check all headers in both request and response against a set of
    sensitive headers (see :attr:`HeaderSanitizer.SENSITIVE_HEADERS`), and
    redact the values to protect sensitive data.

    """

    # List of sensitive headers copied from:
    # https://github.com/google/har-sanitizer
    SENSITIVE_HEADERS = {
        "state",
        "shdf",
        "usg",
        "password",
        "email",
        "code",
        "code-verifier",
        "client-secret",
        "client-id",
        "token",
        "access-token",
        "authenticity-token",
        "id-token",
        "appid",
        "challenge",
        "facetid",
        "assertion",
        "fcparams",
        "serverdata",
        "authorization",
        "auth",
        "x-client-data",
        "samlrequest",
        "samlresponse"
    }

    def should_sanitize_header(self, name):
        return name.lower().replace('_', '-') in self.SENSITIVE_HEADERS


class PrefixSettings(_PrefixSettings):
    def __new__(cls, request, response):
        request = _coerce_to_bytes(request)
        response = _coerce_to_bytes(response)
        return super(PrefixSettings, cls).__new__(cls, request, response)


def _get_proxy_information(response):
    if getattr(response.connection, 'proxy_manager', False):
        proxy_info = {}
        request_url = response.request.url
        if request_url.startswith('https://'):
            proxy_info['method'] = 'CONNECT'

        proxy_info['request_path'] = request_url
        return proxy_info
    return None


def _format_header(name, value):
    return (_coerce_to_bytes(name) + b': ' + _coerce_to_bytes(value) +
            b'\r\n')


def _build_request_path(url, proxy_info):
    uri = compat.urlparse(url)
    proxy_url = proxy_info.get('request_path')
    if proxy_url is not None:
        request_path = _coerce_to_bytes(proxy_url)
        return request_path, uri

    request_path = _coerce_to_bytes(uri.path)
    if uri.query:
        request_path += b'?' + _coerce_to_bytes(uri.query)

    return request_path, uri


def _dump_request_data(request, prefixes, bytearr, proxy_info=None,
                       sanitizer=None):
    if proxy_info is None:
        proxy_info = {}
    if sanitizer is None:
        sanitizer = NoopSanitizer()

    prefix = prefixes.request
    method = _coerce_to_bytes(proxy_info.pop('method', request.method))
    request_path, uri = _build_request_path(request.url, proxy_info)

    # <prefix><METHOD> <request-path> HTTP/1.1
    bytearr.extend(prefix + method + b' ' + request_path + b' HTTP/1.1\r\n')

    # <prefix>Host: <request-host> OR host header specified by user
    headers = request.headers.copy()
    host_header = _coerce_to_bytes(headers.pop('Host', uri.netloc))
    bytearr.extend(prefix + b'Host: ' + host_header + b'\r\n')

    sanitized_headers = sanitizer.request_headers(headers)
    for name, value in sanitized_headers.items():
        bytearr.extend(prefix + _format_header(name, value))

    bytearr.extend(prefix + b'\r\n')
    if request.body:
        if isinstance(request.body, compat.basestring):
            body = _coerce_to_bytes(request.body)
            body = sanitizer.request_body(body)
            bytearr.extend(prefix + body)
        else:
            # In the event that the body is a file-like object, let's not try
            # to read everything into memory.
            bytearr.extend(b'<< Request body is not a string-like type >>')
    bytearr.extend(b'\r\n')


def _dump_response_data(response, prefixes, bytearr, sanitizer=None):
    if sanitizer is None:
        sanitizer = NoopSanitizer()

    prefix = prefixes.response
    # Let's interact almost entirely with urllib3's response
    raw = response.raw

    # Let's convert the version int from httplib to bytes
    version_str = HTTP_VERSIONS.get(raw.version, b'?')

    # <prefix>HTTP/<version_str> <status_code> <reason>
    bytearr.extend(prefix + b'HTTP/' + version_str + b' ' +
                   str(raw.status).encode('ascii') + b' ' +
                   _coerce_to_bytes(response.reason) + b'\r\n')

    sanitized_headers = sanitizer.response_headers(raw.headers)
    for name in sanitized_headers.keys():
        for value in sanitized_headers.getlist(name):
            bytearr.extend(prefix + _format_header(name, value))

    bytearr.extend(prefix + b'\r\n')

    body = sanitizer.response_body(response.content)
    bytearr.extend(body)


def _coerce_to_bytes(data):
    if not isinstance(data, bytes) and hasattr(data, 'encode'):
        data = data.encode('utf-8')
    # Don't bail out with an exception if data is None
    return data if data is not None else b''


def dump_response(response, request_prefix=b'< ', response_prefix=b'> ',
                  data_array=None, sanitizer=None):
    """Dump a single request-response cycle's information.

    This will take a response object and dump only the data that requests can
    see for that single request-response cycle.

    If the optional ``sanitize`` parameter is used, it should be an object that
    implements the same interface as :class:`Sanitizer`. One possible
    implementation is :class:`HeaderSanitizer`, which will redact sensitive
    headers.

    Example::

        import requests
        from requests_toolbelt.utils import dump

        resp = requests.get('https://api.github.com/users/sigmavirus24')
        data = dump.dump_response(resp)
        print(data.decode('utf-8'))

    :param response:
        The response to format
    :type response: :class:`requests.Response`
    :param request_prefix: (*optional*)
        Bytes to prefix each line of the request data
    :type request_prefix: :class:`bytes`
    :param response_prefix: (*optional*)
        Bytes to prefix each line of the response data
    :type response_prefix: :class:`bytes`
    :param data_array: (*optional*)
        Bytearray to which we append the request-response cycle data
    :type data_array: :class:`bytearray`
    :param sanitizer: (*optional*)
        How to sanitize the dump.
    :type sanitizer: :class:`NoopSanitizer`
    :returns: Formatted bytes of request and response information.
    :rtype: :class:`bytearray`
    """
    data = data_array if data_array is not None else bytearray()
    prefixes = PrefixSettings(request_prefix, response_prefix)
    if sanitizer is None:
        sanitizer = NoopSanitizer()

    if not hasattr(response, 'request'):
        raise ValueError('Response has no associated request')

    proxy_info = _get_proxy_information(response)
    _dump_request_data(response.request, prefixes, data,
                       proxy_info=proxy_info, sanitizer=sanitizer)
    _dump_response_data(response, prefixes, data, sanitizer)
    return data


def dump_all(response, request_prefix=b'< ', response_prefix=b'> ',
             sanitizer=None):
    """Dump all requests and responses including redirects.

    This takes the response returned by requests and will dump all
    request-response pairs in the redirect history in order followed by the
    final request-response.

    If the optional ``sanitize`` parameter is used, it should be an object that
    implements the same interface as :class:`Sanitizer`. One possible
    implementation is :class:`HeaderSanitizer`, which will redact sensitive
    headers.

    Example::

        import requests
        from requests_toolbelt.utils import dump

        resp = requests.get('https://httpbin.org/redirect/5')
        data = dump.dump_all(resp)
        print(data.decode('utf-8'))

    :param response:
        The response to format
    :type response: :class:`requests.Response`
    :param request_prefix: (*optional*)
        Bytes to prefix each line of the request data
    :type request_prefix: :class:`bytes`
    :param response_prefix: (*optional*)
        Bytes to prefix each line of the response data
    :type response_prefix: :class:`bytes`
    :param sanitizer: (*optional*)
        How to sanitize the dump.
    :type sanitizer: :class:`NoopSanitizer`
    :returns: Formatted bytes of request and response information.
    :rtype: :class:`bytearray`
    """
    if sanitizer is None:
        sanitizer = NoopSanitizer()

    data = bytearray()

    history = list(response.history[:])
    history.append(response)

    for response in history:
        dump_response(response, request_prefix, response_prefix, data,
                      sanitizer)

    return data
