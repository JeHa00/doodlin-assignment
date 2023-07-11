from accounts.models import User, Employee
from django.shortcuts import redirect


def grade_filter_on_signup_list(function):
    def decorator_func(request):
        if request.user.is_authenticated:
            if request.user.state == "AP":
                user = User.objects.get(email=request.user.email)
                employee = Employee.objects.get(user=user)
                if employee.authorization_grade == "MS":
                    return function(request)
                elif (
                    employee.authorization_grade == "MA"
                    and employee.signup_approval_authorization
                ):
                    return function(request)
                else:
                    return redirect("employee_list")
            else:
                return redirect("guide")

    return decorator_func
