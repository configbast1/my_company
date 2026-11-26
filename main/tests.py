from django.test import TestCase
from django.urls import reverse

from subsections.data import SUBSECTIONS

from .data import SECTIONS


class PagesTests(TestCase):
    def test_home_lists_five_sections(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(SECTIONS), 5)
        for section in SECTIONS.values():
            self.assertContains(response, section["title"])

    def test_every_section_and_subsection_opens(self):
        for slug in SECTIONS:
            self.assertEqual(self.client.get(f"/{slug}/").status_code, 200)
            self.assertTrue(SUBSECTIONS[slug], f"у розділу {slug} немає підрозділів")
            for sub in SUBSECTIONS[slug]:
                url = reverse("subsections:detail", args=[slug, sub])
                self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_unknown_pages_return_404(self):
        self.assertEqual(self.client.get("/nope/").status_code, 404)
        self.assertEqual(self.client.get("/about/nope/").status_code, 404)
        self.assertEqual(self.client.get("/nope/history/").status_code, 404)


class ComplaintFormTests(TestCase):
    def setUp(self):
        from .models import Service
        self.service = Service.objects.create(title="Тестова послуга", description="—", price_from=100)
        self.data = {
            "full_name": "Іван Петренко",
            "email": "ivan@example.com",
            "phone": "",
            "complaint_type": "service",
            "service": self.service.pk,
            "subject": "Не працює сайт",
            "description": "Після оновлення сайт не відкривається вже два дні.",
            "resolution": "fix",
            "agree": "on",
        }

    def test_page_opens_and_is_in_menu(self):
        response = self.client.get(reverse("complaint"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Скарга на товар або послугу")
        self.assertContains(self.client.get(reverse("home")), reverse("complaint"))

    def test_valid_complaint_is_saved(self):
        from .models import Complaint
        response = self.client.post(reverse("complaint"), self.data, follow=True)
        self.assertEqual(Complaint.objects.count(), 1)
        self.assertContains(response, "прийнято")

    def test_validation_rules(self):
        from .models import Complaint
        cases = [
            ({"agree": ""}, "agree"),
            ({"description": "коротко"}, "description"),
            ({"service": ""}, "service"),
            ({"complaint_type": "product", "service": "", "product_name": ""}, "product_name"),
            ({"wants_callback": "on", "phone": ""}, "phone"),
        ]
        for changes, field in cases:
            data = {**self.data, **changes}
            if not data["agree"]:
                del data["agree"]
            response = self.client.post(reverse("complaint"), data)
            self.assertEqual(response.status_code, 200, field)
            self.assertIn(field, response.context["form"].errors, field)
        self.assertEqual(Complaint.objects.count(), 0)
