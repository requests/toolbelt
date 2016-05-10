History
=======

0.6.2 -- 2016-05-10
-------------------

Fixed Bugs
~~~~~~~~~~

- When passing a timeout via Requests, it was not appropriately translated to
  the timeout that the urllib3 code was expecting.

0.6.1 -- 2016-05-05
-------------------

Fixed Bugs
~~~~~~~~~~

- Remove assertion about request URLs in the AppEngineAdapter.

- Prevent pip from installing requests 3.0.0 when that is released until we
  are ready to handle it.

0.6.0 -- 2016-01-27
-------------------

More information about this release can be found on the `0.6.0 milestone`_.

New Features
~~~~~~~~~~~~

- Add ``AppEngineAdapter`` to support developers using Google's AppEngine
  platform with Requests.

- Add ``GuessProxyAuth`` class to support guessing between Basic and Digest
  Authentication for proxies.

Fixed Bugs
~~~~~~~~~~

- Ensure that proxies use the correct TLS version when using the
  ``SSLAdapter``.

- Fix an ``AttributeError`` when using the ``HTTPProxyDigestAuth`` class.

Miscellaneous
~~~~~~~~~~~~~

- Drop testing support for Python 3.2. virtualenv and pip have stopped
  supporting it meaning that it is harder to test for this with our CI
  infrastructure. Moving forward we will make a best-effort attempt to
  support 3.2 but will not test for it.


.. _0.6.0 milestone:
    https://github.com/sigmavirus24/requests-toolbelt/milestones/0.6.0

0.5.1 -- 2015-12-16
-------------------

More information about this release can be found on the `0.5.1 milestone`_.

Fixed Bugs
~~~~~~~~~~

- Now papers over the differences in requests' ``super_len`` function from
  versions prior to 2.9.0 and versions 2.9.0 and later.


.. _0.5.1 milestone:
    https://github.com/sigmavirus24/requests-toolbelt/milestones/0.5.1

0.5.0 -- 2015-11-24
-------------------

More information about this release can be found on the `milestone
<https://github.com/sigmavirus24/requests-toolbelt/issues?utf8=%E2%9C%93&q=is%3Aall+milestone%3A0.5+>`_
for 0.5.0.

New Features
~~~~~~~~~~~~

- The ``tee`` submodule was added to ``requests_toolbelt.downloadutils``. It
  allows you to iterate over the bytes of a response while also writing them
  to a file. The ``tee.tee`` function, expects you to pass an open file
  object, while ``tee.tee_to_file`` will use the provided file name to open
  the file for you.

- Added a new parameter to ``requests_toolbelt.utils.user_agent`` that allows
  the user to specify additional items.

- Added nested form-data helper,
  ``requests_toolbelt.utils.formdata.urlencode``.

- Added the ``ForgetfulCookieJar`` to ``requests_toolbelt.cookies``.

- Added utilities for dumping the information about a request-response cycle
  in ``requests_toolbelt.utils.dump``.

- Implemented the API described in the ``requests_toolbelt.threaded`` module
  docstring, i.e., added ``requests_toolbelt.threaded.map`` as an available
  function.

Fixed Bugs
~~~~~~~~~~

- Now papers over the API differences in versions of requests installed from
  system packages versus versions of requests installed from PyPI.

- Allow string types for ``SourceAddressAdapter``.

0.4.0 -- 2015-04-03
-------------------

For more information about this release, please see `milestone 0.4.0
<https://github.com/sigmavirus24/requests-toolbelt/issues?q=milestone%3A0.4>`_
on the project's page.

New Features
~~~~~~~~~~~~

- A naive implemenation of a thread pool is now included in the toolbelt. See
  the docs in ``docs/threading.rst`` or on `Read The Docs
  <https://toolbelt.readthedocs.org>`_.

- The ``StreamingIterator`` now accepts files (such as ``sys.stdin``) without
  a specific length and will properly stream them.

- The ``MultipartEncoder`` now accepts exactly the same format of fields as
  requests' ``files`` parameter does. In other words, you can now also pass in
  extra headers to add to a part in the body. You can also now specify a
  custom ``Content-Type`` for a part.

- An implementation of HTTP Digest Authentication for Proxies is now included.

- A transport adapter that allows a user to specify a specific Certificate
  Fingerprint is now included in the toolbelt.

- A transport adapter that simplifies how users specify socket options is now
  included.

- A transport adapter that simplifies how users can specify TCP Keep-Alive
  options is now included in the toolbelt.

- Deprecated functions from ``requests.utils`` are now included and
  maintained.

- An authentication tool that allows users to specify how to authenticate to
  several different domains at once is now included.

- A function to save streamed responses to disk by analyzing the
  ``Content-Disposition`` header is now included in the toolbelt.

Fixed Bugs
~~~~~~~~~~

- The ``MultipartEncoder`` will now allow users to upload files larger than
  4GB on 32-bit systems.

- The ``MultipartEncoder`` will now accept empty unicode strings for form
  values.

0.3.1 -- 2014-06-23
-------------------

- Fix the fact that 0.3.0 bundle did not include the ``StreamingIterator``

0.3.0 -- 2014-05-21
-------------------

Bug Fixes
~~~~~~~~~

- Complete rewrite of ``MultipartEncoder`` fixes bug where bytes were lost in
  uploads

New Features
~~~~~~~~~~~~

- ``MultipartDecoder`` to accept ``multipart/form-data`` response bodies and
  parse them into an easy to use object.

- ``SourceAddressAdapter`` to allow users to choose a local address to bind
  connections to.

- ``GuessAuth`` which accepts a username and password and uses the
  ``WWW-Authenticate`` header to determine how to authenticate against a
  server.

- ``MultipartEncoderMonitor`` wraps an instance of the ``MultipartEncoder``
  and keeps track of how many bytes were read and will call the provided
  callback.

- ``StreamingIterator`` will wrap an iterator and stream the upload instead of
  chunk it, provided you also provide the length of the content you wish to
  upload.

0.2.0 -- 2014-02-24
-------------------

- Add ability to tell ``MultipartEncoder`` which encoding to use. By default
  it uses 'utf-8'.

- Fix #10 - allow users to install with pip

- Fix #9 - Fix ``MultipartEncoder#to_string`` so that it properly handles file
  objects as fields

0.1.2 -- 2014-01-19
-------------------

- At some point during development we broke how we handle normal file objects.
  Thanks to @konomae this is now fixed.

0.1.1 -- 2014-01-19
-------------------

- Handle ``io.BytesIO``-like objects better

0.1.0 -- 2014-01-18
-------------------

- Add initial implementation of the streaming ``MultipartEncoder``

- Add initial implementation of the ``user_agent`` function

- Add the ``SSLAdapter``
