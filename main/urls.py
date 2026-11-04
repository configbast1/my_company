from django.urls import path

from .views import HomeView, SectionView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("<slug:section>/", SectionView.as_view(), name="section"),
]
