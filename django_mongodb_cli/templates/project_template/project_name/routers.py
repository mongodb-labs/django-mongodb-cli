class EncryptedRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "django_mongodb_demo":
            return "encrypted"
        return None

    db_for_write = db_for_read

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "django_mongodb_demo":
            print("allow_migrate for django_mongodb_demo:", db)
            return db == "encrypted"
        # Don't create other app's models in the encrypted database.
        if db == "encrypted":
            return False
        return None

    def kms_provider(self, model, **hints):
        return "local"
