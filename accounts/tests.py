from django.test import TestCase
from django.urls import reverse

from . import storage

PASSWORD = "Secret-pass-123"


class AuthTests(TestCase):
    def setUp(self):
        storage.USERS.clear()

    def register(self, username="ivan", email="ivan@example.com", password2=PASSWORD):
        return self.client.post(reverse("accounts:register"), {
            "username": username, "email": email,
            "password1": PASSWORD, "password2": password2,
        })

    def test_anonymous_is_redirected_from_home_to_login(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next=%2F")

    def test_register_logs_in_and_shows_greeting(self):
        response = self.register()
        self.assertRedirects(response, reverse("home"))
        home = self.client.get(reverse("home"))
        self.assertContains(home, "Добрий день, <b>ivan</b>!")
        self.assertContains(home, "Вийти з облікового запису")
        # пароль збережено як хеш, а не відкритим текстом
        self.assertNotEqual(storage.USERS["ivan"]["password"], PASSWORD)

    def test_register_validation(self):
        self.register()
        self.client.post(reverse("accounts:logout"))
        cases = [
            (self.register(password2="other-pass-999"), "password2"),
            (self.register(username="IVAN", email="new@example.com"), "username"),
            (self.register(username="petro", email="IVAN@example.com"), "email"),
            (self.register(username="ab", email="ab@example.com"), "username"),
        ]
        for response, field in cases:
            self.assertEqual(response.status_code, 200, field)
            self.assertIn(field, response.context["form"].errors, field)
        self.assertEqual(len(storage.USERS), 1)

    def test_login_and_logout(self):
        storage.create_user("olena", "olena@example.com", PASSWORD)

        bad = self.client.post(reverse("accounts:login"), {"username": "olena", "password": "wrong"})
        self.assertContains(bad, "Невірний логін або пароль.")

        ok = self.client.post(reverse("accounts:login") + "?next=/about/",
                              {"username": "olena", "password": PASSWORD, "next": "/about/"})
        self.assertRedirects(ok, "/about/")
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)  # тільки POST
        self.client.post(reverse("accounts:logout"))
        self.assertEqual(self.client.get(reverse("home")).status_code, 302)

    def test_login_ignores_external_next(self):
        storage.create_user("olena", "olena@example.com", PASSWORD)
        response = self.client.post(reverse("accounts:login"),
                                    {"username": "olena", "password": PASSWORD, "next": "https://evil.example/"})
        self.assertRedirects(response, reverse("home"))

    def test_logged_in_user_skips_login_page(self):
        self.register()
        self.assertRedirects(self.client.get(reverse("accounts:login")), reverse("home"))
