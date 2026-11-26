from django.urls import path

from .views import CompanyApi, ComplaintsApi, EmployeesApi, ProjectsApi, ServicesApi

app_name = "api"

urlpatterns = [
    path("company/", CompanyApi.as_view(), name="company"),
    path("services/", ServicesApi.as_view(), name="services"),
    path("employees/", EmployeesApi.as_view(), name="employees"),
    path("projects/", ProjectsApi.as_view(), name="projects"),
    path("complaints/", ComplaintsApi.as_view(), name="complaints"),
]
