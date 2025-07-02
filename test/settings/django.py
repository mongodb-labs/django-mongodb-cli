import os

from django_mongodb_backend import encryption, parse_uri

kms_providers = encryption.get_kms_providers()

auto_encryption_opts = encryption.get_auto_encryption_opts(
    kms_providers=kms_providers,
)

DATABASE_URL = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DATABASES = {
    "default": parse_uri(
        DATABASE_URL,
        db_name="djangotests",
    ),
    "encrypted": parse_uri(
        DATABASE_URL,
        options={"auto_encryption_opts": auto_encryption_opts},
        db_name="encrypted_djangotests",
    ),
}

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
SECRET_KEY = "django_tests_secret_key"
USE_TZ = False
