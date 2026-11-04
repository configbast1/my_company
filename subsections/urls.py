from django.urls import path

from .views import SubsectionView

app_name = "subsections"

urlpatterns = [
    path("<slug:section>/<slug:subsection>/", SubsectionView.as_view(), name="detail"),
]
