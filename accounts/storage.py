"""Користувачі сайту зберігаються в пам'яті процесу, без моделей і БД.

Після перезапуску сервера словник порожній, тож усі мають зареєструватися знову.
Паролі зберігаються не відкритим текстом, а як хеш (стандартні хешери Django).
"""
from django.contrib.auth.hashers import check_password, make_password

# ключ - логін у нижньому регістрі, значення - дані користувача
USERS = {}

SESSION_KEY = "site_username"


def get_user(username):
    return USERS.get((username or "").lower())


def username_taken(username):
    return get_user(username) is not None


def email_taken(email):
    email = email.lower()
    return any(user["email"] == email for user in USERS.values())


def create_user(username, email, password):
    USERS[username.lower()] = {
        "username": username,
        "email": email.lower(),
        "password": make_password(password),
    }
    return USERS[username.lower()]


def authenticate(username, password):
    """Повертає користувача, якщо логін і пароль правильні, інакше None."""
    user = get_user(username)
    if user and check_password(password, user["password"]):
        return user
    return None


def login(request, user):
    request.session.cycle_key()  # новий ідентифікатор сесії після входу
    request.session[SESSION_KEY] = user["username"]


def logout(request):
    request.session.flush()


def current_user(request):
    """Логін поточного користувача або None, якщо він не увійшов."""
    user = get_user(request.session.get(SESSION_KEY))
    return user["username"] if user else None
