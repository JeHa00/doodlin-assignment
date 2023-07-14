from django.contrib import admin

from accounts.models import User, Employee, Resignation


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "phone", "state"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        "get_user",
        "authorization_grade",
        "signup_approval_authorization",
        "is_resigned",
    ]

    @admin.display(description="임직원")
    def get_user(self, obj):
        return obj.user.name


@admin.register(Resignation)
class ResignationAdmin(admin.ModelAdmin):
    list_display = ["get_resigned_user", "resigned_at", "reason_for_resignation"]

    @admin.display(description="임직원")
    def get_resigned_user(self, obj):
        return obj.resigned_user.user.name
