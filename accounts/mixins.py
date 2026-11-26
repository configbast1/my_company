from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import reverse

from .storage import current_user


class SiteLoginRequiredMixin:
    """Пускає на сторінку тільки авторизованих, решту відправляє на вхід."""

    def dispatch(self, request, *args, **kwargs):
        if not current_user(request):
            query = urlencode({"next": request.get_full_path()})
            return redirect(f"{reverse('accounts:login')}?{query}")
        return super().dispatch(request, *args, **kwargs)
