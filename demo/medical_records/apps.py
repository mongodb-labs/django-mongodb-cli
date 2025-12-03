from django.apps import AppConfig


class MedicalRecordsConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "demo.medical_records"
