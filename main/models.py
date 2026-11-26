from django.db import models


class Department(models.Model):
    """Відділ компанії (розробка, дизайн, тестування...)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва відділу")
    description = models.TextField(blank=True, verbose_name="Опис")
    floor = models.PositiveSmallIntegerField(default=1, verbose_name="Поверх")
    created_at = models.DateField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Відділ"
        verbose_name_plural = "Відділи"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Співробітник компанії"""
    full_name = models.CharField(max_length=150, verbose_name="ПІБ")
    position = models.CharField(max_length=100, verbose_name="Посада")
    email = models.EmailField(unique=True, verbose_name="Email")
    hire_date = models.DateField(verbose_name="Дата прийому на роботу")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,  # якщо відділ видалено - співробітник лишається
        null=True,
        blank=True,
        related_name="employees",
        verbose_name="Відділ",
    )

    class Meta:
        verbose_name = "Співробітник"
        verbose_name_plural = "Співробітники"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Service(models.Model):
    """Послуга, яку надає компанія"""
    title = models.CharField(max_length=150, verbose_name="Назва послуги")
    description = models.TextField(verbose_name="Опис")
    price_from = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна від (грн)")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Client(models.Model):
    """Клієнт компанії"""
    company_name = models.CharField(max_length=150, verbose_name="Назва компанії-клієнта")
    contact_person = models.CharField(max_length=150, verbose_name="Контактна особа")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    country = models.CharField(max_length=100, default="Україна", verbose_name="Країна")

    class Meta:
        verbose_name = "Клієнт"
        verbose_name_plural = "Клієнти"
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name


class Project(models.Model):
    """Проєкт, який компанія виконує для клієнта"""
    STATUS_CHOICES = [
        ("planned", "Запланований"),
        ("in_progress", "У роботі"),
        ("done", "Завершений"),
    ]

    name = models.CharField(max_length=200, verbose_name="Назва проєкту")
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,  # видалили клієнта - видаляються і його проєкти
        related_name="projects",
        verbose_name="Клієнт",
    )
    services = models.ManyToManyField(Service, blank=True, related_name="projects", verbose_name="Послуги")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned", verbose_name="Статус")
    start_date = models.DateField(verbose_name="Дата початку")

    class Meta:
        verbose_name = "Проєкт"
        verbose_name_plural = "Проєкти"
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class Complaint(models.Model):
    """Скарга клієнта на товар або послугу"""
    TYPE_CHOICES = [
        ("product", "Товар"),
        ("service", "Послуга"),
    ]
    RESOLUTION_CHOICES = [
        ("refund", "Повернення коштів"),
        ("replace", "Заміна товару / повторне надання послуги"),
        ("fix", "Усунення недоліків"),
        ("other", "Інше"),
    ]
    STATUS_CHOICES = [
        ("new", "Нова"),
        ("in_review", "На розгляді"),
        ("resolved", "Вирішена"),
    ]

    full_name = models.CharField(max_length=150, verbose_name="ПІБ")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    complaint_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="service",
                                      verbose_name="Скарга на")
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complaints",
        verbose_name="Послуга",
    )
    product_name = models.CharField(max_length=150, blank=True, verbose_name="Назва товару")
    order_number = models.CharField(max_length=30, blank=True, verbose_name="Номер замовлення")
    purchase_date = models.DateField(null=True, blank=True, verbose_name="Дата покупки")
    subject = models.CharField(max_length=150, verbose_name="Тема")
    description = models.TextField(verbose_name="Опис проблеми")
    resolution = models.CharField(max_length=10, choices=RESOLUTION_CHOICES, default="fix",
                                  verbose_name="Бажане вирішення")
    wants_callback = models.BooleanField(default=False, verbose_name="Передзвоніть мені")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="new", verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подання")

    class Meta:
        verbose_name = "Скарга"
        verbose_name_plural = "Скарги"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} {self.subject}"
