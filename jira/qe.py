from bson.codec_options import CodecOptions
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption, AutoEncryptionOpts
from pymongo.errors import EncryptedCollectionError

from django_mongodb_backend.encryption import KMS_PROVIDERS

KEY_VAULT_NAMESPACE = "encryption.__keyVault"

client = MongoClient(
    auto_encryption_opts=AutoEncryptionOpts(
        key_vault_namespace=KEY_VAULT_NAMESPACE,
        kms_providers=KMS_PROVIDERS,
    )
)

codec_options = CodecOptions()
client_encryption = ClientEncryption(
    KMS_PROVIDERS, KEY_VAULT_NAMESPACE, client, codec_options
)

COLLECTION_NAME = "patient"
DB_NAME = "qe"
client.drop_database(DB_NAME)
database = client[DB_NAME]

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
    collection = client_encryption.create_encrypted_collection(
        database, "patient", encrypted_fields, "local"
    )
    patient = {
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
    collection = client[DB_NAME][COLLECTION_NAME]
    collection.insert_one(patient)
    print(collection.find_one({"patientRecord.ssn": "987-65-4320"}))

except EncryptedCollectionError as e:
    print(f"Encrypted collection error: {e}")
