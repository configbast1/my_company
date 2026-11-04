from subsections.data import SUBSECTIONS

from .data import COMPANY, SECTIONS


def menu(request):
    """Меню з розділами та підрозділами доступне в усіх шаблонах."""
    items = [
        {"slug": slug, "title": s["title"], "icon": s["icon"],
         "children": SUBSECTIONS.get(slug, {})}
        for slug, s in SECTIONS.items()
    ]
    return {"menu": items, "company": COMPANY}
