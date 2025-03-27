from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from allauth.account.apps import AccountConfig
from allauth.socialaccount.apps import SocialAccountConfig
from allauth.usersessions.apps import UserSessionsConfig
from allauth.mfa.apps import MFAConfig
from allauth.headless.apps import HeadlessConfig


class MongoAdminConfig(AdminConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoHeadlessConfig(HeadlessConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoMFAConfig(MFAConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoUserSessionsConfig(UserSessionsConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAccountConfig(AccountConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoSocialAccountConfig(SocialAccountConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
