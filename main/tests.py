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
