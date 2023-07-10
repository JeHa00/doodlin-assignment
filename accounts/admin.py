from django.contrib import admin

from accounts.models import User, Employee, Resignation


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "phone", "state"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        "authorization_grade",
        "signup_approval_authorization",
        "is_resigned",
    ]


@admin.register(Resignation)
class ResignationAdmin(admin.ModelAdmin):
    list_display = ["resigned_at"]
