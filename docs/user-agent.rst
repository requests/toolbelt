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

Adding Extra Information to Your User-Agent String
--------------------------------------------------

.. versionadded:: 0.5.0

If you feel it necessary, you can also include versions for other things that
your client is using. For example if you were building a package and wanted to
include the package name and version number as well as the version of requests
and requests-toolbelt you were using you could do the following:

.. code-block:: python

    import requests
    import requests_toolbelt
    from requests_toolbelt.utils.user_agent import user_agent as ua

    user_agent = ua.user_agent('mypackage', '0.0.1',
                               extras=[('requests', requests.__version__),
                                       ('requests-toolbelt', requests_toolbelt.__version__)])

    s = requests.Session()
    s.headers['User-Agent'] = user_agent


Your user agent will now look like::

    mypackage/0.0.1 requests/2.7.0 requests-toolbelt/0.5.0 CPython/2.7.10 Darwin/13.0.0
