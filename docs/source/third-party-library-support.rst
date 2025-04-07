Third party library support
===========================

.. note::

   This is the criteria used to determine if a third party library is supported
   by Django MongoDB Backend. It is not a guarantee that the library will
   work without issues, just that these criteria have been met.

Support for third party libraries is determined via the following:

- :ref:`Test suites <test_suites>`
- :ref:`Project examples <project_examples>`
- :ref:`Known limitations <known_limitations>`

.. _test_suites:

Test suites
-----------

For each third party library that is supported, the following tasks are performed:

- The test suite is configured to run with Django MongoDB Backend

  - Evaluate test runner configuration

    - Depending on the test runner, updating the settings may require copying
      ``mongo_apps.py`` and ``mongo_migrations`` to a module that is already
      included in ``sys.path``.

  - Update django settings

    - Replace the database backend with ``django_mongodb_backend``
    - Replace contrib apps with MongoDB compatible apps
    - Replace test suite apps with MongoDB compatible apps

  - Update or disable migrations

    - Use MongoDB compatible migrations if not disabled

- The test suite is run with Django MongoDB Backend
- The test results are recorded
- The test suite is updated

  - Replace static primary key references with dynamic references or static ``ObjectId`` references

.. _`project_examples`:

Project examples
----------------

.. _`known_limitations`:

Known limitations
-----------------

- URL configuration
