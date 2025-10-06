# {{ project_name }} settings module.

from .base import *  # noqa
from pymongo.encryption_options import AutoEncryptionOpts
from bson import ObjectId

# Queryable Encryption
INSTALLED_APPS += [  # noqa
    "django_mongodb_backend",
    "django_mongodb_demo",
]

DATABASES["encrypted"] = {  # noqa
    "ENGINE": "django_mongodb_backend",
    "HOST": os.getenv("MONGODB_URI"),  # noqa
    "NAME": "{{ project_name }}_encrypted",
    "OPTIONS": {
        "auto_encryption_opts": AutoEncryptionOpts(
            kms_providers={"local": {"key": os.urandom(96)}},  # noqa
            key_vault_namespace="keyvault.__keyVault",
        ),
    },
}

DATABASE_ROUTERS = ["{{project_name}}.routers.EncryptedRouter"]

# Sites framework
SITE_ID = ObjectId("000000000000000000000001")
SILENCED_SYSTEM_CHECKS = [
    "sites.E101",
]
INSTALLED_APPS += [
    "{{ project_name }}.apps.MongoDBSitesConfig",
]

# Flatpages and Redirects
INSTALLED_APPS += [
    "{{ project_name }}.apps.MongoDBFlatPagesConfig",
    "{{ project_name }}.apps.MongoDBRedirectsConfig",
]
