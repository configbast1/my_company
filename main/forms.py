from django import forms

from .models import Client, Department, Employee, Project, Service

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "floor", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["full_name", "position", "email", "department", "hire_date"]
        widgets = {"hire_date": DATE}


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["title", "price_from", "is_active", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["company_name", "contact_person", "phone", "email", "country"]


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "client", "status", "start_date", "services"]
        widgets = {"start_date": DATE, "services": forms.CheckboxSelectMultiple}
