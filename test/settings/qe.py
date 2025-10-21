import os


from pymongo.encryption import AutoEncryptionOpts
from django_mongodb_backend.utils import model_has_encrypted_fields


MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")

KMS_CREDENTIALS = {
    "local": {
        "key": os.urandom(96),
    },
}
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "NAME": "djangotests",
        "HOST": MONGODB_URI,
    },
    "other": {
        "ENGINE": "django_mongodb_backend",
        "NAME": "other",
        "HOST": MONGODB_URI,
    },
    "encrypted": {
        "ENGINE": "django_mongodb_backend",
        "NAME": "djangotests_encrypted",
        "HOST": MONGODB_URI,
        "OPTIONS": {
            "auto_encryption_opts": AutoEncryptionOpts(
                key_vault_namespace="djangotests_encrypted.__keyVault",
                kms_providers=KMS_CREDENTIALS,
            ),
        },
    },
}


class EncryptedRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if hints.get("model"):
            if model_has_encrypted_fields(hints["model"]):
                return db == "encrypted"
            else:
                return db == "default"
        return None

    def db_for_read(self, model, **hints):
        if model_has_encrypted_fields(model):
            return "encrypted"
        return "default"

    def kms_provider(self, model):
        if model_has_encrypted_fields(model):
            return "local"
        return None

    db_for_write = db_for_read


DATABASE_ROUTERS = [EncryptedRouter()]
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
SECRET_KEY = "django_tests_secret_key"
USE_TZ = False
