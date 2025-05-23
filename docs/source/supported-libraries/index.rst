Supported Libraries
===================

.. _third-party-libraries:

+------------------------------------+-------------------------------------------------------------+-------------------------------+----------------------------------+-------------------------+
| **Library**                        |  **Test suites**                                            |    **Project examples**       |   **Known issues**               |    **Notes**            |
+------------------------------------+-------------------------------------------------------------+-------------------------------+----------------------------------+-------------------------+
| **django-allauth**                 |        :ref:`63% passing <django-allauth-results>`          |                               |                                  |                         |
+------------------------------------+-------------------------------------------------------------+-------------------------------+----------------------------------+-------------------------+
| **django-debug-toolbar**           |        :ref:`73% passing <django-debug-toolbar-results>`    |                               | SQL panel not supported.         |                         |
|                                    |                                                             |                               | Use MQL panel from               |                         |
|                                    |                                                             |                               | django-mongodb-extensions.       |                         |
+------------------------------------+-------------------------------------------------------------+-------------------------------+----------------------------------+-------------------------+
| **django-filter**                  |        :ref:`93% passing <django-filter-results>`           |                               |                                  |                         |
+------------------------------------+-------------------------------------------------------------+-------------------------------+----------------------------------+-------------------------+
| **django-rest-framework**          |        :ref:`81% passing <django-rest-framework-results>`   |                               |                                  |                         |
+------------------------------------+-------------------------------------------------------------+-------------------------------+----------------------------------+-------------------------+
|                                    |                                                             |                               | In addition to custom apps and   | Test results prior to   |
|                                    |                                                             |                               | migrations, requires custom      | merge of `256`_.        |
|                                    |                                                             |                               | URL patterns.                    |                         |
| **wagtail**                        |        :ref:`43% passing <wagtail-results>`                 |                               |                                  |                         |
|                                    |                                                             |                               |                                  |                         |
|                                    |                                                             |                               |                                  |                         |
|                                    |                                                             |                               |                                  |                         |
|                                    |                                                             |                               |                                  |                         |
|                                    |                                                             |                               |                                  |                         |
+------------------------------------+-------------------------------------------------------------+-------------------------------+----------------------------------+-------------------------+

.. toctree::
   django-filter
   django-rest-framework
   django-debug-toolbar
   django-allauth
   wagtail

.. _256: https://github.com/mongodb/django-mongodb-backend/pull/256
