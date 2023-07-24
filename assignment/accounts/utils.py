from typing import Any

from django.shortcuts import redirect

from accounts.forms import UserForm, EmployeeForm, ResignationForm
from accounts.models import User, Employee


def authorization_filter_on_signup_list(function) -> Any:
    """가입 대기 목록 진입 자격을 걸러준다.
        임직원 회원으로 등록되어 있고, 가입 신청 승인 권한이 있을 경우 signup_list에 들어갈 수 있다.
    Args:
        function (func): SignupListView 의미

    Returns:
        - guide:  임직원 회원으 등록이 안되어 있으면 가입 승인 권한 안내 화면으로 이동한다.
        - employee_list: 임직원 회원이지만 가입 신청 승인 허가가 없으면 회원 목록 화면으로 이동한다.
    """

    def decorator_func(request):
        if request.user.state == "AP":
            employee = Employee.objects.filter(user_id=request.user.id).last()
            if employee.signup_approval_authorization:
                return function(request)
            else:
                return redirect("employee_list")
        else:
            return redirect("guide")

    return decorator_func


def authorization_filter_on_employee_list(function) -> Any:
    """회원 목록 진입 자격을 걸러준다.
       임직원 회원으로 등록되어 있고, 회원 조회 권한이 있을 경우 employee_list에 진입할 수 있다.

    Args:
        function (func):  EmployeeListView를 의미한다.

    Returns:
        Any: 임직원으로 등록되어 있지 않거나, 조회 권한이 없으면
             guide view로 이동한다.
    """

    def decorator_func(request):
        if request.user.state == "AP":
            employee = Employee.objects.filter(user_id=request.user.id).last()
            if employee.list_read_authorization:
                return function(request)
            else:
                return redirect("guide")
        else:
            return redirect("guide")

    return decorator_func


def get_authorizations(current_user_grade: str, cleaned_data: dict) -> dict:
    """cleaned_data로부터 얻어낸 권한들에 대한 값들을 딕셔너리 형태로 정리해준다.

    Args:
        current_user_grade (str): "MS"와 "MA" 중 하나를 나타낸다.
        cleaned_data (dict): EmployeeForm으로부터 반환된 cleaned_data를 의미한다.

    Returns:
        dict: MS이면 등급을 포함하고, MA이면 등급을 미포함하여 권한들을 반환한다.
    """
    if current_user_grade == "MS":
        authorizations = {
            "authorization_grade": cleaned_data.get("authorization_grade"),
            "signup_approval_authorization": cleaned_data.get(
                "signup_approval_authorization",
            ),
            "list_read_authorization": cleaned_data.get("list_read_authorization"),
            "update_authorization": cleaned_data.get("update_authorization"),
            "resign_authorization": cleaned_data.get("resign_authorization"),
        }

    elif current_user_grade == "MA":
        authorizations = {
            "signup_approval_authorization": cleaned_data.get(
                "signup_approval_authorization",
            ),
            "list_read_authorization": cleaned_data.get("list_read_authorization"),
            "update_authorization": cleaned_data.get("update_authorization"),
            "resign_authorization": cleaned_data.get("resign_authorization"),
        }
    return authorizations


class CheckAuthAndAddError:
    def __init__(self, current_user_id: int, target_user_id: int) -> None:
        self.current_employee = Employee.objects.filter(user_id=current_user_id).last()
        self.target_employee = Employee.objects.filter(user_id=target_user_id).last()
        self.target_user = User.objects.filter(pk=target_user_id).last() # FIXME: self.target_employee.user_id였지만 수정완료.
        self.auth_grade = self.current_employee.authorization_grade
        self.update_auth = self.current_employee.update_authorization

    def check_to_do_refusal(
        self,
        user_form: UserForm,
    ) -> bool:
        """현재 로그인된 유저가 refusal 권한이 있는지 확인한다.
            인증 등급이 마스터 등급이면 가입 신청 승인을 거절할 수 있다. 하지만 그 외의 등급은 할 수 없다.

        Args:
            user_form (UserForm): user_form의 cleaned_data 에서 reason_for_refusal
            라는 key 값에 대한 값을 None으로 바꾸면서 유효성 검증 시 발생할 에러에 다음 에러 내용을 추가한다.

        Returns:
            bool: 거절할 권한이 있으면 True, 없으면 False
        """
        if self.auth_grade == "MS":
            return True
        else:
            user_form.add_error("reason_for_refusal", "거절할 권한이 없습니다.")
            return False

    def check_to_do_resignation(
        self,
        resignation_form: ResignationForm,
    ) -> bool:
        """현재 로그인된 유저가 탈퇴시킬 권한이 있는지 확인한다.
            마스터 등급이면 탈퇴시킬 수 있으나 그 외 등급은 탈퇴시킬 수 없다.

        Args:
            - resignation_form (ResignationForm): resignation_form의 cleaned_data 에서
                reason_for_refusal 라는 key 값에 대한 값을 None으로 바꾸면서
                유효성 검증 시 발생할 에러에 다음 에러 내용을 추가한다.

        Returns:
            bool: 거절할 권한이 있으면 True, 없으면 False
        """
        if self.auth_grade == "MS":
            return True
        else:
            resignation_form.add_error("reason_for_resignation", "탈퇴시킬 권한이 없습니다.")
            return False

    def check_to_update_grade(
        self,
        employee_form: EmployeeForm,
    ) -> bool:
        """현재 임직원과 변경 대상인 임직원의 등급을 비교해서 authorization_grade를 변경할 권한이 있는지 확인한다.
            내부 정책에 따르면 마스터 등급만이 등급을 변경할 수 있다.
            등급 변경 시도는 target이 되는 employee의 이전 값과 cleaned_data에 잇는 값을 비교하여
            달라지면 변경을 시도하는 것으로 파악한다.

        Args:
            employee_form (EmployeeForm): EmployeeForm을 통해서 유효성 검사가 끝난 데이터를 가지고 있는 Form

        Returns:
            bool: 인증 등급을 변경할 수 없으면 False를 반환한다.
        """
        if self.auth_grade == "MS":
            return True
        else:
            previous_grade = self.target_employee.authorization_grade
            next_grade = employee_form.cleaned_data["authorization_grade"]
            if previous_grade != next_grade:
                employee_form.add_error("authorization_grade", "등급을 변경할 권한이 없습니다.")
                return False

    def check_to_update_user_name_or_phone(
        self,
        user_form: UserForm,
        target_field: str,
    ) -> bool:
        """현재 로그인된 user의 등급과 변경 대상인 user의 등급을 비교하고
            이전 값과 user_form을 통해 새로 입력한 값과 비교하여 값이 변했으면
            변경 시도로 파악하여 등급에 따라 에러를 발생시킨다.

        Args:
            user_form (UserForm): name과 phone 정보를 가지고 있다.
            target_field (str): name 또는 phone을 가리킨다.

        Returns:
            bool: 권한이 없으면 False, 있으면 True를 반환한다.
        """
        if target_field == "name":
            field_error = "이름"
        else:
            field_error = "전화번호"

        if self.auth_grade == "MS":
            return True
        elif self.auth_grade == "MA":
            if self.update_auth:
                if self.target_employee.authorization_grade == "MS":
                    if target_field == "name":
                        previous_target_field = self.target_user.name
                    else:
                        previous_target_field = self.target_user.phone
                    next_target_field = user_form.cleaned_data[target_field]
                    if previous_target_field != next_target_field:
                        user_form.add_error(
                            target_field,
                            f"해당 유저의 {field_error}을 변경할 권한이 없습니다.",
                        )
                        return False

                else:
                    return True
            else:  # 회원 수정 권한이 없을 때
                user_form.add_error(
                    target_field,
                    f"해당 유저의 {field_error}을 변경할 권한이 없습니다.",
                )
                return False
        else:  # "ST" 일 때
            if target_field == "name":
                previous_target_field = self.target_user.name
            else:
                previous_target_field = self.target_user.phone
            next_target_field = user_form.cleaned_data[target_field]
            if previous_target_field != next_target_field:
                user_form.add_error(
                    target_field,
                    f"해당 유저의 {field_error}을 변경할 권한이 없습니다.",
                )
                return False

    def check_to_update_auth(
        self,
        employee_form: EmployeeForm,
    ) -> bool:
        """현재 로그인된 임직원과 변경 대상인 임직원의 등급을 비교하여
           Employee model의 4가지 권한을 수정할 수 있는지 판단한다.

           변경 시도를 하는지 판단은 변경 대상의 임직원의 form 입력 전값과 입력 후 값을 비교한다.

        Args:
            employee_form (EmployeeForm): 권한들에 대한 정보를 가지고 있는 form

        Returns:
            bool: 권한이 있으면 True, 없으면 False를 반환한다.
        """
        if self.auth_grade == "MS":
            return True
        elif self.auth_grade == "MA":
            if (
                self.target_employee.authorization_grade != "ST"
            ):  # 현재 등급이 매니저이고 대상 등급이 일반이 아닌 경우
                previous_auth = {
                    "signup_approval_authorization": self.target_employee.signup_approval_authorization,
                    "list_read_authorization": self.target_employee.list_read_authorization,
                    "update_authorization": self.target_employee.update_authorization,
                    "resign_authorization": self.target_employee.resign_authorization,
                }

                next_auth = {
                    "signup_approval_authorization": employee_form.cleaned_data[
                        "signup_approval_authorization"
                    ],
                    "list_read_authorization": employee_form.cleaned_data[
                        "list_read_authorization"
                    ],
                    "update_authorization": employee_form.cleaned_data[
                        "update_authorization"
                    ],
                    "resign_authorization": employee_form.cleaned_data[
                        "resign_authorization"
                    ],
                }

                total_auth = [
                    "signup_approval_authorization",
                    "list_read_authorization",
                    "update_authorization",
                    "resign_authorization",
                ]

                for auth in total_auth:
                    if previous_auth[auth] != next_auth[auth]:
                        employee_form.add_error(auth, "권한들을 변경할 수 없습니다.")
                    return False
                return True
            else:
                return True
        else:  # 현재 로그인된 임직원의 등급이 ST인 경우
            previous_auth = {
                "signup_approval_authorization": self.target_employee.signup_approval_authorization,
                "list_read_authorization": self.target_employee.list_read_authorization,
                "update_authorization": self.target_employee.update_authorization,
                "resign_authorization": self.target_employee.resign_authorization,
            }

            next_auth = {
                "signup_approval_authorization": employee_form.cleaned_data[
                    "signup_approval_authorization"
                ],
                "list_read_authorization": employee_form.cleaned_data[
                    "list_read_authorization"
                ],
                "update_authorization": employee_form.cleaned_data[
                    "update_authorization"
                ],
                "resign_authorization": employee_form.cleaned_data[
                    "resign_authorization"
                ],
            }

            total_auth = [
                "signup_approval_authorization",
                "list_read_authorization",
                "update_authorization",
                "resign_authorization",
            ]

            for auth in total_auth:
                if previous_auth[auth] != next_auth[auth]:
                    employee_form.add_error(auth, "권한들을 변경할 수 없습니다.")
            return True

    def check_in_employee_list(
        self,
        employee_form: EmployeeForm,
        user_form: UserForm,
        name: str,
        phone: str,
    ) -> None:
        """위에서 언급된 employee_form과 user_form에 관한 점검 포인트를
            한 곳에 모아놓는다.

        Args:
            employee_form (EmployeeForm): EmployeeForm의 form data
            user_form (UserForm): UserForm의 form data
            name (str): User의 name 값
            phone (str): User의 phone 값
        """
        self.check_to_update_auth(employee_form)
        self.check_to_update_grade(employee_form)
        self.check_to_update_user_name_or_phone(user_form, name)
        self.check_to_update_user_name_or_phone(user_form, phone)
