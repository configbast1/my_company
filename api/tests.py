import json

from django.test import TestCase
from django.urls import reverse

from main.models import Complaint, Service

ORIGIN = "http://localhost:5173"


class ApiTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(title="API-послуга", description="—", price_from=500)

    def test_get_endpoints_return_json(self):
        for name in ("company", "services", "employees", "projects"):
            response = self.client.get(reverse(f"api:{name}"))
            self.assertEqual(response.status_code, 200, name)
            self.assertEqual(response["Content-Type"], "application/json", name)
        services = self.client.get(reverse("api:services")).json()
        self.assertIn("API-послуга", [s["title"] for s in services])

    def test_cors_only_for_allowed_origin(self):
        ok = self.client.get(reverse("api:services"), HTTP_ORIGIN=ORIGIN)
        self.assertEqual(ok["Access-Control-Allow-Origin"], ORIGIN)
        bad = self.client.get(reverse("api:services"), HTTP_ORIGIN="http://evil.example")
        self.assertNotIn("Access-Control-Allow-Origin", bad)

    def test_preflight(self):
        response = self.client.options(reverse("api:complaints"), HTTP_ORIGIN=ORIGIN)
        self.assertEqual(response.status_code, 204)
        self.assertIn("POST", response["Access-Control-Allow-Methods"])

    def post(self, **changes):
        data = {
            "full_name": "Іван", "email": "ivan@example.com", "complaint_type": "service",
            "service": self.service.id, "subject": "Тема",
            "description": "Достатньо довгий опис проблеми для перевірки.",
            "resolution": "fix", "agree": True, "wants_callback": False, **changes,
        }
        return self.client.post(reverse("api:complaints"), json.dumps(data),
                                content_type="application/json", HTTP_ORIGIN=ORIGIN)

    def test_create_complaint(self):
        response = self.post()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Complaint.objects.count(), 1)
        self.assertEqual(response["Access-Control-Allow-Origin"], ORIGIN)

    def test_complaint_validation_errors(self):
        response = self.post(agree=False, description="коротко")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()["errors"]), {"agree", "description"})
        self.assertEqual(Complaint.objects.count(), 0)
