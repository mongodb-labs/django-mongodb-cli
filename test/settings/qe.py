import os


from pymongo.encryption import AutoEncryptionOpts
from django_mongodb_backend.utils import model_has_encrypted_fields


MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "NAME": "django_mongodb_backend",
        "HOST": MONGODB_URI,
    },
    "encrypted": {
        "ENGINE": "django_mongodb_backend",
        "NAME": "encrypted",
        "HOST": MONGODB_URI,
        "OPTIONS": {
            "auto_encryption_opts": AutoEncryptionOpts(
                key_vault_namespace="encrypted.keyvault",
                kms_providers={
                    "local": {"key": os.urandom(96)},
                },
            ),
        },
    },
}


class EncryptedRouter:
    def db_for_read(self, model, **hints):
        if model_has_encrypted_fields(model):
            return "encrypted"
        return "default"

    def db_for_write(self, model, **hints):
        if model_has_encrypted_fields(model):
            return "encrypted"
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if hints.get("model"):
            if model_has_encrypted_fields(hints["model"]):
                return db == "encrypted"
            else:
                return db == "default"
        return None

    def kms_provider(self, model):
        if model_has_encrypted_fields(model):
            return "local"
        return None


DATABASE_ROUTERS = [EncryptedRouter()]
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
SECRET_KEY = "django_tests_secret_key"
USE_TZ = False
