from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import FormView, ListView
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q

from config.settings.base import COUNTS_PER_PAGE
from accounts.utils import (
    authorization_filter_on_employee_list,
    authorization_filter_on_signup_list,
)
from accounts.forms import (
    EmployeeForm,
    SignUpForm,
    LoginForm,
    UserForm,
)
from accounts.models import User, Employee


@login_required(login_url=reverse_lazy("login"))
def guide_view(request):
    context = dict()
    if request.user.state == "AP":
        employee = Employee.objects.get(user_id=request.user.id)

        if not employee.list_read_authorization:
            context["AP"] = True
    else:
        context["AP"] = False

    return render(request, "guide.html", context)


@login_required(login_url=reverse_lazy("login"))
def logout_view(request):
    logout(request)
    return redirect("login")


class SignUpView(FormView):
    template_name = "user/signup.html"
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
    template_name = "user/login.html"
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
        if self.request.user.state == "AP":
            employee = Employee.objects.get(user_id=self.request.user.id)

            if employee.signup_approval_authorization:
                return reverse_lazy("signup_list")
            else:
                return reverse_lazy("employee_list")
        else:
            return reverse_lazy("guide")


@method_decorator(login_required(login_url=reverse_lazy("login")), name="get")
@method_decorator(authorization_filter_on_signup_list, name="get")
class SignupListView(ListView):
    queryset = User.objects.exclude(Q(state="AP") | Q(is_superuser=1))
    template_name = "list.html"
    ordering = ["-id"]
    paginate_by = COUNTS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = Employee.objects.get(user_id=self.request.user.id)

        if employee.list_read_authorization:
            context["read_authorization"] = True

        context["approval_authorization"] = True
        context["signup_list"] = True

        return context


@method_decorator(login_required(login_url=reverse_lazy("login")), name="get")
@method_decorator(authorization_filter_on_employee_list, name="get")
class EmployeeListView(ListView):
    queryset = Employee.objects.select_related("user")
    template_name = "list.html"
    ordering = ["-id"]
    paginate_by = COUNTS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = Employee.objects.get(user_id=self.request.user.id)

        if employee.signup_approval_authorization:
            context["approval_authorization"] = True

        context["read_authorization"] = True
        context["signup_list"] = False

        return context


@login_required(login_url=reverse_lazy("login"))
def signup_user_detail_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        if "refusal-btn" in request.POST:  # 거절 버튼 클릭 시
            user_form = UserForm(request.POST, instance=user)
            if user_form.is_valid():
                reason_for_refusal = user_form.cleaned_data.get("reason_for_refusal")
                rejected_at = timezone.now()
                user.reason_for_refusal = reason_for_refusal
                user.rejected_at = rejected_at
                user.save()

        else:  # 승인 버튼 클릭 시
            user_form = UserForm(request.POST, instance=user)
            if user_form.is_valid():
                state = user_form.cleaned_data.get("state")
                user.state = state
                user.save()

            employee_form = EmployeeForm(request.POST)
            if employee_form.is_valid():
                cleaned_data = employee_form.cleaned_data
                grade = employee_form.data.get("grade")
                authorizations = {
                    "authorization_grade": grade,
                    "signup_approval_authorization": cleaned_data.get(
                        "signup_approval_authorization"
                    ),
                    "list_read_authorization": cleaned_data.get(
                        "list_read_authorization"
                    ),
                    "update_authorization": cleaned_data.get("update_authorization"),
                    "resign_authorization": cleaned_data.get("resign_authorization"),
                }

            employee = Employee.objects.create(user_id=user.id, **authorizations)
            employee.save()

            return redirect(request, "signup_detail", user_id=user_id)
    else:
        user_form = UserForm(instance=user)
        employee_form = EmployeeForm()

    context = {
        "user_form": user_form,
        "employee_form": employee_form,
        "signup_list": True,
    }
    return render(request, "detail.html", context)
