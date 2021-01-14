.. _dumputils:

Utilities for Dumping Information About Responses
=================================================

Occasionally, it is helpful to know almost exactly what data was sent to a
server and what data was received. It can also be challenging at times to
gather all of that data from requests because of all of the different places
you may need to look to find it. In :mod:`requests_toolbelt.utils.dump` there
are two functions that will return a :class:`bytearray` with the information
retrieved from a response object.

Sanitizing information before dumping
-------------------------------------

When debugging, it is quite often useful to dump the request or response to
debugging log, where it can be inspected. The problem is that often the request
or response can contain sensitive data that should not be stored in a logfile
on disk.

To solve this, it is possible to supply a :class:`Sanitizer` which can
manipulate the body or the headers before they are dumped. The default is to
not do anything. For convenience, :class:`HeaderSanitizer` is provided, which
will redact the value of headers that are commonly considered sensitive (See
:attr:`HeaderSanitizer.SENSITIVE_HEADERS`).

You can make any sanitizing you need by subclassing :class:`Sanitizer` and
passing in an instance to :py:func:`dump_all` or :func:`dump_response`.

Public members
--------------

.. autofunction::
    requests_toolbelt.utils.dump.dump_all

.. autofunction::
    requests_toolbelt.utils.dump.dump_response

.. autoclass::
    requests_toolbelt.utils.dump.Sanitizer
    :members:

.. autoclass::
    requests_toolbelt.utils.dump.HeaderSanitizer
