from django.http import Http404
from django.views.generic import TemplateView

from subsections.data import SUBSECTIONS

from .data import SECTIONS


class HomeView(TemplateView):
    """Головна сторінка: перелік усіх 5 розділів."""
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sections"] = SECTIONS
        return context


class SectionView(TemplateView):
    """Сторінка розділу: опис + картки його підрозділів."""
    template_name = "main/section.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs["section"]
        if slug not in SECTIONS:
            raise Http404("Розділ не знайдено")
        context["section_slug"] = slug
        context["section"] = SECTIONS[slug]
        context["subsections"] = SUBSECTIONS.get(slug, {})
        return context
