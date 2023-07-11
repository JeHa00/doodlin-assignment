from accounts.models import User, Employee
from django.shortcuts import redirect


def authorization_filter_on_signup_list(function):
    def decorator_func(request):
        if request.user.state == "AP":
            employee = Employee.objects.get(user_id=request.user.id)
            if employee.signup_approval_authorization:
                return function(request)
            else:
                return redirect("employee_list")
        else:
            return redirect("guide")

    return decorator_func


def authorization_filter_on_employee_list(function):
    def decorator_func(request):
        if request.user.state == "AP":
            employee = Employee.objects.get(user_id=request.user.id)
            if employee.list_read_authorization:
                return function(request)
        else:
            return redirect("guide")

    return decorator_func
