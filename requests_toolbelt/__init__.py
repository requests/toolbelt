# -*- coding: utf-8 -*-
"""
requests-toolbelt
=================

See http://toolbelt.rtfd.org/ for documentation

:copyright: (c) 2014 by Ian Cordasco and Cory Benfield
:license: Apache v2.0, see LICENSE for more details
"""

__title__ = 'requests-toolbelt'
__authors__ = 'Ian Cordasco, Cory Benfield'
__license__ = 'Apache v2.0'
__copyright__ = 'Copyright 2014 Ian Cordasco, Cory Benfield'
__version__ = '0.2.0'
__version_info__ = tuple(int(i) for i in __version__.split('.'))

from .auth import GuessAuth
from .multipart import MultipartEncoder, MultipartDecoder
from .multipart import ImproperBodyPartContentException
from .multipart import NonMultipartContentTypeException
from .ssl_adapter import SSLAdapter
from .user_agent import user_agent

__all__ = [
    GuessAuth, MultipartEncoder, MultipartDecoder, SSLAdapter, user_agent,
    ImproperBodyPartContentException, NonMultipartContentTypeException
]
