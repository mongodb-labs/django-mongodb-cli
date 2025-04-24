.. _test_suites:

Test suites
-----------

For each third party library that is supported, the following tasks are performed:

#. **The test suite is configured to run with Django MongoDB Backend.**

  a. Evaluate test runner configuration

    i. Depending on the test runner, updating the settings may require
    copying ``mongo_apps.py`` and ``mongo_migrations`` to a module that is
    already included in ``sys.path``.

  b. Update django settings

    i. Replace the database backend with ``django_mongodb_backend``
    #. Replace contrib apps with MongoDB compatible apps
    #. Replace test suite apps with MongoDB compatible apps

  c. Update or disable migrations

    i. Use MongoDB compatible migrations if not disabled

2. **The test suite is run with Django MongoDB Backend configured.**
#. **The test run results are logged.**
#. **The test suite tests are updated as needed.**

  a. Replace static primary key references with dynamic references or static ``ObjectId`` references
