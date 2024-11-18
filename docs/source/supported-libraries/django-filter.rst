Django filter
=============

Settings
--------

Via ``dm repo test django-filter --show``

::

    {
        "apps_file": {
            "source": "settings/filter_apps.py",
            "target": "src/django-filter/tests/mongo_apps.py",
        },
        "clone_dir": "src/django-filter",
        "migrations_dir": {
            "source": "src/django-mongodb-templates/project_template/mongo_migrations",
            "target": "src/django-filter/tests/mongo_migrations",
        },
        "settings": {
            "test": {
                "source": "settings/filter_settings.py",
                "target": "src/django-filter/tests/settings.py",
            },
            "migrations": {
                "source": "settings/filter_settings.py",
                "target": "src/django-filter/tests/settings.py",
            },
            "module": {"test": "tests.settings", "migrations": "tests.settings"},
        },
        "test_command": "./runtests.py",
        "test_dir": "src/django-filter",
        "test_dirs": ["src/django-filter/tests"],
    }


Tests
-----

Via ``dm repo test django-filter -l``


::

    src/django-filter/tests
        ├── models.py
        ├── mongo_apps.py
        ├── mongo_migrations
        ├── rest_framework
        ├── settings.py
        ├── templates
        ├── test_conf.py
        ├── test_fields.py
        ├── test_filtering.py
        ├── test_filters.py
        ├── test_filterset.py
        ├── test_forms.py
        ├── test_utils.py
        ├── test_views.py
        ├── test_widgets.py
        ├── urls.py
        └── utils.py


Results
-------

+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+---------------------------+
| **TOTAL**  |  **PASS** | **FAIL**  |  **SKIPPED**   |   **ERROR**  | **EXPECTED FAILURES**      |  **WARNING**     |  **PERCENTAGE PASSED**    |
+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+---------------------------+
| 515        |      480  | 1         |       16       |       15     |                    3       |   0              |  93%                      |
+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+---------------------------+

Via ``dm repo test django-filter``

- `django-filter.txt <../_static/django-filter.txt>`_
