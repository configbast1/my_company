from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

from . import storage


class RegisterForm(forms.Form):
    username = forms.CharField(
        label="Логін",
        min_length=3,
        max_length=30,
        validators=[RegexValidator(
            r"^[A-Za-z0-9_.-]+$",
            "Лише латинські літери, цифри та символи _ . -",
        )],
        widget=forms.TextInput(attrs={"placeholder": "ivan_petrenko", "autocomplete": "username"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "ivan@example.com", "autocomplete": "email"}),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Мінімум 8 символів", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Підтвердження пароля",
        widget=forms.PasswordInput(attrs={"placeholder": "Повторіть пароль", "autocomplete": "new-password"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if storage.username_taken(username):
            raise forms.ValidationError("Цей логін уже зайнятий.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if storage.email_taken(email):
            raise forms.ValidationError("Користувач з таким email уже зареєстрований.")
        return email

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        validate_password(password)  # стандартні правила Django: довжина, не лише цифри...
        return password

    def clean(self):
        data = super().clean()
        if data.get("password1") and data.get("password2") and data["password1"] != data["password2"]:
            self.add_error("password2", "Паролі не збігаються.")
        return data


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Логін",
        widget=forms.TextInput(attrs={"placeholder": "Ваш логін", "autocomplete": "username", "autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Ваш пароль", "autocomplete": "current-password"}),
    )

    def clean(self):
        data = super().clean()
        if data.get("username") and data.get("password"):
            self.user = storage.authenticate(data["username"], data["password"])
            if self.user is None:
                raise forms.ValidationError("Невірний логін або пароль.")
        return data
