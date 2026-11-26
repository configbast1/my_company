# Django: Моя компанія (ТехноСвіт)

Сайт компанії з 5 розділами, до кожного з яких додано підрозділи.

## Що зроблено

- **5 розділів** (додаток `main`): Про компанію, Послуги, Проєкти, Команда, Контакти.
- **Підрозділи** винесені в **окремий додаток `subsections`** - по 3 підрозділи в кожному розділі (15 сторінок).
- Усі контролери - **на класах** (class-based views, `TemplateView`):
  - `main.views.HomeView` - головна сторінка;
  - `main.views.SectionView` - сторінка розділу зі списком його підрозділів;
  - `subsections.views.SubsectionView` - сторінка підрозділу з боковим меню.
- Випадне меню з підрозділами в шапці (context processor `main.context_processors.menu`).
- Хлібні крихти: Головна / Розділ / Підрозділ.
- Неіснуючий розділ або підрозділ повертає 404.

| Розділ | Підрозділи |
|---|---|
| Про компанію `/about/` | Історія, Місія та цінності, Нагороди |
| Послуги `/services/` | Веб-розробка, Мобільні застосунки, Хмарні рішення |
| Проєкти `/projects/` | Портфоліо, Кейси, Відгуки клієнтів |
| Команда `/team/` | Керівництво, Розробники, Вакансії |
| Контакти `/contacts/` | Офіси, Зворотний зв'язок, Як дістатися |

## Власна адмінка `/panel/`

Кастомна адмінка для всіх 5 моделей (`Department`, `Employee`, `Service`, `Client`, `Project`) на одній сторінці:

- вкладки для кожної таблиці + картки зі статистикою (кількість записів);
- форма додавання, таблиця з пошуком, редагування в модальному вікні (Esc / клік по фону закриває), видалення з підтвердженням;
- у підтвердженні видалення - попередження про зв'язки: видалення клієнта видаляє його проєкти (`CASCADE`), співробітники видаленого відділу лишаються без відділу (`SET_NULL`);
- зв'язки: `ForeignKey` - випадний список, `ManyToMany` (послуги проєкту) - чекбокси;
- валідація через `ModelForm` (`main/forms.py`): помилки (наприклад, email, що вже існує) показуються повідомленням, а не 500;
- доступ лише для користувачів зі статусом staff (`StaffRequiredMixin`), інших перенаправляє на вхід;
- контролер на класі: `main.panel.AdminPanelView` (один view обробляє дії `create_*`, `update_*`, `delete_*`);
- початкові дані - міграція `main/migrations/0002_seed_data.py`;
- моделі також зареєстровані у стандартній адмінці Django `/admin/` (`main/admin.py`);
- тести: `main/tests_panel.py`.

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Відкрити http://127.0.0.1:8000/panel/

## Структура

```
config/                     # налаштування та головні urls.py
main/                       # головна + 5 розділів + власна адмінка
├── data.py                 # дані розділів
├── views.py                # HomeView, SectionView
├── panel.py                # AdminPanelView - власна адмінка
├── forms.py                # ModelForm для 5 моделей
├── admin.py                # реєстрація моделей у Django admin
├── urls.py
├── context_processors.py   # меню
├── templates/main/         # base.html, home.html, section.html
├── static/main/style.css
└── tests.py
subsections/                # окремий додаток для підрозділів
├── data.py                 # дані підрозділів
├── views.py                # SubsectionView
├── urls.py                 # /<розділ>/<підрозділ>/
└── templates/subsections/subsection.html
manage.py
```

## Запуск

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Відкрити http://127.0.0.1:8000/

Тести: `python manage.py test`

## Скріншоти

### Головна сторінка
![Головна](screenshots/01_home.png)

### Випадне меню з підрозділами
![Меню](screenshots/02_menu_subsections.png)

### Розділ «Послуги» зі списком підрозділів
![Розділ Послуги](screenshots/03_section_services.png)

### Підрозділ «Веб-розробка»
![Веб-розробка](screenshots/04_subsection_web.png)

### Підрозділ «Історія»
![Історія](screenshots/05_subsection_history.png)

### Розділ «Команда»
![Команда](screenshots/06_section_team.png)

## Скріншоти: власна адмінка

### Вкладка «Відділи» (після додавання запису)
![Адмінка: відділи](screenshots/07_admin_panel.png)

### Вкладка «Проєкти» (ForeignKey + ManyToMany)
![Адмінка: проєкти](screenshots/08_admin_panel_projects.png)

### Редагування в модальному вікні
![Редагування](screenshots/09_admin_panel_edit_modal.png)

### Вкладка «Клієнти»
![Адмінка: клієнти](screenshots/10_admin_panel_clients.png)

### Стандартна адмінка Django: проєкти
![Django admin](screenshots/11_django_admin_projects.png)

### Таблиці БД
![Таблиці БД](screenshots/12_db_tables.png)

## React-клієнт (окремий проєкт у папці `client/`)

React + Vite. Отримує дані з Django через JSON API (`/api/...`) і надсилає скаргу POST-запитом.
Інструкція запуску: [client/README.md](client/README.md).

### Послуги (`GET /api/services/`)
![React: послуги](screenshots/18_react_services.jpg)

### Команда (`GET /api/employees/`)
![React: команда](screenshots/19_react_team.jpg)

### Проєкти (`GET /api/projects/`)
![React: проєкти](screenshots/20_react_projects.jpg)

### Скарга (`POST /api/complaints/`)
![React: скарга](screenshots/21_react_complaint_post.jpg)
