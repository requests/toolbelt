Contributing to this project
============================

Checklist
---------

#. All potential contributors must read the :ref:`code-of-conduct` and follow
   it

#. Fork the repository on `GitHub`_ or `GitLab`_

#. Create a new branch, e.g., ``git checkout -b bug/12345``

#. Fix the bug and add tests (if applicable)

#. Run the tests (see :ref:`how-to-run-tests` below)

#. Add documentation

#. Build the documentation to check for errors and formatting (see
   :ref:`how-to-build-the-docs` below)

#. Add yourself to the :file:`AUTHORS.rst` (unless you're already there)

#. Commit it. While writing your commit message, follow these rules:

   * Keep the subject line under 50 characters

   * Use an imperative verb to start the commit

   * Use an empty line between the subject and the message

   * Describe the *why* in detail in the message portion of the commit

   * Wrap the lines of the message at 72 characters

   * Add the appropriate "Closes #12345" syntax to autoclose the issue it
     fixed

   * See :ref:`example-commit-message` below

#. Push it to your fork

#. Create either a request for us to merge your contribution

After this last step, it is possible that we may leave feedback in the form of
review comments. When addressing these comments, you can follow two
strategies:

* Amend/rebase your changes into an existing commit

* Create a new commit with a different message [#]_ and push it to your
  branch

This project is not opinionated about which approach you should prefer.  We
only ask that you are aware of the following:

* Neither GitHub nor GitLab notifies us that you have pushed new changes. A
  friendly ping is welcome

* If you continue to use the same branch that you created the request from,
  both GitHub and GitLab will update the request on the website. You do
  **not** need to create a new request for the new changes.


.. _code-of-conduct:

.. include:: ../CODE_OF_CONDUCT.rst


.. _how-to-run-tests:

How To Run The Tests
--------------------

The preferred method for running the tests in this project is to use `tox`_.
Before you run the tests, ensure you have installed tox either using your
system package manager (e.g., apt, yum, etc.), or your prefered python
installer (e.g., pip).

Then run the tests on at least Python 2.7 and Python 3.x, e.g.,

.. code::

    $ tox -e py27,py34

Finally run one, or both, of the flake8 test environments, e.g.,

.. code::

    $ tox -e py27-flake8
    # or
    $ tox -e py34-flake8

Tox will manage virtual environments and dependencies for you so it will be
the only dependency you need to install to contribute to this project.

.. _how-to-build-the-docs:

How To Build The Documentation
------------------------------

To build the docs, you need to ensure tox is installed and then you may run

.. code::

    $ tox -e docs

This will build the documentation into ``docs/_build/html``. If you then run

.. code::

    $ python2.7 -m SimpleHTTPServer
    # or
    $ python3.4 -m http.server

From that directory, you can view the docs locally at http://localhost:8000/.

.. _example-commit-message:

Example Commit Message
----------------------

::

    Allow users to use the frob when uploading data

    When uploading data with FooBar, users may need to use the frob method
    to ensure that pieces of data are not munged.

    Closes #1234567

Footnotes
---------

.. [#] If each commit has the same message, the reviewer may ask you to
       squash your commits or may squash them for you and perform a manual
       merge.

.. _GitHub: https://github.com/sigmavirus24/requests-toolbelt
.. _GitLab: https://gitlab.com/sigmavirus24/toolbelt
.. _tox: https://tox.readthedocs.org/en/latest/
