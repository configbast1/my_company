from django.contrib import admin
from django.urls import include, path

from main.panel import AdminPanelView
from main.views import ComplaintView

urlpatterns = [
    path("admin/", admin.site.urls),
    # власна адмінка «Моя компанія» (стоїть до шаблону /<розділ>/)
    path("panel/", AdminPanelView.as_view(), name="panel"),
    # форма «Скарга на товар або послугу»
    path("complaint/", ComplaintView.as_view(), name="complaint"),
    # підрозділи (окремий додаток): /<розділ>/<підрозділ>/
    path("", include("subsections.urls")),
    # головна та 5 розділів: /, /<розділ>/
    path("", include("main.urls")),
]
