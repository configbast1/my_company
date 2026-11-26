"""Простий CORS для /api/: дозволяє React-клієнту з іншого порту робити запити.

Браузер блокує запити з http://localhost:5173 (Vite) на http://127.0.0.1:8000 (Django),
якщо сервер не відповість заголовком Access-Control-Allow-Origin.
Дозволені адреси задаються в settings.API_ALLOWED_ORIGINS.
"""
from django.conf import settings
from django.http import HttpResponse


class ApiCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        origin = request.headers.get("Origin")
        allowed = origin in getattr(settings, "API_ALLOWED_ORIGINS", [])

        # попередній (preflight) запит браузера перед POST з JSON
        if request.method == "OPTIONS":
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        if allowed:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
            response["Vary"] = "Origin"
        return response
