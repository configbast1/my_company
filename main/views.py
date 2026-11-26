from django.contrib import messages
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from subsections.data import SUBSECTIONS

from .data import SECTIONS
from .forms import ComplaintForm


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


class ComplaintView(CreateView):
    """Форма «Скарга на товар або послугу»: зберігає скаргу в БД."""
    form_class = ComplaintForm
    template_name = "main/complaint.html"
    success_url = reverse_lazy("complaint")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Дякуємо! Скаргу №{self.object.pk} прийнято. Ми відповімо на {self.object.email} протягом 2 робочих днів.",
        )
        return response
