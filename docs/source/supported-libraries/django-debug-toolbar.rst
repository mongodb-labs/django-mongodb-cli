Django debug toolbar
====================

.. _django-debug-toolbar-results:

Results
-------

Via ``dm repo test django-debug-toolbar``

+---------------------------+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+
|  **PERCENTAGE PASSED**    | **TOTAL**  |  **PASS** | **FAIL**  |  **SKIPPED**   |   **ERROR**  | **EXPECTED FAILURES**      |  **WARNING**     |
+---------------------------+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+
|  73%                      | 262        |     192   | 41        |        26      |       0      |                    1       |   0              |
+---------------------------+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+

- `django-debug-toolbar.txt <../_static/django-debug-toolbar.txt>`_

Settings
--------

Via ``dm repo test django-filter --show``

::

    {
        "apps_file": {
            "source": "config/debug_toolbar/debug_toolbar_apps.py",
            "target": "src/django-debug-toolbar/debug_toolbar/mongo_apps.py",
        },
        "clone_dir": "src/django-debug-toolbar",
        "settings": {
            "test": {
                "source": "config/debug_toolbar/debug_toolbar_settings.py",
                "target": "src/django-debug-toolbar/debug_toolbar/mongo_settings.py",
            },
            "migrations": {
                "source": "config/debug_toolbar/debug_toolbar_settings.py",
                "target": "src/django-debug-toolbar/debug_toolbar/mongo_settings.py",
            },
            "module": {
                "test": "debug_toolbar.mongo_settings",
                "migrations": "debug_toolbar.mongo_settings",
            },
        },
        "test_command": "pytest",
        "test_dir": "src/django-debug-toolbar",
        "test_dirs": ["src/django-debug-toolbar/tests"],
    }

Tests
-----

Via ``dm repo test django-filter -l``

::

    src/django-debug-toolbar/tests
        ├── additional_static
        ├── base.py
        ├── commands
        ├── context_processors.py
        ├── forms.py
        ├── loaders.py
        ├── middleware.py
        ├── models.py
        ├── panels
        ├── settings.py
        ├── sync.py
        ├── templates
        ├── test_checks.py
        ├── test_csp_rendering.py
        ├── test_decorators.py
        ├── test_forms.py
        ├── test_integration.py
        ├── test_integration_async.py
        ├── test_login_not_required.py
        ├── test_middleware.py
        ├── test_toolbar.py
        ├── test_utils.py
        ├── urls.py
        ├── urls_invalid.py
        ├── urls_use_package_urls.py
        └── views.py
