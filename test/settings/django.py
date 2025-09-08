import os

from bson.binary import Binary

# from django_mongodb_backend import encryption, parse_uri
from django_mongodb_backend import parse_uri

# from pymongo.encryption import AutoEncryptionOpts

EXPECTED_ENCRYPTED_FIELDS_MAP = {
    "billing": {
        "fields": [
            {
                "bsonType": "string",
                "path": "cc_type",
                "queries": {"queryType": "equality"},
                "keyId": Binary(b" \x901\x89\x1f\xafAX\x9b*\xb1\xc7\xc5\xfdl\xa4", 4),
            },
            {
                "bsonType": "long",
                "path": "cc_number",
                "queries": {"queryType": "equality"},
                "keyId": Binary(
                    b"\x97\xb4\x9d\xb8\xd5\xa6Ay\x85\xfe\x00\xc0\xd4{\xa2\xff", 4
                ),
            },
            {
                "bsonType": "decimal",
                "path": "account_balance",
                "queries": {"queryType": "range"},
                "keyId": Binary(b"\xcc\x01-s\xea\xd9B\x8d\x80\xd7\xf8!n\xc6\xf5U", 4),
            },
        ]
    },
    "patientrecord": {
        "fields": [
            {
                "bsonType": "string",
                "path": "ssn",
                "queries": {"queryType": "equality"},
                "keyId": Binary(
                    b"\x14F\x89\xde\x8d\x04K7\xa9\x9a\xaf_\xca\x8a\xfb&", 4
                ),
            },
            {
                "bsonType": "date",
                "path": "birth_date",
                "queries": {"queryType": "range"},
                "keyId": Binary(b"@\xdd\xb4\xd2%\xc2B\x94\xb5\x07\xbc(ER[s", 4),
            },
            {
                "bsonType": "binData",
                "path": "profile_picture",
                "queries": {"queryType": "equality"},
                "keyId": Binary(b"Q\xa2\xebc!\xecD,\x8b\xe4$\xb6ul9\x9a", 4),
            },
            {
                "bsonType": "int",
                "path": "patient_age",
                "queries": {"queryType": "range"},
                "keyId": Binary(b"\ro\x80\x1e\x8e1K\xde\xbc_\xc3bi\x95\xa6j", 4),
            },
            {
                "bsonType": "double",
                "path": "weight",
                "queries": {"queryType": "range"},
                "keyId": Binary(
                    b"\x9b\xfd:n\xe1\xd0N\xdd\xb3\xe7e)\x06\xea\x8a\x1d", 4
                ),
            },
        ]
    },
    "patient": {
        "fields": [
            {
                "bsonType": "int",
                "path": "patient_id",
                "queries": {"queryType": "equality"},
                "keyId": Binary(b"\x8ft\x16:\x8a\x91D\xc7\x8a\xdf\xe5O\n[\xfd\\", 4),
            },
            {
                "bsonType": "string",
                "path": "patient_name",
                "keyId": Binary(
                    b"<\x9b\xba\xeb:\xa4@m\x93\x0e\x0c\xcaN\x03\xfb\x05", 4
                ),
            },
            {
                "bsonType": "string",
                "path": "patient_notes",
                "queries": {"queryType": "equality"},
                "keyId": Binary(b"\x01\xe7\xd1isnB$\xa9(gwO\xca\x10\xbd", 4),
            },
            {
                "bsonType": "date",
                "path": "registration_date",
                "queries": {"queryType": "equality"},
                "keyId": Binary(b"F\xfb\xae\x82\xd5\x9a@\xee\xbfJ\xaf#\x9c:-I", 4),
            },
            {
                "bsonType": "bool",
                "path": "is_active",
                "queries": {"queryType": "equality"},
                "keyId": Binary(b"\xb2\xb5\xc4K53A\xda\xb9V\xa6\xa9\x97\x94\xea;", 4),
            },
        ]
    },
}
# DATABASE_ROUTERS = [encryption.EncryptedRouter()]
DATABASE_URL = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
# KEY_VAULT_NAMESPACE = "encrypted.__keyvault"
DATABASES = {
    "default": parse_uri(
        DATABASE_URL,
        db_name="test",
    ),
    # "other": parse_uri(
    #     DATABASE_URL,
    #     options={
    #         "auto_encryption_opts": AutoEncryptionOpts(
    #             key_vault_namespace=KEY_VAULT_NAMESPACE,
    #             kms_providers={
    #                 "local": {"key": encryption.KMS_CREDENTIALS["local"]["key"]}
    #             },
    #             # schema_map=EXPECTED_ENCRYPTED_FIELDS_MAP,
    #         )
    #     },
    #     db_name="other",
    # ),
}
# DATABASES["other"]["KMS_CREDENTIALS"] = encryption.KMS_CREDENTIALS

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
SECRET_KEY = "django_tests_secret_key"
USE_TZ = False
