"""JSON API сайту «Моя компанія» для окремого React-клієнта.

GET  /api/company/      - інформація про компанію та розділи
GET  /api/services/     - послуги
GET  /api/employees/    - співробітники (з відділом)
GET  /api/projects/     - проєкти (з клієнтом і послугами)
POST /api/complaints/   - створити скаргу (JSON), перевірка тією ж ComplaintForm
"""
import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from main.data import COMPANY, SECTIONS
from main.forms import ComplaintForm
from main.models import Employee, Project, Service


def json_response(data, status=200):
    # ensure_ascii=False - щоб кирилиця йшла як є, а не Те...
    return JsonResponse(data, status=status, safe=False, json_dumps_params={"ensure_ascii": False})


class CompanyApi(View):
    def get(self, request):
        sections = [
            {"slug": slug, "title": s["title"], "icon": s["icon"], "description": s["description"]}
            for slug, s in SECTIONS.items()
        ]
        return json_response({**COMPANY, "sections": sections})


class ServicesApi(View):
    def get(self, request):
        services = [
            {
                "id": s.id,
                "title": s.title,
                "description": s.description,
                "price_from": float(s.price_from),
                "is_active": s.is_active,
            }
            for s in Service.objects.all()
        ]
        return json_response(services)


class EmployeesApi(View):
    def get(self, request):
        employees = [
            {
                "id": e.id,
                "full_name": e.full_name,
                "position": e.position,
                "email": e.email,
                "department": e.department.name if e.department else None,
                "hire_date": e.hire_date.isoformat(),
            }
            for e in Employee.objects.select_related("department")
        ]
        return json_response(employees)


class ProjectsApi(View):
    def get(self, request):
        projects = [
            {
                "id": p.id,
                "name": p.name,
                "client": p.client.company_name,
                "status": p.status,
                "status_display": p.get_status_display(),
                "start_date": p.start_date.isoformat(),
                "services": [s.title for s in p.services.all()],
            }
            for p in Project.objects.select_related("client").prefetch_related("services")
        ]
        return json_response(projects)


# Для локального навчального прикладу CSRF вимкнено лише для цього JSON-ендпоінту:
# React-клієнт працює на іншому порту і не має CSRF-cookie Django.
@method_decorator(csrf_exempt, name="dispatch")
class ComplaintsApi(View):
    def post(self, request):
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return json_response({"errors": {"__all__": ["Некоректний JSON."]}}, status=400)

        # Чекбокси з JSON приходять як true/false, ComplaintForm очікує значення з форми
        for key in ("agree", "wants_callback"):
            if not data.get(key):
                data.pop(key, None)

        form = ComplaintForm(data)
        if not form.is_valid():
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return json_response({"errors": errors}, status=400)

        complaint = form.save()
        return json_response(
            {"id": complaint.id, "message": f"Скаргу №{complaint.id} прийнято. Відповідь надійде на {complaint.email}."},
            status=201,
        )
