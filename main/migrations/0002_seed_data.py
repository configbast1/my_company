"""Початкові дані для адмінки: відділи, співробітники, послуги, клієнти, проєкти."""
from datetime import date
from decimal import Decimal

from django.db import migrations

DEPARTMENTS = [
    ("Розробка", 3, "Backend і frontend розробка веб-застосунків."),
    ("Мобільна розробка", 3, "iOS та Android застосунки."),
    ("Дизайн", 2, "UI/UX дизайн, прототипи, брендинг."),
    ("Тестування", 2, "Ручне та автоматизоване тестування."),
    ("Продажі", 1, "Робота з клієнтами та укладання договорів."),
]

EMPLOYEES = [
    ("Коваленко Олександр Петрович", "Тімлід", "o.kovalenko@technosvit.ua", date(2014, 3, 1), "Розробка"),
    ("Шевченко Марина Іванівна", "Python-розробник", "m.shevchenko@technosvit.ua", date(2019, 9, 16), "Розробка"),
    ("Бондар Дмитро Сергійович", "Frontend-розробник", "d.bondar@technosvit.ua", date(2021, 2, 1), "Розробка"),
    ("Мельник Ірина Олегівна", "Flutter-розробник", "i.melnyk@technosvit.ua", date(2020, 6, 8), "Мобільна розробка"),
    ("Ткаченко Андрій Васильович", "UI/UX дизайнер", "a.tkachenko@technosvit.ua", date(2018, 11, 12), "Дизайн"),
    ("Литвин Оксана Миколаївна", "QA-інженер", "o.lytvyn@technosvit.ua", date(2022, 4, 4), "Тестування"),
    ("Романенко Софія Андріївна", "Менеджер з продажу", "s.romanenko@technosvit.ua", date(2023, 1, 9), "Продажі"),
]

SERVICES = [
    ("Веб-розробка", "Сайти та веб-застосунки на Django і React.", "25000", True),
    ("Мобільні застосунки", "Кросплатформені застосунки для iOS та Android.", "60000", True),
    ("Хмарні рішення", "Розгортання та супровід у хмарі.", "15000", True),
    ("UI/UX дизайн", "Дизайн інтерфейсів і прототипування.", "12000", True),
    ("Технічна підтримка", "Супровід проєктів після запуску.", "5000", False),
]

CLIENTS = [
    ("Нова Пекарня", "Іван Гнатюк", "+380671112233", "office@novapekarnya.ua", "Україна"),
    ("AgroLink", "Тарас Кравець", "+380502223344", "hello@agrolink.ua", "Україна"),
    ("Baltic Logistics", "Jonas Petraitis", "+37061234567", "info@balticlog.lt", "Литва"),
    ("Medica Plus", "Anna Nowak", "+48501234567", "it@medicaplus.pl", "Польща"),
]

PROJECTS = [
    ("Інтернет-магазин випічки", "Нова Пекарня", "done", date(2025, 2, 10), ["Веб-розробка", "UI/UX дизайн"]),
    ("Мобільний застосунок доставки", "Нова Пекарня", "in_progress", date(2026, 6, 1), ["Мобільні застосунки"]),
    ("CRM для агрохолдингу", "AgroLink", "in_progress", date(2026, 3, 15), ["Веб-розробка", "Хмарні рішення"]),
    ("Трекінг вантажів", "Baltic Logistics", "planned", date(2026, 12, 1), ["Веб-розробка", "Мобільні застосунки"]),
    ("Портал запису до лікаря", "Medica Plus", "done", date(2024, 9, 2), ["Веб-розробка", "Технічна підтримка"]),
]


def seed(apps, schema_editor):
    Department = apps.get_model("main", "Department")
    Employee = apps.get_model("main", "Employee")
    Service = apps.get_model("main", "Service")
    Client = apps.get_model("main", "Client")
    Project = apps.get_model("main", "Project")

    deps = {name: Department.objects.create(name=name, floor=floor, description=desc)
            for name, floor, desc in DEPARTMENTS}
    for full_name, position, email, hired, dep in EMPLOYEES:
        Employee.objects.create(full_name=full_name, position=position, email=email,
                                hire_date=hired, department=deps[dep])
    services = {title: Service.objects.create(title=title, description=desc,
                                              price_from=Decimal(price), is_active=active)
                for title, desc, price, active in SERVICES}
    clients = {name: Client.objects.create(company_name=name, contact_person=person,
                                           phone=phone, email=email, country=country)
               for name, person, phone, email, country in CLIENTS}
    for name, client, status, start, service_titles in PROJECTS:
        project = Project.objects.create(name=name, client=clients[client],
                                         status=status, start_date=start)
        project.services.set([services[t] for t in service_titles])


def unseed(apps, schema_editor):
    apps.get_model("main", "Client").objects.filter(company_name__in=[c[0] for c in CLIENTS]).delete()
    apps.get_model("main", "Service").objects.filter(title__in=[s[0] for s in SERVICES]).delete()
    apps.get_model("main", "Employee").objects.filter(email__in=[e[2] for e in EMPLOYEES]).delete()
    apps.get_model("main", "Department").objects.filter(name__in=[d[0] for d in DEPARTMENTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
