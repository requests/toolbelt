"""Private module full of compatibility hacks.

Primarily this is for downstream redistributions of requests that unvendor
urllib3 without providing a shim.

.. warning::

    This module is private. If you use it, and something breaks, you were
    warned
"""

try:
    from requests.packages.urllib3 import connection
    from requests.packages.urllib3 import fields
    from requests.packages.urllib3 import filepost
    from requests.packages.urllib3 import poolmanager
except ImportError:
    from urllib3 import connection  # NOQA
    from urllib3 import fields  # NOQA
    from urllib3 import filepost  # NOQA
    from urllib3 import poolmanager  # NOQA
