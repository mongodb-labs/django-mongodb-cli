Django rest framework
=====================

Settings
--------

Via ``dm repo test django-rest-framework --show``

::

    {
        "apps_file": {
            "source": "config/rest_framework/rest_framework_apps.py",
            "target": "src/django-rest-framework/tests/mongo_apps.py",
        },
        "clone_dir": "src/django-rest-framework",
        "migrations_dir": {
            "source": "src/rest_framework/django-mongodb-project/mongo_migrations",
            "target": "src/django-rest-framework/tests/mongo_migrations",
        },
        "settings": {
            "test": {
                "source": "config/rest_framework/rest_framework_settings.py",
                "target": "src/django-rest-framework/tests/conftest.py",
            },
            "migrations": {
                "source": "config/rest_framework/rest_framework_migrate.py",
                "target": "src/django-rest-framework/tests/conftest.py",
            },
            "module": {"test": "tests.conftest", "migrations": "tests.conftest"},
        },
        "test_command": "./runtests.py",
        "test_dir": "src/django-rest-framework",
        "test_dirs": ["src/django-rest-framework/tests"],
    }

Tests
-----

Via ``dm repo test django-filter -l``

::

    src/django-rest-framework/tests
        ├── authentication
        ├── browsable_api
        ├── conftest.py
        ├── generic_relations
        ├── importable
        ├── models.py
        ├── mongo_apps.py
        ├── mongo_migrations
        ├── schemas
        ├── test_api_client.py
        ├── test_atomic_requests.py
        ├── test_authtoken.py
        ├── test_bound_fields.py
        ├── test_decorators.py
        ├── test_description.py
        ├── test_encoders.py
        ├── test_exceptions.py
        ├── test_fields.py
        ├── test_filters.py
        ├── test_generics.py
        ├── test_htmlrenderer.py
        ├── test_lazy_hyperlinks.py
        ├── test_metadata.py
        ├── test_middleware.py
        ├── test_model_serializer.py
        ├── test_multitable_inheritance.py
        ├── test_negotiation.py
        ├── test_one_to_one_with_inheritance.py
        ├── test_pagination.py
        ├── test_parsers.py
        ├── test_permissions.py
        ├── test_prefetch_related.py
        ├── test_relations.py
        ├── test_relations_hyperlink.py
        ├── test_relations_pk.py
        ├── test_relations_slug.py
        ├── test_renderers.py
        ├── test_request.py
        ├── test_requests_client.py
        ├── test_response.py
        ├── test_reverse.py
        ├── test_routers.py
        ├── test_serializer.py
        ├── test_serializer_bulk_update.py
        ├── test_serializer_lists.py
        ├── test_serializer_nested.py
        ├── test_settings.py
        ├── test_status.py
        ├── test_templates.py
        ├── test_templatetags.py
        ├── test_testing.py
        ├── test_throttling.py
        ├── test_urlpatterns.py
        ├── test_utils.py
        ├── test_validation.py
        ├── test_validation_error.py
        ├── test_validators.py
        ├── test_versioning.py
        ├── test_views.py
        ├── test_viewsets.py
        ├── test_write_only_fields.py
        ├── urls.py
        └── utils.py

Results
-------

Via ``dm repo test django-rest-framework``

+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+---------------------------+
| **TOTAL**  |  **PASS** | **FAIL**  |  **SKIPPED**   |   **ERROR**  | **EXPECTED FAILURES**      |  **WARNING**     |  **PERCENTAGE PASSED**    |
+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+---------------------------+
| 1558       |     1276  | 146       |        136     |       0      |                    0       |   4              |  81%                      |
+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+---------------------------+

- `django-rest-framework.txt <../_static/django-rest-framework.txt>`_
