Contributing to this project
============================

#. All potential contributors must read the :ref:`code-of-conduct` and follow
   it

#. Fork the repository on `GitHub`_ or `GitLab`_

#. Create a new branch, e.g., ``git checkout -b bug/12345``

#. Fix the bug and add tests (if applicable)

#. Add yourself to the :file:`AUTHORS.rst`

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

* Create a new commit and push it to your branch

This project is not opinionated about which approach you should prefer.  We
only ask that you are aware of the following:

* Neither GitHub nor GitLab notifies us that you have pushed new changes. A
  friendly ping is welcome

* If you continue to use the same branch that you created the request from,
  both GitHub and GitLab will update the request on the website. You do
  **not** need to create a new request for the new changes.


.. _code-of-conduct:

.. include:: ../CODE_OF_CONDUCT.rst

.. _example-commit-message:

Example Commit Message
----------------------

::

    Allow users to use the frob when uploading data

    When uploading data with FooBar, users may need to use the frob method
    to ensure that pieces of data are not munged.

    Closes #1234567

.. _GitHub: https://github.com/sigmavirus24/requests-toolbelt
.. _GitLab: https://gitlab.com/sigmavirus24/toolbelt
