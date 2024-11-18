import django_mongodb_backend
import os


MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/djangotests")
DATABASES = {
    "default": django_mongodb_backend.parse_uri(MONGODB_URI),
}
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
SECRET_KEY = "django_tests_secret_key"
USE_TZ = False
