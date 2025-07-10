from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path, include
from django.contrib import admin
from .views import BaseView


urlpatterns = [
    path("django/", admin.site.urls),
    path("wagtail/", include("wagtail.admin.urls")),
    path("", BaseView.as_view(), name="base"),
] + debug_toolbar_urls()
