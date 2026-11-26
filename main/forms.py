from django import forms

from .models import Client, Complaint, Department, Employee, Project, Service

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


class ComplaintForm(forms.ModelForm):
    """Форма «Скарга на товар або послугу» для відвідувачів сайту."""
    agree = forms.BooleanField(
        label="Я погоджуюсь на обробку персональних даних",
        error_messages={"required": "Без згоди ми не можемо прийняти скаргу."},
    )

    class Meta:
        model = Complaint
        fields = [
            "full_name", "email", "phone",
            "complaint_type", "service", "product_name", "order_number", "purchase_date",
            "subject", "description", "resolution", "wants_callback",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Іван Петренко"}),
            "email": forms.EmailInput(attrs={"placeholder": "ivan@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+38 (0__) ___-__-__"}),
            "complaint_type": forms.RadioSelect,
            "product_name": forms.TextInput(attrs={"placeholder": "Напр. ліцензія CRM «Старт»"}),
            "order_number": forms.TextInput(attrs={"placeholder": "Напр. TS-2026-0142"}),
            "purchase_date": DATE,
            "subject": forms.TextInput(attrs={"placeholder": "Коротко про проблему"}),
            "description": forms.Textarea(attrs={
                "rows": 5, "placeholder": "Що сталося, коли і що ви вже пробували зробити..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        self.fields["service"].empty_label = "— оберіть послугу —"

    def clean_description(self):
        text = self.cleaned_data["description"].strip()
        if len(text) < 20:
            raise forms.ValidationError("Опишіть проблему детальніше (мінімум 20 символів).")
        return text

    def clean(self):
        data = super().clean()
        kind = data.get("complaint_type")
        if kind == "service" and not data.get("service"):
            self.add_error("service", "Оберіть послугу, на яку скаржитесь.")
        if kind == "product" and not data.get("product_name"):
            self.add_error("product_name", "Вкажіть назву товару.")
        if data.get("wants_callback") and not data.get("phone"):
            self.add_error("phone", "Вкажіть телефон, щоб ми могли передзвонити.")
        return data
