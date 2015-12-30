.. _dumputils:

Utilities for Dumping Information About Responses
=================================================

Occasionally, it is helpful to know almost exactly what data was sent to a
server and what data was received. It can also be challenging at times to
gather all of that data from requests because of all of the different places
you may need to look to find it. In :mod:`requests_toolbelt.utils.dump` there
are two functions that will return a :class:`bytearray` with the information
retrieved from a response object.

.. autofunction::
    requests_toolbelt.utils.dump.dump_all

.. autofunction::
    requests_toolbelt.utils.dump.dump_response
