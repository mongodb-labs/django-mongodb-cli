import os


from pymongo.encryption import AutoEncryptionOpts


MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")

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
                kms_providers={
                    "local": {
                        "key": os.urandom(96),
                    },
                },
            ),
        },
        "KMS_CREDENTIALS": {
            "aws": {},
        },
    },
}


class EncryptedRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "encryption_":
            return "encrypted"
        return None

    db_for_write = db_for_read

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # The encryption_ app's models are only created in the encrypted
        # database.
        if app_label == "encryption_":
            return db == "encrypted"
        # Don't create other app's models in the encrypted database.
        if db == "encrypted":
            return False
        return None

    def kms_provider(self, model):
        return "local"


DATABASE_ROUTERS = ["django_mongodb_backend.routers.MongoRouter", EncryptedRouter()]
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
SECRET_KEY = "django_tests_secret_key"
USE_TZ = False
