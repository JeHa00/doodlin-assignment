from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import FormView, ListView
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Q

from accounts.utils import grade_filter_on_signup_list
from accounts.forms import SignUpForm, LoginForm
from accounts.models import User, Employee


@login_required(login_url=reverse_lazy("login"))
def guide_view(request):
    return render(request, "accounts/signup_guide.html")


@login_required(login_url=reverse_lazy("login"))
def logout_view(request):
    logout(request)
    return redirect("login")


class SignUpView(FormView):
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        email = form.data.get("email")
        password = form.data.get("password")
        username = form.data.get("username")
        phone = form.data.get("phone")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
        )
        user.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def get_success_url(self) -> str:
        return self.redirect_url()

    def form_valid(self, form):
        email = form.data.get("email")
        user = User.objects.get(email=email)
        user.update_last_login()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def redirect_url(self):
        if  self.request.user.state == "AP":
            employee = Employee.objects.get(user=self.request.user)
            if employee.authorization_grade == "MS":
                return reverse_lazy("signup_list")
            elif (
                employee.authorization_grade == "MA"
                and employee.signup_approval_authorization
            ):
                return reverse_lazy("signup_list")
            else:
                return reverse_lazy("employee_list")
        else:
            return reverse_lazy("guide")


@method_decorator(login_required(login_url=reverse_lazy("login")), name="dispatch")
@method_decorator(grade_filter_on_signup_list, name="dispatch")
class SignupListView(ListView):
    queryset = User.objects.exclude(Q(state="AP") | Q(is_superuser=1))
    template_name = "accounts/signup_list.html"
    context_object_name = "signup_list"
    ordering = ["-id"]
    paginate_by = 7


@method_decorator(login_required(login_url=reverse_lazy("login")), name="get")
class EmployeeListView(ListView):
    template_name = "employee/list.html"
    context_object_name = "employee_list"
    ordering = ["-id"]
    paginate_by = 7