from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from pymongo.errors import EncryptedCollectionError
from django_mongodb_backend.encryption import (
    get_auto_encryption_opts,
    get_kms_providers,
    get_key_vault_namespace,
)

kms_providers = get_kms_providers()
key_vault_namespace = get_key_vault_namespace()

client = MongoClient(
    auto_encryption_opts=get_auto_encryption_opts(
        key_vault_namespace=key_vault_namespace,
        kms_providers=kms_providers,
    )
)

codec_options = CodecOptions(uuid_representation=STANDARD)
client_encryption = ClientEncryption(
    kms_providers, key_vault_namespace, client, codec_options
)

client.drop_database("test")

database = client["test"]

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
try:
    encrypted_collection = client_encryption.create_encrypted_collection(
        database, "encrypted_collection", encrypted_fields, "local"
    )
    patient_document = {
        "patientName": "Jon Doe",
        "patientId": 12345678,
        "patientRecord": {
            "ssn": "987-65-4320",
            "billing": {
                "type": "Visa",
                "number": "4111111111111111",
            },
            "billAmount": 1500,
        },
    }
    encrypted_collection = client["test"]["encrypted_collection"]
    encrypted_collection.insert_one(patient_document)
    print(encrypted_collection.find_one({"patientRecord.ssn": "987-65-4320"}))

except EncryptedCollectionError as e:
    print(f"Encrypted collection error: {e}")
