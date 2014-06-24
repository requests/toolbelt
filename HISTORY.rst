History
=======

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
