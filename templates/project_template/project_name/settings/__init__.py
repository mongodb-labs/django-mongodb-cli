import os

from bson import ObjectId
from django_mongodb_backend import parse_uri


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.path.dirname(PROJECT_DIR)

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

INSTALLED_APPS = [
    "{{ project_name }}.mongo_apps.MongoWagtailFormsAppConfig",
    "{{ project_name }}.mongo_apps.MongoWagtailRedirectsAppConfig",
    "{{ project_name }}.mongo_apps.MongoWagtailEmbedsAppConfig",
    "wagtail.sites",
    "{{ project_name }}.mongo_apps.MongoWagtailUsersAppConfig",
    "wagtail.snippets",
    "{{ project_name }}.mongo_apps.MongoWagtailDocsAppConfig",
    "{{ project_name }}.mongo_apps.MongoWagtailImagesAppConfig",
    "{{ project_name }}.mongo_apps.MongoWagtailSearchAppConfig",
    "{{ project_name }}.mongo_apps.MongoWagtailAdminAppConfig",
    "{{ project_name }}.mongo_apps.MongoWagtailAppConfig",
    "modelcluster",
    "{{ project_name }}.mongo_apps.MongoTaggitAppConfig",
    "{{ project_name }}.mongo_apps.MongoAdminConfig",
    "{{ project_name }}.mongo_apps.MongoAuthConfig",
    "{{ project_name }}.mongo_apps.MongoContentTypesConfig",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "webpack_boilerplate",
    "debug_toolbar",
    "home",
    "django_mongodb_extensions",
]

MIGRATION_MODULES = {
    "admin": "mongo_migrations.admin",
    "auth": "mongo_migrations.auth",
    "contenttypes": "mongo_migrations.contenttypes",
    "taggit": "mongo_migrations.taggit",
    "wagtaildocs": "mongo_migrations.wagtaildocs",
    "wagtailredirects": "mongo_migrations.wagtailredirects",
    "wagtailimages": "mongo_migrations.wagtailimages",
    "wagtailsearch": "mongo_migrations.wagtailsearch",
    "wagtailadmin": "mongo_migrations.wagtailadmin",
    "wagtailcore": "mongo_migrations.wagtailcore",
    "wagtailforms": "mongo_migrations.wagtailforms",
    "wagtailembeds": "mongo_migrations.wagtailembeds",
    "wagtailusers": "mongo_migrations.wagtailusers",
}

DATABASES = {
    "default": parse_uri(
        os.environ.get("MONGODB_URI", "mongodb://localhost:27017/{{ project_name }}")
    )
}

DEBUG = True

ROOT_URLCONF = "{{ project_name }}.urls"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "frontend", "build")]

WEBPACK_LOADER = {
    "MANIFEST_FILE": os.path.join(BASE_DIR, "frontend", "build", "manifest.json")
}

SECRET_KEY = "{{ secret_key }}"

ALLOWED_HOSTS = ["*"]

STATIC_URL = "static/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join("{{ project_name }}", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

WAGTAIL_SITE_NAME = "{{ project_name }}"

INTERNAL_IPS = [
    "127.0.0.1",
]

SITE_ID = ObjectId("000000000000000000000001")


DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "django_mongodb_extensions.debug_toolbar.panels.mql.MQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.alerts.AlertsPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
