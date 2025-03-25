import os
import django_mongodb_backend

from bson import ObjectId
from django.contrib.messages import constants as message_constants
from django.utils.translation import gettext_lazy as _

from wagtail.test.numberformat import patch_number_formats
from django_mongodb_cli.utils import get_databases

WAGTAIL_CHECK_TEMPLATE_NUMBER_FORMAT = (
    os.environ.get("WAGTAIL_CHECK_TEMPLATE_NUMBER_FORMAT", "0") == "1"
)
if WAGTAIL_CHECK_TEMPLATE_NUMBER_FORMAT:
    # Patch Django number formatting functions to raise exceptions if a number is output directly
    # on a template (which is liable to cause bugs when USE_THOUSAND_SEPARATOR is in use).
    patch_number_formats()

DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
WAGTAIL_ROOT = os.path.dirname(os.path.dirname(__file__))
WAGTAILADMIN_BASE_URL = "http://testserver"
STATIC_ROOT = os.path.join(WAGTAIL_ROOT, "tests", "test-static")
MEDIA_ROOT = os.path.join(WAGTAIL_ROOT, "tests", "test-media")
MEDIA_URL = "/media/"

TIME_ZONE = "Asia/Tokyo"

DATABASES = get_databases("wagtail")

SECRET_KEY = "not needed"

ROOT_URLCONF = "wagtail.test.urls"

STATIC_URL = "/static/"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Default storage settings
# https://docs.djangoproject.com/en/stable/ref/settings/#std-setting-STORAGES
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

if os.environ.get("STATICFILES_STORAGE", "") == "manifest":
    STORAGES["staticfiles"]["BACKEND"] = (
        "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
    )


USE_TZ = not os.environ.get("DISABLE_TIMEZONE")
if not USE_TZ:
    print("Timezone support disabled")  # noqa: T201

LANGUAGE_CODE = "en"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "wagtail.test.context_processors.do_not_use_static_url",
                "wagtail.contrib.settings.context_processors.settings",
            ],
            "debug": True,  # required in order to catch template errors
        },
    },
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "APP_DIRS": False,
        "DIRS": [
            os.path.join(WAGTAIL_ROOT, "test", "testapp", "jinja2_templates"),
        ],
        "OPTIONS": {
            "extensions": [
                "wagtail.jinja2tags.core",
                "wagtail.admin.jinja2tags.userbar",
                "wagtail.images.jinja2tags.images",
                "wagtail.contrib.settings.jinja2tags.settings",
            ],
        },
    },
]

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.test.middleware.BlockDodgyUserAgentMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
)

INSTALLED_APPS = [
    # Place wagtail.test.earlypage first, to test the behaviour of page models
    # that are defined before wagtail.admin is loaded
    "wagtail.test.earlypage",
    # Install wagtailredirects with its appconfig
    # There's nothing special about wagtailredirects, we just need to have one
    # app which uses AppConfigs to test that hooks load properly
    "wagtail.test.mongo_apps.MongoWagtailRedirectsAppConfig",
    "wagtail.test.mongo_apps.MongoWagtailTestsAppConfig",
    "wagtail.test.mongo_apps.MongoDemositeAppConfig",
    "wagtail.test.routablepage",
    "wagtail.test.mongo_apps.MongoWagtailSearchAppConfig",
    "wagtail.test.mongo_apps.MongoI18nAppConfig",
    "wagtail.test.mongo_apps.MongoWagtailSnippetsAppConfig",
    "wagtail.test.mongo_apps.MongoSimpleTranslationAppConfig",
    "wagtail.contrib.styleguide",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.frontend_cache",
    "wagtail.test.mongo_apps.MongoWagtailSearchPromotionsAppConfig",
    "wagtail.contrib.settings",
    "wagtail.contrib.table_block",
    "wagtail.test.mongo_apps.MongoWagtailFormsAppConfig",
    "wagtail.contrib.typed_table_block",
    "wagtail.test.mongo_apps.MongoWagtailEmbedsAppConfig",
    "wagtail.test.mongo_apps.MongoWagtailImagesAppConfig",
    "wagtail.sites",
    "wagtail.locales",
    "wagtail.test.mongo_apps.MongoWagtailUsersAppConfig",
    "wagtail.test.mongo_apps.MongoWagtailDocsAppConfig",
    "wagtail.test.mongo_apps.MongoWagtailAdminAppConfig",
    "wagtail.api.v2",
    "wagtail.test.mongo_apps.MongoWagtailAppConfig",
    "wagtail.test.mongo_apps.MongoTaggitAppConfig",
    "rest_framework",
    "wagtail.test.mongo_apps.MongoAdminConfig",
    "wagtail.test.mongo_apps.MongoAuthConfig",
    "wagtail.test.mongo_apps.MongoContentTypesConfig",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django_extensions",
]

# Using DatabaseCache to make sure that the cache is cleared between tests.
# This prevents false-positives in some wagtail core tests where we are
# changing the 'wagtail_root_paths' key which may cause future tests to fail.
CACHES = {
    "default": {
        "BACKEND": "django_mongodb_backend.cache.MongoDBCache",
        "LOCATION": "cache",
    }
}

PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.MD5PasswordHasher",  # don't use the intentionally slow default password hasher
)

ALLOWED_HOSTS = [
    "localhost",
    "testserver",
    "other.example.com",
    "127.0.0.1",
    "0.0.0.0",
]

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database.fallback",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

if os.environ.get("USE_EMAIL_USER_MODEL"):
    INSTALLED_APPS.append("wagtail.test.emailuser")
    AUTH_USER_MODEL = "emailuser.EmailUser"
    print("EmailUser (no username) user model active")  # noqa: T201
else:
    INSTALLED_APPS.append("wagtail.test.customuser")
    AUTH_USER_MODEL = "customuser.CustomUser"
    # Extra user field for custom user edit and create form tests. This setting
    # needs to here because it is used at the module level of wagtailusers.forms
    # when the module gets loaded. The decorator 'override_settings' does not work
    # in this scenario.
    WAGTAIL_USER_CUSTOM_FIELDS = ["country", "attachment"]

if os.environ.get("DATABASE_ENGINE") == "django.db.backends.postgresql":
    WAGTAILSEARCH_BACKENDS["postgresql"] = {
        "BACKEND": "wagtail.search.backends.database",
        "AUTO_UPDATE": False,
        "SEARCH_CONFIG": "english",
    }

if "ELASTICSEARCH_URL" in os.environ:
    if os.environ.get("ELASTICSEARCH_VERSION") == "8":
        backend = "wagtail.search.backends.elasticsearch8"
    elif os.environ.get("ELASTICSEARCH_VERSION") == "7":
        backend = "wagtail.search.backends.elasticsearch7"

    WAGTAILSEARCH_BACKENDS["elasticsearch"] = {
        "BACKEND": backend,
        "URLS": [os.environ["ELASTICSEARCH_URL"]],
        "TIMEOUT": 10,
        "max_retries": 1,
        "AUTO_UPDATE": False,
        "INDEX_SETTINGS": {"settings": {"index": {"number_of_shards": 1}}},
    }


WAGTAIL_SITE_NAME = "Test Site"

WAGTAILADMIN_RICH_TEXT_EDITORS = {
    "default": {"WIDGET": "wagtail.admin.rich_text.DraftailRichTextArea"},
    "custom": {"WIDGET": "wagtail.test.testapp.rich_text.CustomRichTextArea"},
}

WAGTAIL_CONTENT_LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
]


# Set a non-standard DEFAULT_AUTHENTICATION_CLASSES value, to verify that the
# admin API still works with session-based auth regardless of this setting
# (see https://github.com/wagtail/wagtail/issues/5585)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
    ]
}

# Disable redirect autocreation for the majority of tests (to improve efficiency)
WAGTAILREDIRECTS_AUTO_CREATE = False


# https://github.com/wagtail/wagtail/issues/2551 - projects should be able to set
# MESSAGE_TAGS for their own purposes without them leaking into Wagtail admin styles.

MESSAGE_TAGS = {
    message_constants.DEBUG: "my-custom-tag",
    message_constants.INFO: "my-custom-tag",
    message_constants.SUCCESS: "my-custom-tag",
    message_constants.WARNING: "my-custom-tag",
    message_constants.ERROR: "my-custom-tag",
}

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/wagtail")
DATABASES["default"] = django_mongodb_backend.parse_uri(MONGODB_URI)

MIGRATION_MODULES = {
    "admin": None,
    "auth": None,
    "contenttypes": None,
    "customuser": None,
    "demosite": None,
    "earlypage": None,
    "i18n": None,
    "routablepagetests": None,
    "taggit": None,
    "tests": None,
    "wagtaildocs": None,
    "wagtailredirects": None,
    "wagtailimages": None,
    "wagtailsearch": None,
    "wagtailsearchpromotions": None,
    "wagtailadmin": None,
    "wagtailcore": None,
    "wagtailforms": None,
    "wagtailembeds": None,
    "wagtailusers": None,
}
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

SITE_ID = ObjectId("000000000000000000000001")
