===========
Test suites
===========

For each third-party library that is supported, the following tasks are performed:

#. **Configure the test suite to run with Django MongoDB Backend**

   a. Evaluate test runner configuration

      i. Depending on the test runner, updating the settings may require
         copying ``mongo_apps.py`` and ``mongo_migrations`` to a module
         that is already included in ``sys.path``.

   b. Update Django settings

      i. Replace the database backend with ``django_mongodb_backend``
      #. Replace contrib apps with MongoDB-compatible apps
      #. Replace test suite apps with MongoDB-compatible apps

   c. Update or disable migrations

      i. Use MongoDB-compatible migrations if not disabled

#. **Run the test suite with Django MongoDB Backend configured**

#. **Log the test run results**

#. **Update test suite tests as needed**

   a. Replace static primary key references with dynamic references
      or static ``ObjectId`` references
