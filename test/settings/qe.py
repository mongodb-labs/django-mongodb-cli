import os


from pymongo.encryption import AutoEncryptionOpts


MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")

# Configure KMS providers.
#
# We prefer AWS when FLE_AWS_KEY/FLE_AWS_SECRET are set, mirroring
# src/mongo-python-driver/test/helpers_shared.py. Otherwise we fall back
# to a local KMS for convenience in local development.
AWS_CREDS = {
    "accessKeyId": os.environ.get("FLE_AWS_KEY", ""),
    "secretAccessKey": os.environ.get("FLE_AWS_SECRET", ""),
}
_USE_AWS_KMS = any(AWS_CREDS.values())

if _USE_AWS_KMS:
    # Use the same demo key ARN and region as the PyMongo QE tests.
    _AWS_REGION = os.environ.get("FLE_AWS_KMS_REGION", "us-east-1")
    _AWS_KEY_ARN = os.environ.get(
        "FLE_AWS_KMS_KEY_ARN",
        "arn:aws:kms:us-east-1:579766882180:key/89fcc2c4-08b0-4bd9-9f25-e30687b580d0",
    )
    KMS_PROVIDERS = {"aws": AWS_CREDS}
    KMS_CREDENTIALS = {"aws": {"key": _AWS_KEY_ARN, "region": _AWS_REGION}}
    DEFAULT_KMS_PROVIDER = "aws"
else:
    pass
    # Local-only fallback: matches the original configuration.
    # KMS_PROVIDERS = {"local": {"key": os.urandom(96)}}
    # KMS_CREDENTIALS = {"aws": {}}
    # DEFAULT_KMS_PROVIDER = "local"


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
                kms_providers=KMS_PROVIDERS,
            ),
        },
        "KMS_CREDENTIALS": KMS_CREDENTIALS,
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
        return DEFAULT_KMS_PROVIDER


DATABASE_ROUTERS = ["django_mongodb_backend.routers.MongoRouter", EncryptedRouter()]
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
SECRET_KEY = "django_tests_secret_key"
USE_TZ = False
