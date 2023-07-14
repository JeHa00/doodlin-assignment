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
    def get_user(self, obj: Employee) -> str:
        """Employee instance이 obj의 user name을 반환한다.

        Args:
            obj (Employee): Employee 객체를 의미한다.

        Returns:
            str: obj의 user name 속성을 반환한다.
        """
        return obj.user.name


@admin.register(Resignation)
class ResignationAdmin(admin.ModelAdmin):
    list_display = ["get_resigned_user", "resigned_at", "reason_for_resignation"]

    @admin.display(description="임직원")
    def get_resigned_user(self, obj: Resignation) -> str:
        """Resignation instance인 obj의 회원가입 승인 신청 전 모델의 이름을 반환한다.

        Args:
            obj (Resignation): Resignation의 인스턴스

        Returns:
            str: 회원가입 승인 신청 전 모델의 이름을 반환한다.
        """
        return obj.resigned_user.user.name
