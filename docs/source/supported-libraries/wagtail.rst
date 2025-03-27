Wagtail
=======

Settings
--------

Via ``dm repo test django-filter --show``

::

    {
        "apps_file": {
            "source": "config/wagtail/wagtail_apps.py",
            "target": "src/wagtail/wagtail/test/mongo_apps.py",
        },
        "clone_dir": "src/wagtail",
        "migrations_dir": {
            "source": "src/django-mongodb-templates/project_template/mongo_migrations",
            "target": "src/wagtail/wagtail/test/mongo_migrations",
        },
        "settings": {
            "test": {
                "source": "config/wagtail/wagtail_settings.py",
                "target": "src/wagtail/wagtail/test/mongo_settings.py",
            },
            "migrations": {
                "source": "config/wagtail/settings_wagtail.py",
                "target": "src/wagtail/wagtail/test/mongo_settings.py",
            },
            "module": {
                "test": "wagtail.test.mongo_settings",
                "migrations": "wagtail.test.mongo_settings",
            },
        },
        "test_command": "./runtests.py",
        "test_dir": "src/wagtail",
        "test_dirs": ["src/wagtail/wagtail/tests", "src/wagtail/wagtail/test"],
    }

Tests
-----

Via ``dm repo test django-filter -l``

::

    src/wagtail/wagtail/tests
        ├── streamfield_migrations
        ├── test-media
        ├── test_audit_log.py
        ├── test_blocks.py
        ├── test_collection_model.py
        ├── test_collection_permission_policies.py
        ├── test_comments.py
        ├── test_draft_model.py
        ├── test_form_data_utils.py
        ├── test_hooks.py
        ├── test_jinja2.py
        ├── test_locale_model.py
        ├── test_lockable_model.py
        ├── test_management_commands.py
        ├── test_migrations.py
        ├── test_page_allowed_http_methods.py
        ├── test_page_assertions.py
        ├── test_page_model.py
        ├── test_page_permission_policies.py
        ├── test_page_permissions.py
        ├── test_page_privacy.py
        ├── test_page_queryset.py
        ├── test_permission_policies.py
        ├── test_reference_index.py
        ├── test_revision_model.py
        ├── test_rich_text.py
        ├── test_signals.py
        ├── test_sites.py
        ├── test_streamfield.py
        ├── test_telepath.py
        ├── test_tests.py
        ├── test_translatablemixin.py
        ├── test_utils.py
        ├── test_views.py
        ├── test_whitelist.py
        ├── test_workflow.py
        ├── test_workflow_model.py
        └── tests.py

    src/wagtail/wagtail/test
        ├── .gitignore
        ├── benchmark.py
        ├── context_processors.py
        ├── customuser
        ├── demosite
        ├── dummy_external_storage.py
        ├── dummy_sendfile_backend.py
        ├── earlypage
        ├── emailuser
        ├── headless_urls.py
        ├── i18n
        ├── manage.py
        ├── middleware.py
        ├── mongo_apps.py
        ├── mongo_migrations
        ├── mongo_settings.py
        ├── non_root_urls.py
        ├── numberformat.py
        ├── routablepage
        ├── search
        ├── settings.py
        ├── settings_ui.py
        ├── snippets
        ├── streamfield_migrations
        ├── testapp
        ├── urls.py
        ├── urls_multilang.py
        ├── urls_multilang_non_root.py
        └── utils

Results
-------

.. note::

    Prior to https://github.com/mongodb/django-mongodb-backend/pull/256

Via ``dm repo test django-filter``

+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+---------------------------+
| **TOTAL**  |  **PASS** | **FAIL**  |  **SKIPPED**   |   **ERROR**  | **EXPECTED FAILURES**      |  **WARNING**     |  **PERCENTAGE PASSED**    |
+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+---------------------------+
| 4897       |     2124  | 52        |        468     |       2252   |                    1       |   0              |  43%                      |
+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+---------------------------+

- `wagtail.txt <../_static/wagtail.txt>`_
- `wagtail2.txt <../_static/wagtail2.txt>`_
