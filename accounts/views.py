from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
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
    ResignationForm,
    EmployeeForm,
    SignUpForm,
    LoginForm,
    UserForm,
)
from accounts.models import User, Employee, Resignation


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
        name = form.data.get("name")
        phone = form.data.get("phone")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            phone=phone,
            name=name,
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
    queryset = None
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

    def get_queryset(self, **kwargs):
        employee = Employee.objects.get(user_id=self.request.user.id)
        if employee.authorization_grade == "MS":
            queryset = Employee.objects.select_related("user")
        else:
            queryset = Employee.objects.select_related("user").exclude(is_resigned=True)
        self.queryset = queryset
        return super().get_queryset()


@login_required(login_url=reverse_lazy("login"))
def signup_user_detail_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    def get_context_data(
        user_form=UserForm(instance=user),
        employee_form=EmployeeForm(),
    ):
        context = {
            "user_form": user_form,
            "employee_form": employee_form,
            "signup_list": True,
        }
        return context

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)

        if user_form.is_valid():
            if "refusal-btn" in request.POST:  # 가입 신청 거절 성공 시
                # User 거절 관련 정보 업데이트
                reason_for_refusal = user_form.cleaned_data.get("reason_for_refusal")
                rejected_at = timezone.now()
                user.reason_for_refusal = reason_for_refusal
                user.rejected_at = rejected_at
                user.state = "RJ"

                fields_to_be_updated = ["state", "reason_for_refusal", "rejected_at"]
                user.save(update_fields=fields_to_be_updated)

                context = get_context_data(user_form=user_form)
                return render(request, "detail.html", context)
            else:  # 가입 신청 시
                employee_form = EmployeeForm(request.POST)

                if employee_form.is_valid():  # 가입 신청 승인 성공으로 Employee 객체 생성 시
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
                        "update_authorization": cleaned_data.get(
                            "update_authorization"
                        ),
                        "resign_authorization": cleaned_data.get(
                            "resign_authorization"
                        ),
                    }

                    employee = Employee.objects.create(
                        user_id=user.id, **authorizations
                    )
                    employee.save()

                    user.state = "AP"
                    return redirect("signup_list")
                else:  # 등급을 선택하지 않고 승인 버튼을 눌렀을 경우
                    context = get_context_data()
                    return render(request, "detail.html", context)
        else:  # 거절 사유를 입력하지 않고 거절 버튼을 눌렀을 경우
            context = get_context_data()
            return render(request, "detail.html", context)

    else:  # GET method일 때
        context = get_context_data()
        return render(request, "detail.html", context)


@login_required(login_url=reverse_lazy("login"))
def employee_detail_view(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    user = get_object_or_404(User, pk=employee.user_id)

    def get_context_data(
        user_form=UserForm(instance=user),
        employee_form=EmployeeForm(instance=employee),
        resignation_form=ResignationForm(),
    ):
        context = {
            "user_form": user_form,
            "employee_form": employee_form,
            "resignation_form": resignation_form,
            "signup_list": False,
            "approval_authorization": True,
            "read_authorization": True,
        }
        return context

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        employee_form = EmployeeForm(request.POST, instance=employee)
        resignation_form = ResignationForm(request.POST)

        if "resignation-btn" in request.POST:  # 퇴사처리 시도 의미
            if resignation_form.is_valid():
                # 퇴사자 정보 생성
                cleaned_data = resignation_form.cleaned_data
                reason_for_resignation = cleaned_data.get("reason_for_resignation")
                resigned_at = timezone.now()
                resignation = Resignation.objects.create(
                    resigned_user=employee,
                    reason_for_resignation=reason_for_resignation,
                    resigned_at=resigned_at,
                )
                resignation.save()

                # 임직원 퇴사 유무 확인 정보 업데이트
                employee.is_resigned = True
                employee.save(update_fields=["is_resigned"])

                context = get_context_data(
                    user_form=user_form,
                    employee_form=employee_form,
                    resignation_form=resignation_form,
                )
                return render(request, "detail.html", context)

            context = get_context_data()
            return render(request, "detail.html", context)
        # 퇴사 처리 이외 정보 변경 시도 의미
        else:
            if user_form.is_valid() and employee_form.is_valid():
                user_cleaned_data = user_form.cleaned_data
                employee_cleaned_data = employee_form.cleaned_data

                # 수정될 user 정보
                name = user_cleaned_data.get("name")
                phone = user_cleaned_data.get("phone")
                user.name = name
                user.phone = phone

                # 수정될 employee 정보
                grade = employee_cleaned_data.get("grade")
                authorizations = {
                    "authorization_grade": grade,
                    "signup_approval_authorization": employee_cleaned_data.get(
                        "signup_approval_authorization"
                    ),
                    "list_read_authorization": employee_cleaned_data.get(
                        "list_read_authorization"
                    ),
                    "update_authorization": employee_cleaned_data.get(
                        "update_authorization"
                    ),
                    "resign_authorization": employee_cleaned_data.get(
                        "resign_authorization"
                    ),
                }

                employee.authorization_grade = grade
                employee.signup_approval_authorization = authorizations.get(
                    "signup_approval_authorization"
                )
                employee.list_read_authorization = authorizations.get(
                    "list_read_authorization"
                )
                employee.update_authorization = authorizations.get(
                    "update_authorization"
                )
                employee.resign_authorization = authorizations.get(
                    "resign_authorization"
                )

                user.save(update_fields=["name", "phone"])
                employee.save(
                    update_fields=[
                        "authorization_grade",
                        "signup_approval_authorization",
                        "list_read_authorization",
                        "update_authorization",
                        "resign_authorization",
                    ]
                )

                context = get_context_data(
                    user_form=user_form,
                    employee_form=employee_form,
                    resignation_form=resignation_form,
                )
                return render(request, "detail.html", context)
    else:
        try:
            resignation = Resignation.objects.get(resigned_user_id=employee.id)
            resignation_form = ResignationForm(instance=resignation)
        except ObjectDoesNotExist:
            resignation_form = ResignationForm()

        context = get_context_data(resignation_form=resignation_form)
        return render(request, "detail.html", context)
