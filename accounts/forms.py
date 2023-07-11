import re

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django import forms

from accounts.models import User


class SignUpForm(forms.Form):
    email = forms.EmailField(
        label="이메일", widget=forms.EmailInput(attrs={"placeholder": "이메일"})
    )
    username = forms.CharField(
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
        label="이메일", widget=forms.EmailInput(attrs={"placeholder": "이메일"})
    )
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(
            attrs={"placeholder": "비밀번호", "autocomplete": "new-password"}
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not User.objects.filter(email=email).exists():
            raise ValidationError("가입되지 않은 이메일입니다.")

        return email

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        user = User.objects.get(email=email)
        if not check_password(password, user.get_password()):
            raise ValidationError({"password": "비밀번호가 잘못되었습니다."})

        return cleaned_data
