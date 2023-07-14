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
        else:
            return redirect("guide")

    return decorator_func


def get_authorizations(current_user_grade, cleaned_data):
    if current_user_grade == "MS":
        authorizations = {
            "authorization_grade": cleaned_data.get("authorization_grade"),
            "signup_approval_authorization": cleaned_data.get(
                "signup_approval_authorization"
            ),
            "list_read_authorization": cleaned_data.get("list_read_authorization"),
            "update_authorization": cleaned_data.get("update_authorization"),
            "resign_authorization": cleaned_data.get("resign_authorization"),
        }

    elif current_user_grade == "MA":
        authorizations = {
            "signup_approval_authorization": cleaned_data.get(
                "signup_approval_authorization"
            ),
            "list_read_authorization": cleaned_data.get("list_read_authorization"),
            "update_authorization": cleaned_data.get("update_authorization"),
            "resign_authorization": cleaned_data.get("resign_authorization"),
        }
    return authorizations


class CheckAuthAndAddError:
    def __init__(self, current_user_id, target_user_id):
        self.current_employee = Employee.objects.filter(user_id=current_user_id).last()
        self.target_employee = Employee.objects.filter(user_id=target_user_id).last()
        self.target_user = User.objects.filter(pk=self.target_employee.user_id).last()
        self.auth_grade = self.current_employee.authorization_grade
        self.update_auth = self.current_employee.update_authorization

    def check_to_do_refusal(
        self,
        user_form,
    ) -> bool:
        if self.auth_grade == "MS":
            return True
        else:
            user_form.add_error("reason_for_refusal", "거절할 권한이 없습니다.")
            return False

    def check_to_do_resignation(
        self,
        resignation_form,
    ) -> bool:
        if self.auth_grade == "MS":
            return True
        else:
            resignation_form.add_error("reason_for_resignation", "탈퇴시킬 권한이 없습니다.")
            return False

    def check_to_update_grade(
        self,
        employee_form,
    ) -> bool:
        if self.auth_grade == "MS":
            return True
        else:
            before_grade = self.target_employee.authorization_grade
            grade_to_be_updated = employee_form.cleaned_data["authorization_grade"]
            if before_grade != grade_to_be_updated:
                employee_form.add_error("authorization_grade", "등급을 변경할 권한이 없습니다.")
                return False

    def check_to_update_user_name_or_phone(
        self,
        user_form,
        target_field,
    ) -> bool:
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
                        before_target_field = self.target_user.name
                    else:
                        before_target_field = self.target_user.phone
                    after_target_field = user_form.cleaned_data[target_field]
                    if before_target_field != after_target_field:
                        user_form.add_error(
                            target_field, f"해당 유저의 {field_error}을 변경할 권한이 없습니다."
                        )
                        return False

                else:
                    return True
            else:
                user_form.add_error(
                    target_field, f"해당 유저의 {field_error}을 변경할 권한이 없습니다."
                )
                return False
        else:
            if target_field == "name":
                before_target_field = self.target_user.name
            else:
                before_target_field = self.target_user.phone
            after_target_field = user_form.cleaned_data[target_field]
            if before_target_field != after_target_field:
                user_form.add_error(
                    target_field, f"해당 유저의 {field_error}을 변경할 권한이 없습니다."
                )
                return False

    def check_to_update_auth(
        self,
        employee_form,
    ) -> bool:
        if self.auth_grade == "MS":
            return True
        elif self.auth_grade == "MA":
            if self.target_employee.authorization_grade != "ST":
                before_auth = {
                    "signup_approval_authorization": self.target_employee.signup_approval_authorization,
                    "list_read_authorization": self.target_employee.list_read_authorization,
                    "update_authorization": self.target_employee.update_authorization,
                    "resign_authorization": self.target_employee.resign_authorization,
                }

                after_auth = {
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
                    if before_auth[auth] != after_auth[auth]:
                        employee_form.add_error(auth, "권한들을 변경할 수 없습니다.")
                    return False
                return True
            else:
                return True
        else:
            before_auth = {
                "signup_approval_authorization": self.target_employee.signup_approval_authorization,
                "list_read_authorization": self.target_employee.list_read_authorization,
                "update_authorization": self.target_employee.update_authorization,
                "resign_authorization": self.target_employee.resign_authorization,
            }

            after_auth = {
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
                if before_auth[auth] != after_auth[auth]:
                    employee_form.add_error(auth, "권한들을 변경할 수 없습니다.")
            return True
            # return False

    def check_in_employee_list(self, employee_form, user_form, name, phone):
        self.check_to_update_auth(employee_form)
        self.check_to_update_grade(employee_form)
        self.check_to_update_user_name_or_phone(user_form, name)
        self.check_to_update_user_name_or_phone(user_form, phone)