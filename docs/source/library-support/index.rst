Third Party Library Support
============================

A third party library is supported when the following criteria are met:

.. note::

    This is the criteria used to determine if a third party library is
    supported by :ref:`Django MongoDB Backend <django-mongodb-backend>`.

    It is not a guarantee that the library will work without issues,
    just that these criteria have been met.

Supported Libraries
-------------------

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

.. toctree::
   :maxdepth: 1
   :caption: Library Details
   
   django-filter
   django-rest-framework
   django-debug-toolbar
   django-allauth

.. toctree::
   :maxdepth: 1
   :caption: Support Information
   
   test-suites
   project-examples
   known-issues
