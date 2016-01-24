# -*- coding: utf-8 -*-
"""Collection of exceptions raised by requests-toolbelt."""


class StreamingError(Exception):
    """Used in :mod:`requests_toolbelt.downloadutils.stream`."""
    pass


class VersionMismatchError(Exception):
    """Used to indicate a version mismatch in the version of requests required.

    The feature in use requires a newer version of Requests to function
    appropriately but the version installed is not sufficient.
    """
    pass
