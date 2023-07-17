from typing import Any
from django import http

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.http import HttpRequest, HttpResponse
from django.views.generic import FormView, ListView
from django.contrib.auth import login, logout
from django.views.generic.base import View
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q

from config.settings.base import COUNTS_PER_PAGE
from accounts.utils import (
    authorization_filter_on_employee_list,
    authorization_filter_on_signup_list,
    CheckAuthAndAddError,
    get_authorizations,
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
def guide_view(request: HttpRequest):
    """
    로그인 된 유저의 상태가 승인(AP)상태이면 임직원으로 등록되어 있기 때문에,
    임직원으로 조회하여 회원 조회 권한의 유무를 플래그 변수를 사용하여 전달해서
    guide.html의 가이드 종류가 달라진다.
    """
    context = dict()
    if request.user.state == "AP":
        employee = Employee.objects.get(user_id=request.user.id)

        if not employee.list_read_authorization:
            context["AP"] = True
    else:
        context["AP"] = False

    return render(request, "guide.html", context)


@login_required(login_url=reverse_lazy("login"))
def logout_view(request: HttpRequest):
    """
    django 자체 logout 함수를 사용하여 로그아웃처리 후 로그인 화면으로 리다이렉트한다.
    """
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
        """
        success_url이 1개가 아닌 여러 개일 때 사용한다.
        """
        return self.redirect_url()

    def form_valid(self, form):
        email = form.data.get("email")
        user = User.objects.filter(email=email).last()

        user.update_last_login()
        login(self.request, user)

        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def redirect_url(self):
        """
        로그인 후 어느 화면으로 갈지 결정해준다.

        현재 로그인된 유저의 상태가 승인 (AP) 상태이면 이 유저의 임직원 정보를 얻는다.
        이 임직원의 가입 신청 승인 권한이 있을 경우  signup_list로,
        해당 권한이 없으면 employee_list로 이동한다.
        """
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
    """
    승인 상태가 아닌 조건과 superuser가 아닌 유저 조건에ㅔ 만족하는 queryset 을 가져와
    template_name에 해당하는 html에 전달해주는 view

    - read_authorization: 읽기 권한이 있어야 사이드 바에 회원 목록 바를 볼 수 있어서 전달한다.
    - signup_list key: singup_list 인지 employee_list인 구분해주는 플래그 변수
    """

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
        """
        마스터 등급은 퇴사자 명단을 볼 수 있고, 그 이외 등급은 퇴사자 명단을 볼 수 없도록
        queryset을 구분한다.
        """
        employee = Employee.objects.get(user_id=self.request.user.id)
        if employee.authorization_grade == "MS":
            queryset = Employee.objects.select_related("user")
        else:
            queryset = Employee.objects.select_related("user").exclude(is_resigned=True)
        self.queryset = queryset
        return super().get_queryset()


@login_required(login_url=reverse_lazy("login"))
def employee_detail_view(
    request: HttpRequest,
    employee_id: int,
) -> Any:
    """
    해당 detail view에는 UserForm, EmployeeForm 그리고 ResignationForm 모두를 사용하고 있다.
    - 퇴사인 경우 EmployeeForm과 Resignation을 사용한다.
    - 그 외 정보 업데이트 경우, UserForm, EmployeeForm을 사용한다.


    - "resignation-btn" 과 "update-btn"은 detail.html의 button tag의 name을 의미


    Args:
        request (HttpRequest): request 요청
        user_id (int): 상세화면으로 조회할 target user의 id

    """
    target_employee = get_object_or_404(Employee, pk=employee_id)
    target_user = get_object_or_404(User, pk=target_employee.user_id)

    compare_auth_and_add_error = CheckAuthAndAddError(request.user.id, target_user.id)

    def get_context_data(
        user_form=UserForm(instance=target_user),
        employee_form=EmployeeForm(instance=target_employee),
        resignation_form=ResignationForm(),
    ):
        """
        계속해서 사용하는 context 형태를 반복 입력하는 걸 방지하고자 만든 함수
        """
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
        user_form = UserForm(request.POST, instance=target_user)
        employee_form = EmployeeForm(request.POST, instance=target_employee)
        resignation_form = ResignationForm(request.POST)
        if "resignation-btn" in request.POST:  # 퇴사처리 시
            compare_auth_and_add_error.check_to_do_resignation(resignation_form)
            if resignation_form.is_valid():
                # 퇴사자 정보 생성
                cleaned_data = resignation_form.cleaned_data
                reason_for_resignation = cleaned_data.get("reason_for_resignation")
                resigned_at = timezone.now()
                resignation = Resignation.objects.create(
                    resigned_user=target_employee,
                    reason_for_resignation=reason_for_resignation,
                    resigned_at=resigned_at,
                )
                resignation.save()

                # 임직원 퇴사 유무 확인 정보 업데이트
                target_employee.is_resigned = True
                target_employee.save(update_fields=["is_resigned"])

                context = get_context_data(
                    user_form=user_form,
                    employee_form=employee_form,
                    resignation_form=resignation_form,
                )
                return render(request, "detail.html", context)

            context = get_context_data(resignation_form=resignation_form)
            return render(request, "detail.html", context)

        else:  # 퇴사 처리 외 정보들 변경 시
            if user_form.is_valid() and employee_form.is_valid():
                update_fields = []

                # 권한 비교 및 유효성 추가 검증 확인
                compare_auth_and_add_error.check_in_employee_list(
                    employee_form,
                    user_form,
                    "name",
                    "phone",
                )

                # 권한에 따른 대상 employee_form에서 저장할 데이터 선별
                for key, value in employee_form.cleaned_data.items():
                    if not value:
                        continue
                    update_fields.append(key)

                target_employee.save(update_fields=update_fields)
                update_fields.clear()

                # 권한에 따른 대상 user_form에서 저장할 데이터 선별
                for key, value in user_form.cleaned_data.items():
                    if not value:
                        continue
                    update_fields.append(key)

                target_user.save(update_fields=update_fields)

                context = get_context_data(
                    user_form=user_form,
                    employee_form=employee_form,
                    resignation_form=resignation_form,
                )
                return render(request, "detail.html", context)

            context = get_context_data(
                user_form=user_form,
                employee_form=employee_form,
                resignation_form=resignation_form,
            )
            return render(request, "detail.html", context)

    else:  # get 요청
        try:
            resignation = Resignation.objects.get(resigned_user_id=target_employee.id)
            resignation_form = ResignationForm(instance=resignation)
        except ObjectDoesNotExist:
            resignation_form = ResignationForm()

        context = get_context_data(resignation_form=resignation_form)
        return render(request, "detail.html", context)


@method_decorator(login_required(login_url=reverse_lazy("login")), name="get")
class SetFormView(View):
    user_form = None
    employee_form = None
    resignation_form = None
    target_user = None
    compare_auth_and_add_error = None

    def set_employee_form(self, request, instance):
        self.employee_form = EmployeeForm(
            request,
            instance=instance,
        )
        return self.employee_form

    def set_user_form(self, request, instance):
        self.user_form = UserForm(
            request,
            instance=instance,
        )
        return self.user_form

    def set_resignation_form(self, request, instance):
        self.user_form = ResignationForm(
            request,
            instance=instance,
        )
        return self.resignation_form


class SignupDetailView(SetFormView):
    current_employee = None

    """
    해당 detail view에는 UserForm과 EmployeeForm 모두를 사용하고 있다.
    회원 가입 승인 거절인 경우 UserForm을 사용하고, 단순한 가입신청 승인일 경우 두 form 모두 필요.

    - "refusal-btn" 과 "approval-btn"은 detail.html의 button tag의 name을 의미

    Args:
        request (HttpRequest): request 요청
        user_id (int): 상세화면으로 조회할 target user의 id

    """

    def dispatch(
        self, request: HttpRequest, user_id, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        self.current_employee = Employee.objects.filter(user_id=request.user.id).last()
        self.target_user = User.objects.filter(pk=user_id).last()
        self.set_user_form(None, self.target_user)
        self.set_employee_form(None, None)
        return super().dispatch(request, user_id, *args, **kwargs)

    def get_context_data(self):
        context = {
            "user_form": self.user_form,
            "employee_form": self.employee_form,
            "signup_list": True,
        }

        return context

    def get(self, request: HttpRequest, user_id: int):
        context = self.get_context_data()
        return render(request, "detail.html", context)

    def update_when_refusal_btn(self):
        self.compare_auth_and_add_error.check_to_do_refusal(self.user_form)

        reason_for_refusal = self.user_form.cleaned_data.get("reason_for_refusal")
        self.target_user.reason_for_refusal = reason_for_refusal
        self.target_user.rejected_at = timezone.now()
        self.target_user.state = "RJ"

        self.target_user.save(
            update_fields=["state", "reason_for_refusal", "rejected_at"]
        )

        return True

    def update_when_approval_btn(self):
        # 가입 신청 승인을 master가 했을 경우
        if self.current_employee.authorization_grade == "MS":
            authorizations = get_authorizations(
                "MS",
                self.employee_form.cleaned_data,
            )

            employee = Employee.objects.create(
                user_id=self.target_user.id,
                **authorizations,
            )

        # 가입 신청 승인을 관리자 등급이 했을 경우
        elif self.current_employee.authorization_grade == "MA":
            employee = Employee.objects.create(user_id=self.target_user.id)

        self.target_user.state = "AP"
        self.target_user.save(update_fields=["state"])
        employee.save()

        return True

    def post(self, request, user_id):
        self.set_user_form(request.POST, self.target_user)
        if self.user_form.is_valid():
            if "refusal-btn" in request.POST:  # 가입 신청 거절 시
                self.update_when_refusal_btn(self)
                return render(request, "detail.html", context)
            else:  # 가입 신청 승인 시
                self.set_employee_form(request.POST, None)
                if self.employee_form.is_valid():
                    self.update_when_approval_btn()
                    return redirect("signup_list")
                else:  # 등급을 선택하지 않고 승인 버튼을 눌렀을 경우
                    return render(request, "detail.html", context)

        else:  # 거절 사유를 입력하지 않고 거절 버튼을 눌렀을 경우
            context = self.get_context_data()
            return render(request, "detail.html", context)
