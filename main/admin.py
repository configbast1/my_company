from django.contrib import admin

from .models import Client, Complaint, Department, Employee, Project, Service


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 0


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    fields = ("name", "status", "start_date")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "floor", "created_at")
    search_fields = ("name",)
    inlines = [EmployeeInline]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "email", "department", "hire_date")
    list_filter = ("department",)
    search_fields = ("full_name", "email")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "price_from", "is_active")
    list_filter = ("is_active",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_person", "phone", "email", "country")
    search_fields = ("company_name", "contact_person")
    inlines = [ProjectInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "status", "start_date")
    list_filter = ("status", "client")
    filter_horizontal = ("services",)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "complaint_type", "full_name", "email", "status", "created_at")
    list_filter = ("status", "complaint_type", "resolution")
    list_editable = ("status",)
    search_fields = ("subject", "full_name", "email", "order_number")
