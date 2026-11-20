from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Client, Department, Employee, Project, Service


class AdminPanelTests(TestCase):
    def setUp(self):
        self.url = reverse("panel")
        self.admin = User.objects.create_superuser("boss", "boss@example.com", "pass12345")

    def login(self):
        self.client.force_login(self.admin)

    def test_anonymous_and_non_staff_redirected_to_login(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("admin:login"), r["Location"])

        self.client.force_login(User.objects.create_user("worker", password="pass12345"))
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_page_shows_all_five_tables_with_seed_data(self):
        self.login()
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        for text in ["Відділи", "Співробітники", "Послуги", "Клієнти", "Проєкти",
                     "Розробка", "Шевченко Марина Іванівна", "Веб-розробка", "AgroLink", "CRM для агрохолдингу"]:
            self.assertContains(r, text)

    def test_department_crud_and_set_null(self):
        self.login()
        r = self.client.post(self.url, {"action": "create_department", "name": "DevOps",
                                        "floor": 4, "description": ""}, follow=True)
        self.assertContains(r, "додано")
        dep = Department.objects.get(name="DevOps")

        self.client.post(self.url, {"action": "update_department", "id": dep.id,
                                    "name": "DevOps і хмара", "floor": 5, "description": "CI/CD"})
        dep.refresh_from_db()
        self.assertEqual((dep.name, dep.floor), ("DevOps і хмара", 5))

        emp = Employee.objects.create(full_name="Тест", position="Інженер", email="t@t.ua",
                                      hire_date=date(2026, 1, 1), department=dep)
        self.client.post(self.url, {"action": "delete_department", "id": dep.id})
        self.assertFalse(Department.objects.filter(pk=dep.pk).exists())
        emp.refresh_from_db()
        self.assertIsNone(emp.department)  # SET_NULL: співробітник лишився

    def test_employee_create_update(self):
        self.login()
        dep = Department.objects.first()
        self.client.post(self.url, {"action": "create_employee", "full_name": "Іван Новий",
                                    "position": "Стажер", "email": "new@technosvit.ua",
                                    "department": dep.id, "hire_date": "2026-11-01"})
        emp = Employee.objects.get(email="new@technosvit.ua")
        self.client.post(self.url, {"action": "update_employee", "id": emp.id, "full_name": "Іван Новий",
                                    "position": "Junior", "email": "new@technosvit.ua",
                                    "department": "", "hire_date": "2026-11-01"})
        emp.refresh_from_db()
        self.assertEqual(emp.position, "Junior")
        self.assertIsNone(emp.department)

    def test_service_checkbox(self):
        self.login()
        self.client.post(self.url, {"action": "create_service", "title": "Аудит",
                                    "description": "Аудит коду", "price_from": "8000", "is_active": "on"})
        s = Service.objects.get(title="Аудит")
        self.assertTrue(s.is_active)
        self.client.post(self.url, {"action": "update_service", "id": s.id, "title": "Аудит",
                                    "description": "Аудит коду", "price_from": "9000"})
        s.refresh_from_db()
        self.assertFalse(s.is_active)

    def test_project_with_services_and_client_cascade(self):
        self.login()
        client = Client.objects.create(company_name="ТестКлієнт", contact_person="Хтось",
                                       phone="1", email="c@c.ua")
        services = list(Service.objects.values_list("id", flat=True)[:2])
        self.client.post(self.url, {"action": "create_project", "name": "Новий проєкт",
                                    "client": client.id, "status": "planned",
                                    "start_date": "2026-12-01", "services": services})
        project = Project.objects.get(name="Новий проєкт")
        self.assertEqual(sorted(project.services.values_list("id", flat=True)), sorted(services))

        self.client.post(self.url, {"action": "delete_client", "id": client.id})
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())  # CASCADE

    def test_invalid_data_shows_error_not_500(self):
        self.login()
        existing = Employee.objects.first()
        before = Employee.objects.count()
        r = self.client.post(self.url, {"action": "create_employee", "full_name": "Дубль",
                                        "position": "X", "email": existing.email,
                                        "hire_date": "не дата"}, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "не збережено")
        self.assertEqual(Employee.objects.count(), before)

    def test_unknown_action_and_missing_object(self):
        self.login()
        r = self.client.post(self.url, {"action": "drop_tables"}, follow=True)
        self.assertContains(r, "Невідома дія")
        r = self.client.post(self.url, {"action": "delete_project", "id": 999999})
        self.assertEqual(r.status_code, 404)
