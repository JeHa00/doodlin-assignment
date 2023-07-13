import re

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django import forms

from accounts.models import User, Employee, Resignation


class SignUpForm(forms.Form):
    email = forms.EmailField(
        label="이메일", widget=forms.EmailInput(attrs={"placeholder": "이메일"})
    )
    name = forms.CharField(
        label="이름", widget=forms.TextInput(attrs={"placeholder": "이름"})
    )
    phone = forms.CharField(
        label="연락처", widget=forms.TextInput(attrs={"placeholder": "01012345678"})
    )
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(
            attrs={"placeholder": "PASSWORD", "autocomplete": "new-password"}
        ),
    )
    password_confirm = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput(
            attrs={"placeholder": "PASSWORD 확인", "autocomplete": "new-password"}
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        match = "^[a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z0-9.]+$"
        validation = re.compile(match)

        if User.objects.filter(email=email).last():
            raise ValidationError("이미 존재하는 이메일입니다.")

        if validation.match(str(email)) is None:
            raise ValidationError("영어 대소문자, 언더바(_), 숫자만 포함 가능합니다.")

        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        match = "^(01[0-9]{1})([0-9]{3,4})([0-9]{4})$"
        validation = re.compile(match)

        if validation.match(str(phone)) is None:
            raise ValidationError("정확한 전화번호를 입력해주세요.")
        return phone

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        match = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        validation = re.compile(match)

        if validation.match(str(password)) is None:
            raise ValidationError(
                {"password": "비밀번호는 문자, 숫자, 특수문자 각 하나 이상을 포함하여 8자리 이상으로 작성해주세요."}
            )
        elif validation.match(str(password_confirm)) is None:
            raise ValidationError(
                {
                    "password_confirm": "비밀번호는 문자, 숫자, 특수문자 각 하나 이상을 포함하여 8자리 이상으로 작성해주세요."
                }
            )
        elif password and password_confirm:
            if password != password_confirm:
                raise ValidationError(
                    {
                        "password": ["비밀번호가 일치하지 않습니다."],
                        "password_confirm": ["비밀번호가 일치하지 않습니다."],
                    }
                )
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="이메일",
        widget=forms.EmailInput(attrs={"placeholder": "example@example.com"}),
    )
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(
            attrs={"placeholder": "PASSWORD", "autocomplete": "new-password"}
        ),
    )

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        try:
            user = User.objects.get(email=email)
            if not check_password(password, user.get_password()):
                raise ValidationError({"password": "비밀번호가 잘못되었습니다."})
        except ObjectDoesNotExist:
            raise ValidationError({"email": "가입되지 않은 이메일입니다."})

        return cleaned_data


class UserForm(forms.ModelForm):
    email = forms.CharField(
        label="이메일",
        required=False,
        widget=forms.TextInput(attrs={"disabled": "disabled"}),
    )
    phone = forms.CharField(label="전화번호")
    reason_for_refusal = forms.CharField(
        label="거절 사유",
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "거절 시 거절 사유를 기입하세요.", "rows": 2}),
    )

    state = forms.CharField(label="상태", required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "phone",
            "state",
            "rejected_at",
            "reason_for_refusal",
        ]

    def clean_reason_for_refusal(self):
        if "refusal-btn" in self.data:
            reason_for_refusal = self.cleaned_data.get("reason_for_refusal")
            if not reason_for_refusal:
                raise ValidationError("거절 사유를 입력해야 거절할 수 있습니다.")
            return reason_for_refusal


class EmployeeForm(forms.ModelForm):
    authorization_choices = [("", ""), ("MA", "관리자"), ("ST", "일반")]
    grade = forms.ChoiceField(
        label="등급",
        choices=authorization_choices,
        initial={"authorization_choices": ""},
        required=False,
    )

    class Meta:
        model = Employee
        fields = [
            "grade",
            "signup_approval_authorization",
            "list_read_authorization",
            "update_authorization",
            "resign_authorization",
            "is_resigned",
        ]

    def clean_grade(self):
        if "approval-btn" in self.data:
            grade = self.cleaned_data.get("grade")
            if not grade:
                raise ValidationError("승인 시에는 반드시 등급을 선택해야 합니다.")
        return grade


class ResignationForm(forms.ModelForm):
    resigned_at = forms.DateTimeField(
        label="탈퇴일시",
        required=False,
        widget=forms.TextInput(attrs={"disabled": "disabled"}),
    )
    reason_for_resignation = forms.CharField(
        label="탈퇴 사유",
        required=False,
        widget=forms.Textarea(
            attrs={"placeholder": "탈퇴 시킬 시 탈퇴 사유를 기입하세요.", "rows": 2}
        ),
    )

    class Meta:
        model = Resignation
        fields = ["reason_for_resignation", "resigned_at"]
