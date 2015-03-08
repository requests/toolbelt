.. _user-agent:

User-Agent Constructor
======================

Having well-formed user-agent strings is important for the proper functioning
of the web. Make server administators happy by generating yourself a nice
user-agent string, just like Requests does! The output of the user-agent
generator looks like this::

    >>> import requests_toolbelt
    >>> requests_toolbelt.user_agent('mypackage', '0.0.1')
    'mypackage/0.0.1 CPython/2.7.5 Darwin/13.0.0'

The Python type and version, and the platform type and version, will accurately
reflect the system that your program is running on. You can drop this easily
into your program like this::

    from requests_toolbelt import user_agent
    from requests import Session

    s = Session()
    s.headers = {
        'User-Agent': user_agent('my_package', '0.0.1')
        }

    r = s.get('https://api.github.com/users')

This will override the default Requests user-agent string for all of your HTTP
requests, replacing it with your own.
