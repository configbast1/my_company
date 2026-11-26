from .storage import current_user


def site_user(request):
    """Логін поточного користувача доступний у всіх шаблонах як site_user."""
    return {"site_user": current_user(request)}
