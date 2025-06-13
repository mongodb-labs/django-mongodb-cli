import code

from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from django_mongodb_backend.utils import get_auto_encryption_options

encrypted_client = MongoClient(
    auto_encryption_opts=get_auto_encryption_options(
        crypt_shared_lib_path="/Users/alexclark/Downloads/mongo_crypt_shared_v1-macos-arm64-enterprise-8.0.10/lib/mongo_crypt_v1.dylib"
    )
)
kms_providers = encrypted_client.options.auto_encryption_opts._kms_providers
key_vault_namespace = encrypted_client.options.auto_encryption_opts._key_vault_namespace
codec_options = CodecOptions(uuid_representation=STANDARD)
client_encryption = ClientEncryption(
    kms_providers, key_vault_namespace, encrypted_client, codec_options
)
encrypted_database = encrypted_client["test"]
encrypted_fields = {
    "fields": [
        {
            "path": "patientRecord.ssn",
            "bsonType": "string",
            "queries": [{"queryType": "equality"}],
        },
        {
            "path": "patientRecord.billing",
            "bsonType": "object",
        },
    ]
}
encrypted_collection = client_encryption.create_encrypted_collection(
    encrypted_database, "encrypted_collection", encrypted_fields
)
code.interact(local=locals())
