from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import FormView

from . import storage
from .forms import LoginForm, RegisterForm


class AnonymousOnlyMixin:
    """Авторизованого користувача з входу/реєстрації одразу ведемо на головну."""

    def dispatch(self, request, *args, **kwargs):
        if storage.current_user(request):
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(AnonymousOnlyMixin, FormView):
    """Реєстрація: логін, email, пароль з підтвердженням, потім одразу вхід."""
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        data = form.cleaned_data
        user = storage.create_user(data["username"], data["email"], data["password1"])
        storage.login(self.request, user)
        messages.success(self.request, "Реєстрація успішна. Ласкаво просимо!")
        return super().form_valid(form)


class LoginView(AnonymousOnlyMixin, FormView):
    """Вхід за логіном і паролем, після входу - на сторінку з ?next= або на головну."""
    form_class = LoginForm
    template_name = "accounts/login.html"

    def get_success_url(self):
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={self.request.get_host()}, require_https=self.request.is_secure()
        ):
            return next_url
        return reverse("home")

    def form_valid(self, form):
        storage.login(self.request, form.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.POST.get("next") or self.request.GET.get("next", "")
        return context


class LogoutView(View):
    """Вихід тільки POST-запитом (захист від виходу через стороннє посилання)."""

    def post(self, request):
        storage.logout(request)
        messages.info(request, "Ви вийшли з облікового запису.")
        return redirect("accounts:login")
