from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from taggit.apps import TaggitAppConfig
from wagtail.documents.apps import WagtailDocsAppConfig
from wagtail.contrib.redirects.apps import WagtailRedirectsAppConfig
from wagtail.images.apps import WagtailImagesAppConfig
from wagtail.search.apps import WagtailSearchAppConfig
from wagtail.admin.apps import WagtailAdminAppConfig
from wagtail.apps import WagtailAppConfig
from wagtail.contrib.forms.apps import WagtailFormsAppConfig
from wagtail.embeds.apps import WagtailEmbedsAppConfig
from wagtail.users.apps import WagtailUsersAppConfig
from wagtail.test.demosite.apps import DemositeAppConfig
from wagtail.test.i18n.apps import I18nAppConfig
from wagtail.snippets.apps import WagtailSnippetsAppConfig
from wagtail.test.testapp.apps import WagtailTestsAppConfig
from wagtail.contrib.simple_translation.apps import SimpleTranslationAppConfig
from wagtail.contrib.search_promotions.apps import WagtailSearchPromotionsAppConfig


class MongoWagtailSearchPromotionsAppConfig(WagtailSearchPromotionsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoSimpleTranslationAppConfig(SimpleTranslationAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailTestsAppConfig(WagtailTestsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailSnippetsAppConfig(WagtailSnippetsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoI18nAppConfig(I18nAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoDemositeAppConfig(DemositeAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoTaggitAppConfig(TaggitAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailDocsAppConfig(WagtailDocsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAdminConfig(AdminConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailRedirectsAppConfig(WagtailRedirectsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailImagesAppConfig(WagtailImagesAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailSearchAppConfig(WagtailSearchAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailAdminAppConfig(WagtailAdminAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailAppConfig(WagtailAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailFormsAppConfig(WagtailFormsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailEmbedsAppConfig(WagtailEmbedsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailUsersAppConfig(WagtailUsersAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
