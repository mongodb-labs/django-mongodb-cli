from os.path import join

test_settings_map = {
    "mongo-python-driver": {
        "test_command": "just",
        "test_dir": join("src", "mongo-python-driver", "test"),
        "clone_dir": join("src", "mongo-python-driver"),
        "test_dirs": [
            join("src", "mongo-python-driver", "test"),
        ],
    },
    "django": {
        "apps_file": {},
        "test_command": "./runtests.py",
        "test_dir": join("src", "django", "tests"),
        "clone_dir": join("src", "django"),
        "migrations_dir": {
            "source": join(
                "src",
                "django-mongodb-templates",
                "project_template",
                "mongo_migrations",
            ),
            "target": join("src", "django", "tests"),
        },
        "settings": {
            "test": {
                "source": join("config", "django", "django_settings.py"),
                "target": join("src", "django", "tests", "mongo_settings.py"),
            },
            "migrations": {
                "source": join("config", "django", "django_settings.py"),
                "target": join("src", "django", "tests", "mongo_settings.py"),
            },
            "module": {
                "test": "mongo_settings",
                "migrations": "mongo_settings",
            },
        },
        "test_dirs": [
            join("src", "django", "tests"),
            join("src", "django-mongodb-backend", "tests"),
        ],
    },
    "django-filter": {
        "apps_file": {
            "source": join("config", "filter", "filter_apps.py"),
            "target": join("src", "django-filter", "tests", "mongo_apps.py"),
        },
        "test_command": "./runtests.py",
        "test_dir": join("src", "django-filter"),
        "migrations_dir": {
            "source": join(
                "src",
                "django-mongodb-templates",
                "project_template",
                "mongo_migrations",
            ),
            "target": join("src", "django-filter", "tests", "mongo_migrations"),
        },
        "clone_dir": join("src", "django-filter"),
        "settings": {
            "test": {
                "source": join("config", "filter", "filter_settings.py"),
                "target": join("src", "django-filter", "tests", "settings.py"),
            },
            "migrations": {
                "source": join("config", "filter", "filter_settings.py"),
                "target": join("src", "django-filter", "tests", "settings.py"),
            },
            "module": {
                "test": "tests.settings",
                "migrations": "tests.settings",
            },
        },
        "test_dirs": [join("src", "django-filter", "tests")],
    },
    "django-rest-framework": {
        "apps_file": {
            "source": join("config", "rest_framework", "rest_framework_apps.py"),
            "target": join("src", "django-rest-framework", "tests", "mongo_apps.py"),
        },
        "migrations_dir": {
            "source": join(
                "src", "rest_framework", "django-mongodb-project", "mongo_migrations"
            ),
            "target": join("src", "django-rest-framework", "tests", "mongo_migrations"),
        },
        "test_command": "./runtests.py",
        "test_dir": join("src", "django-rest-framework"),
        "clone_dir": join("src", "django-rest-framework"),
        "settings": {
            "test": {
                "source": join(
                    "config", "rest_framework", "rest_framework_settings.py"
                ),
                "target": join("src", "django-rest-framework", "tests", "conftest.py"),
            },
            "migrations": {
                "source": join("config", "rest_framework", "rest_framework_migrate.py"),
                "target": join("src", "django-rest-framework", "tests", "conftest.py"),
            },
            "module": {
                "test": "tests.conftest",
                "migrations": "tests.conftest",
            },
        },
        "test_dirs": [join("src", "django-rest-framework", "tests")],
    },
    "wagtail": {
        "apps_file": {
            "source": join("config", "wagtail", "wagtail_apps.py"),
            "target": join("src", "wagtail", "wagtail", "test", "mongo_apps.py"),
        },
        "migrations_dir": {
            "source": join(
                "src",
                "django-mongodb-templates",
                "project_template",
                "mongo_migrations",
            ),
            "target": join("src", "wagtail", "wagtail", "test", "mongo_migrations"),
        },
        "test_command": "./runtests.py",
        "test_dir": join("src", "wagtail"),
        "clone_dir": join("src", "wagtail"),
        "settings": {
            "test": {
                "source": join("config", "wagtail", "wagtail_settings.py"),
                "target": join(
                    "src", "wagtail", "wagtail", "test", "mongo_settings.py"
                ),
            },
            "migrations": {
                "source": join("config", "wagtail", "settings_wagtail.py"),
                "target": join(
                    "src", "wagtail", "wagtail", "test", "mongo_settings.py"
                ),
            },
            "module": {
                "test": "wagtail.test.mongo_settings",
                "migrations": "wagtail.test.mongo_settings",
            },
        },
        "test_dirs": [
            join("src", "wagtail", "wagtail", "tests"),
            join("src", "wagtail", "wagtail", "test"),
        ],
    },
    "django-debug-toolbar": {
        "apps_file": {
            "source": join("config", "debug_toolbar", "debug_toolbar_apps.py"),
            "target": join(
                "src", "django-debug-toolbar", "debug_toolbar", "mongo_apps.py"
            ),
        },
        "test_command": "pytest",
        "test_dir": join("src", "django-debug-toolbar"),
        "clone_dir": join("src", "django-debug-toolbar"),
        "settings": {
            "test": {
                "source": join("config", "debug_toolbar", "debug_toolbar_settings.py"),
                "target": join(
                    "src", "django-debug-toolbar", "debug_toolbar", "mongo_settings.py"
                ),
            },
            "migrations": {
                "source": join("config", "debug_toolbar", "debug_toolbar_settings.py"),
                "target": join(
                    "src", "django-debug-toolbar", "debug_toolbar", "mongo_settings.py"
                ),
            },
            "module": {
                "test": "debug_toolbar.mongo_settings",
                "migrations": "debug_toolbar.mongo_settings",
            },
        },
        "test_dirs": [
            join("src", "django-debug-toolbar", "tests"),
        ],
    },
    "django-mongodb-extensions": {
        "apps_file": {
            "source": join("config", "extensions", "debug_toolbar_apps.py"),
            "target": join(
                "src",
                "django-mongodb-extensions",
                "django_mongodb_extensions",
                "mongo_apps.py",
            ),
        },
        "test_command": "pytest",
        "test_dir": join("src", "django-mongodb-extensions"),
        "clone_dir": join("src", "django-mongodb-extensions"),
        "settings": {
            "test": {
                "source": join("config", "extensions", "debug_toolbar_settings.py"),
                "target": join(
                    "src",
                    "django-mongodb-extensions",
                    "django_mongodb_extensions",
                    "mongo_settings.py",
                ),
            },
            "migrations": {
                "source": join("config", "extensions", "debug_toolbar_settings.py"),
                "target": join(
                    "src",
                    "django-mongodb-extensions",
                    "django_mongodb_extensions",
                    "mongo_settings.py",
                ),
            },
            "module": {
                "test": "django_mongodb_extensions.mongo_settings",
                "migrations": "django_mongodb_extensions.mongo_settings",
            },
        },
        "test_dirs": [
            join(
                "src", "django-mongodb-extensions", "django_mongodb_extensions", "tests"
            ),
        ],
    },
    "django-allauth": {
        "test_command": "pytest",
        "test_dir": join("src", "django-allauth"),
        "clone_dir": join("src", "django-allauth"),
        "apps_file": {
            "source": join("config", "allauth", "allauth_apps.py"),
            "target": join("src", "django-allauth", "allauth", "mongo_apps.py"),
        },
        "settings": {
            "test": {
                "source": join("config", "allauth", "allauth_settings.py"),
                "target": join("src", "django-allauth", "allauth", "mongo_settings.py"),
            },
            "migrations": {
                "source": join("config", "allauth", "allauth_settings.py"),
                "target": join("src", "django-allauth", "allauth", "mongo_settings.py"),
            },
            "module": {
                "test": "allauth.mongo_settings",
                "migrations": "allauth.mongo_settings",
            },
        },
        "migrations_dir": {
            "source": join("src", "django-mongodb-project", "mongo_migrations"),
            "target": join("src", "django-allauth", "allauth", "mongo_migrations"),
        },
        "test_dirs": [
            join("src", "django-allauth", "allauth", "usersessions", "tests"),
            join("src", "django-allauth", "allauth", "core", "tests"),
            join("src", "django-allauth", "allauth", "core", "internal", "tests"),
            join("src", "django-allauth", "allauth", "tests"),
            join("src", "django-allauth", "allauth", "mfa", "recovery_codes", "tests"),
            join("src", "django-allauth", "allauth", "mfa", "webauthn", "tests"),
            join("src", "django-allauth", "allauth", "mfa", "totp", "tests"),
            join("src", "django-allauth", "allauth", "mfa", "base", "tests"),
            join(
                "src",
                "django-allauth",
                "allauth",
                "socialaccount",
                "providers",
                "oauth2",
                "tests",
            ),
            join("src", "django-allauth", "allauth", "socialaccount", "tests"),
            join(
                "src", "django-allauth", "allauth", "socialaccount", "internal", "tests"
            ),
            join("src", "django-allauth", "allauth", "templates", "tests"),
            join(
                "src", "django-allauth", "allauth", "headless", "usersessions", "tests"
            ),
            join("src", "django-allauth", "allauth", "headless", "tests"),
            join("src", "django-allauth", "allauth", "headless", "spec", "tests"),
            join("src", "django-allauth", "allauth", "headless", "internal", "tests"),
            join("src", "django-allauth", "allauth", "headless", "mfa", "tests"),
            join(
                "src", "django-allauth", "allauth", "headless", "socialaccount", "tests"
            ),
            join(
                "src",
                "django-allauth",
                "allauth",
                "headless",
                "contrib",
                "ninja",
                "tests",
            ),
            join(
                "src",
                "django-allauth",
                "allauth",
                "headless",
                "contrib",
                "rest_framework",
                "tests",
            ),
            join("src", "django-allauth", "allauth", "headless", "account", "tests"),
            join("src", "django-allauth", "allauth", "headless", "base", "tests"),
            join("src", "django-allauth", "allauth", "account", "tests"),
            join("src", "django-allauth", "tests"),
        ],
    },
}
