.. _sessions:

Specialized Sessions
====================

The toolbelt provides specialized session classes in the
:mod:`requests_toolbelt.sessions` module.

.. automodule:: requests_toolbelt.sessions
    :members:


BaseUrlSession
--------------

.. versionadded:: 0.7.0

Many people have written Session subclasses that allow a "base URL" to be
specified so all future requests need not specify the complete URL. To create
one simplified and easy to configure version, we've added the
:class:`requests_toolbelt.sessions.BaseUrlSession` object to the Toolbelt.

.. autoclass:: requests_toolbelt.sessions.BaseUrlSession
    :members:
