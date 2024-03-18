Security
========

We take the security of ``requests-toolbelt`` seriously. The following are a set of
policies we have adopted to ensure that security issues are addressed in a
timely fashion.

Known vulnerabilities
---------------------

A list of all known vulnerabilities in ``requests-toolbelt`` can be found on
`osv.dev`_, as well as other ecosystem vulnerability databases. They can
automatically be scanned for using tools such as `pip-audit`_ or `osv-scan`_.

What is a security issue?
-------------------------

Anytime it's possible to write code using ``requests-toolbelt``'s public API which
does not provide the guarantees that a reasonable developer would expect it to
based on our documentation.

That's a bit academic, but basically it means the scope of what we consider a
vulnerability is broad, and we do not require a proof of concept or even a
specific exploit, merely a reasonable threat model under which ``requests-toolbelt``
could be attacked.

In general, if you're unsure, we request that you to default to treating things
as security issues and handling them sensitively, the worst thing that can
happen is that we'll ask you to file a public issue.

Reporting a security issue
--------------------------

We ask that you do not report security issues to our normal GitHub issue
tracker.

If you believe you've identified a security issue with ``requests-toolbelt``,
please report it via our `security advisory page`_.

Once you've submitted an issue, you should receive an acknowledgment and 
depending on the action to be taken, you may receive further follow-up.

Supported Versions
------------------

At any given time, we will provide security support for the `default`_ branch
as well as the most recent release.

Disclosure Process
------------------

When we become aware of a security bug in ``requests-toolbelt``, we will endeavor to
fix it and issue a release as quickly as possible. We will generally issue a new
release for any security issue.

Credits
-------

This policy is largely borrowed from `pyca/cryptography`_ and edited to
represent the guarantees provided by the ``requests-toolbelt`` maintainers.

.. _`osv.dev`: https://osv.dev/list?ecosystem=PyPI&q=requests-toolbelt
.. _`pip-audit`: https://pypi.org/project/pip-audit/
.. _`osv-scan`: https://google.github.io/osv-scanner/
.. _`security advisory page`: https://github.com/requests/toolbelt/security/advisories/new
.. _`default`: https://github.com/requests/toolbelt
.. _`pyca/cryptography`: https://github.com/pyca/cryptography
