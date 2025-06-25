import os

from django_mongodb_backend import encryption, parse_uri

kms_providers = encryption.get_kms_providers()

HOME = os.environ.get("HOME")

auto_encryption_opts = encryption.get_auto_encryption_opts(
    kms_providers=kms_providers,
    crypt_shared_lib_path=f"{HOME}/Downloads/mongo_crypt_shared_v1-macos-arm64-enterprise-8.0.10/lib/mongo_crypt_v1.dylib",
)

DATABASE_URL = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/djangotests")
DATABASES = {
    "default": parse_uri(
        DATABASE_URL, options={"auto_encryption_opts": auto_encryption_opts}
    ),
}

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
SECRET_KEY = "django_tests_secret_key"
USE_TZ = False
