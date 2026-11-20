"""Власна адмінка «Моя компанія»: CRUD для всіх 5 моделей на одній сторінці."""
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from .forms import ClientForm, DepartmentForm, EmployeeForm, ProjectForm, ServiceForm
from .models import Client, Department, Employee, Project, Service


def _money(value):
    return f"{value:,.2f}".replace(",", " ")


# Опис кожної сутності: модель, форма, колонки таблиці, попередження при видаленні.
# Колонка = (заголовок, функція obj -> значення). Порядок словника = порядок вкладок.
ENTITIES = {
    "department": {
        "model": Department, "form": DepartmentForm, "icon": "🏢",
        "title": "Відділи", "one": "Відділ",
        "queryset": lambda: Department.objects.annotate(n=Count("employees")),
        "columns": [
            ("Назва", lambda o: o.name),
            ("Поверх", lambda o: o.floor),
            ("Опис", lambda o: o.description),
            ("Співробітників", lambda o: o.n),
            ("Створено", lambda o: o.created_at.strftime("%d.%m.%Y")),
        ],
        "confirm": "Співробітники відділу залишаться, але без відділу (SET_NULL).",
    },
    "employee": {
        "model": Employee, "form": EmployeeForm, "icon": "👤",
        "title": "Співробітники", "one": "Співробітника",
        "queryset": lambda: Employee.objects.select_related("department"),
        "columns": [
            ("ПІБ", lambda o: o.full_name),
            ("Посада", lambda o: o.position),
            ("Email", lambda o: o.email),
            ("Відділ", lambda o: o.department or "—"),
            ("Прийнято", lambda o: o.hire_date.strftime("%d.%m.%Y")),
        ],
        "confirm": "",
    },
    "service": {
        "model": Service, "form": ServiceForm, "icon": "🛠️",
        "title": "Послуги", "one": "Послугу",
        "queryset": lambda: Service.objects.annotate(n=Count("projects")),
        "columns": [
            ("Назва", lambda o: o.title),
            ("Ціна від, грн", lambda o: _money(o.price_from)),
            ("Статус", lambda o: "активна" if o.is_active else "неактивна"),
            ("Проєктів", lambda o: o.n),
            ("Опис", lambda o: o.description),
        ],
        "confirm": "Послуга зникне з усіх проєктів.",
    },
    "client": {
        "model": Client, "form": ClientForm, "icon": "🤝",
        "title": "Клієнти", "one": "Клієнта",
        "queryset": lambda: Client.objects.annotate(n=Count("projects")),
        "columns": [
            ("Компанія", lambda o: o.company_name),
            ("Контактна особа", lambda o: o.contact_person),
            ("Телефон", lambda o: o.phone),
            ("Email", lambda o: o.email),
            ("Країна", lambda o: o.country),
            ("Проєктів", lambda o: o.n),
        ],
        "confirm": "Усі проєкти цього клієнта теж будуть видалені (CASCADE)!",
    },
    "project": {
        "model": Project, "form": ProjectForm, "icon": "📁",
        "title": "Проєкти", "one": "Проєкт",
        "queryset": lambda: Project.objects.select_related("client").prefetch_related("services"),
        "columns": [
            ("Назва", lambda o: o.name),
            ("Клієнт", lambda o: o.client),
            ("Статус", lambda o: o.get_status_display()),
            ("Початок", lambda o: o.start_date.strftime("%d.%m.%Y")),
            ("Послуги", lambda o: ", ".join(s.title for s in o.services.all()) or "—"),
        ],
        "confirm": "",
    },
}


def _form_values(form_class, obj):
    """Значення полів об'єкта для заповнення модального вікна редагування."""
    values = {}
    for name in form_class.base_fields:
        value = getattr(obj, name)
        if hasattr(value, "all"):  # ManyToMany
            value = [str(s.pk) for s in value.all()]
        elif hasattr(value, "pk"):  # ForeignKey
            value = str(value.pk)
        elif hasattr(value, "isoformat"):  # дата
            value = value.isoformat()
        elif value is None:
            value = ""
        elif not isinstance(value, bool):
            value = str(value)
        values[name] = value
    return values


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Доступ лише для користувачів зі статусом staff, інших - на сторінку входу."""
    login_url = "admin:login"

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect(f"{reverse(self.login_url)}?next={self.request.path}")


class AdminPanelView(StaffRequiredMixin, TemplateView):
    template_name = "main/panel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tabs, edit_data = [], {}
        for key, cfg in ENTITIES.items():
            objects = list(cfg["queryset"]())
            rows = [{"id": o.pk, "label": str(o),
                     "cells": [fn(o) for _, fn in cfg["columns"]]} for o in objects]
            edit_data[key] = {str(o.pk): _form_values(cfg["form"], o) for o in objects}
            tabs.append({
                "key": key, "icon": cfg["icon"], "title": cfg["title"], "one": cfg["one"],
                "headers": [h for h, _ in cfg["columns"]], "rows": rows,
                "confirm": cfg["confirm"],
                "create_form": cfg["form"](auto_id=f"new_{key}_%s"),
                "edit_form": cfg["form"](auto_id=f"edit_{key}_%s"),
            })
        context.update(title="Адмінка", tabs=tabs, edit_data=edit_data)
        return context

    def post(self, request, *args, **kwargs):
        verb, _, key = request.POST.get("action", "").partition("_")
        if key not in ENTITIES or verb not in ("create", "update", "delete"):
            messages.error(request, "Невідома дія.")
            return redirect("panel")

        cfg = ENTITIES[key]
        back = redirect(f"{reverse('panel')}#{key}")

        if verb == "delete":
            obj = get_object_or_404(cfg["model"], pk=request.POST.get("id"))
            obj.delete()
            messages.success(request, f"{cfg['one']} «{obj}» видалено.")
            return back

        instance = get_object_or_404(cfg["model"], pk=request.POST.get("id")) if verb == "update" else None
        form = cfg["form"](request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            done = "додано" if verb == "create" else "оновлено"
            messages.success(request, f"{cfg['one']} «{obj}» {done}.")
        else:
            errors = "; ".join(
                f"{form.fields[f].label if f in form.fields else 'Форма'}: {' '.join(e)}"
                for f, e in form.errors.items())
            messages.error(request, f"{cfg['one']} не збережено. {errors}")
        return back
