import os

from django_mongodb_backend import encryption, parse_uri

# Queryable Encryption settings
KEY_VAULT_NAMESPACE = encryption.get_key_vault_namespace()
KMS_PROVIDERS = encryption.get_kms_providers()
KMS_PROVIDER = encryption.KMS_PROVIDER
AUTO_ENCRYPTION_OPTS = encryption.get_auto_encryption_opts(
    key_vault_namespace=KEY_VAULT_NAMESPACE,
    kms_providers=KMS_PROVIDERS,
)

ENCRYPTED_DB_ALIAS = encryption.ENCRYPTED_DB_ALIAS
ENCRYPTED_APPS = encryption.ENCRYPTED_APPS

DATABASE_URL = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DATABASES = {
    "default": parse_uri(
        DATABASE_URL,
        db_name="test",
    ),
    ENCRYPTED_DB_ALIAS: parse_uri(
        DATABASE_URL,
        options={"auto_encryption_opts": AUTO_ENCRYPTION_OPTS},
        db_name=ENCRYPTED_DB_ALIAS,
    ),
}

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
SECRET_KEY = "django_tests_secret_key"
USE_TZ = False

DATABASE_ROUTERS = [encryption.EncryptedRouter()]
