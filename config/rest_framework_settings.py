import os

import django
import django_mongodb_backend
from bson import ObjectId
from django.core import management

DATABASE_URL = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/djangotests")


def pytest_addoption(parser):
    parser.addoption(
        "--staticfiles",
        action="store_true",
        default=False,
        help="Run tests with static files collection, using manifest "
        "staticfiles storage. Used for testing the distribution.",
    )


def pytest_configure(config):
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            "default": django_mongodb_backend.parse_uri(DATABASE_URL),
        },
        SITE_ID=ObjectId(),
        SECRET_KEY="not very secret in tests",
        USE_I18N=True,
        STATIC_URL="/static/",
        ROOT_URLCONF="tests.urls",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {
                    "debug": True,  # We want template errors to raise
                },
            },
        ],
        MIDDLEWARE=(
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ),
        INSTALLED_APPS=(
            "tests.mongo_apps.MongoAdminConfig",
            "tests.mongo_apps.MongoAuthConfig",
            "tests.mongo_apps.MongoContentTypesConfig",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.staticfiles",
            "rest_framework",
            "rest_framework.authtoken",
            "tests.authentication",
            "tests.generic_relations",
            "tests.importable",
            "tests",
        ),
        PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",),
        DEFAULT_AUTO_FIELD="django_mongodb_backend.fields.ObjectIdAutoField",
        MIGRATION_MODULES={
            "admin": "tests.mongo_migrations.admin",
            "auth": "tests.mongo_migrations.auth",
            "contenttypes": "tests.mongo_migrations.contenttypes",
            "rest_framework": None,
            "generic_relations": None,
        },
    )

    # guardian is optional
    try:
        import guardian  # NOQA
    except ImportError:
        pass
    else:
        settings.ANONYMOUS_USER_ID = -1
        settings.AUTHENTICATION_BACKENDS = (
            "django.contrib.auth.backends.ModelBackend",
            "guardian.backends.ObjectPermissionBackend",
        )
        settings.INSTALLED_APPS += ("guardian",)

    # Manifest storage will raise an exception if static files are not present (ie, a packaging failure).
    if config.getoption("--staticfiles"):
        import rest_framework

        settings.STATIC_ROOT = os.path.join(
            os.path.dirname(rest_framework.__file__), "static-root"
        )
        backend = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        settings.STORAGES["staticfiles"]["BACKEND"] = backend

    django.setup()

    if config.getoption("--staticfiles"):
        management.call_command("collectstatic", verbosity=0, interactive=False)
