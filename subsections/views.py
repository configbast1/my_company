from django.http import Http404
from django.views.generic import TemplateView

from main.data import SECTIONS

from .data import SUBSECTIONS


class SubsectionView(TemplateView):
    """Сторінка підрозділу, наприклад /services/web/."""
    template_name = "subsections/subsection.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_slug = kwargs["section"]
        sub_slug = kwargs["subsection"]

        siblings = SUBSECTIONS.get(section_slug, {})
        if section_slug not in SECTIONS or sub_slug not in siblings:
            raise Http404("Підрозділ не знайдено")

        context.update({
            "section_slug": section_slug,
            "section": SECTIONS[section_slug],
            "sub_slug": sub_slug,
            "subsection": siblings[sub_slug],
            "siblings": siblings,  # для бокового меню
        })
        return context
