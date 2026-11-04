from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # підрозділи (окремий додаток): /<розділ>/<підрозділ>/
    path("", include("subsections.urls")),
    # головна та 5 розділів: /, /<розділ>/
    path("", include("main.urls")),
]
