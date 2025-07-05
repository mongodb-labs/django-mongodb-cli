from bson import ObjectId
from django.db import migrations

# Do not use settings in migrations under normal circumstances.
from django.conf import settings


def create_homepage(apps, schema_editor):
    # Get models
    ContentType = apps.get_model("contenttypes.ContentType")
    Page = apps.get_model("wagtailcore.Page")
    Site = apps.get_model("wagtailcore.Site")
    HomePage = apps.get_model("home.HomePage")

    # Delete the default homepage
    # If migration is run multiple times, it may have already been deleted
    Page.objects.filter(id=ObjectId("000000000000000000000001")).delete()

    # Create content type for homepage model
    homepage_content_type, __ = ContentType.objects.get_or_create(
        model="homepage", app_label="home"
    )

    # Why this is needed in MongoDB and not in PostgreSQL?
    locale = None
    if settings.DATABASES["default"]["ENGINE"] == "django_mongodb_backend":
        Locale = apps.get_model("wagtailcore.Locale")
        locale = Locale.objects.get(language_code="en")

    # Create a new homepage
    homepage_attrs = {
        "title": "Home",
        "draft_title": "Home",
        "slug": "home",
        "content_type": homepage_content_type,
        "path": "00010001",
        "depth": 1,
        "numchild": 0,
        "url_path": "/home/",
    }
    # Add the locale only if it's defined
    if locale:
        homepage_attrs["locale"] = locale

    homepage = HomePage.objects.create(**homepage_attrs)

    # Create a site with the new homepage set as the root
    Site.objects.create(hostname="localhost", root_page=homepage, is_default_site=True)


def remove_homepage(apps, schema_editor):
    # Get models
    ContentType = apps.get_model("contenttypes.ContentType")
    HomePage = apps.get_model("home.HomePage")

    # Delete the default homepage
    # Page and Site objects CASCADE
    HomePage.objects.filter(slug="home", depth=2).delete()

    # Delete content type for homepage model
    ContentType.objects.filter(model="homepage", app_label="home").delete()


def create_locale(apps, schema_editor):
    Locale = apps.get_model("wagtailcore", "Locale")
    # Replace 'en' with your desired language code and add other fields as necessary.
    Locale.objects.create(language_code="en")


def remove_locale(apps, schema_editor):
    Locale = apps.get_model("wagtailcore", "Locale")
    # Replace 'en' with the language code used in create_locale
    Locale.objects.filter(language_code="en").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_homepage, remove_homepage),
    ]

    if settings.DATABASES["default"]["ENGINE"] == "django_mongodb_backend":
        operations.insert(0, migrations.RunPython(create_locale, remove_locale))
