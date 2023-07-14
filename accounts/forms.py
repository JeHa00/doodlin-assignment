import re

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django import forms

from accounts.models import User, Employee, Resignation


class SignUpForm(forms.Form):
    email = forms.EmailField(
        label="이메일", widget=forms.EmailInput(attrs={"placeholder": "이메일"}),
    )
    name = forms.CharField(
        label="이름", widget=forms.TextInput(attrs={"placeholder": "이름"}),
    )
    phone = forms.CharField(
        label="연락처", widget=forms.TextInput(attrs={"placeholder": "01012345678"}),
    )
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(
            attrs={"placeholder": "PASSWORD", "autocomplete": "new-password"},
        ),
    )
    password_confirm = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput(
            attrs={"placeholder": "PASSWORD 확인", "autocomplete": "new-password"},
        ),
    )

    def clean_email(self) -> str:
        """회원가입 시 입력한 이메일에 대해 유효성 검증을 한다.

        Raises:
            ValidationError: 이미 존재하는 이메일일 경우 발생
            ValidationError: 내부 이메일 로직에 맞지 않을 경우 발생

        Returns:
            str: 유효성 검증에 통과한 이메일을 반환한다.
        """

        email = self.cleaned_data.get("email")

        match = "^[a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z0-9.]+$"
        validation = re.compile(match)

        if User.objects.filter(email=email).last():
            raise ValidationError("이미 존재하는 이메일입니다.")

        if validation.match(str(email)) is None:
            raise ValidationError("영어 대소문자, 언더바(_), 숫자만 포함 가능합니다.")

        return email

    def clean_phone(self) -> str:
        """휴대폰 번호에 대해 아래 조건에 대해 유효성 검증을 한다.
        - 010부터 019까지의 핸드폰 번호를 포함한다.
        - 가운데 자리는 3자리 또는 4자리
        - 가장 마지막 자리는 4자리

        Raises:
            ValidationError: 휴대폰 번호가 정규식 표현에 맞지 않을 경우 발생

        Returns:
            str: 유효성 검증에 통과한 휴대폰 번호를 반환한다.
        """
        phone = self.cleaned_data.get("phone")
        match = "^(01[0-9]{1})([0-9]{3,4})([0-9]{4})$"
        validation = re.compile(match)

        if validation.match(str(phone)) is None:
            raise ValidationError("정확한 전화번호를 입력해주세요.")
        return phone

    def clean(self) -> dict:
        """가입 시 입력된 비밀번호가 내부 정책에 적합한지와 패스워드와 확인 패스워드가 일치한지 확인한다.

        Raises:
            ValidationError: 패스워드가 내부 정책에 적합하지 않으면 발생한다.
            ValidationError: 확인 패스워드가 내부 정책에 적합하지 않으면 발생한다.
            ValidationError: 내부 정책에는 적합하지만 패스워드와 확인 패스워드가 일치하지 않으면 발생한다.

        Returns:
            dict: SignUpForm 의 유효성 검증에 통과한 전체 데이터를 반환한다.
        """
        cleaned_data = super(SignUpForm, self).clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        match = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        validation = re.compile(match)

        if validation.match(str(password)) is None:
            raise ValidationError(
                {"password": "비밀번호는 문자, 숫자, 특수문자 각 하나 이상을 포함하여 8자리 이상으로 작성해주세요."},
            )
        elif validation.match(str(password_confirm)) is None:
            raise ValidationError(
                {
                    "password_confirm": "비밀번호는 문자, 숫자, 특수문자 각 하나 이상을 포함하여 8자리 이상으로 작성해주세요.",
                },
            )
        elif password and password_confirm:
            if password != password_confirm:
                raise ValidationError(
                    {
                        "password": ["비밀번호가 일치하지 않습니다."],
                        "password_confirm": ["비밀번호가 일치하지 않습니다."],
                    },
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
            attrs={"placeholder": "PASSWORD", "autocomplete": "new-password"},
        ),
    )

    def clean(self) -> dict:
        """로그인 시 입력한 이메일과 패스워드에 대해 유효성 검증을 실시한다.


        Raises:
            ValidationError: 입력한 비밀번호가 입려한 이메일로 저장된 유저의 비밀번호가 다를 경우 발생한다.
            ValidationError: 입력한 이메일이 가입되지 않은 이메일이면 발생한다.

        Returns:
            dict: LoginForm 의 유효성 검증에 통과한 전체 데이터를 반환한다.
        """
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
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
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

    def clean_reason_for_refusal(self) -> str:
        """회원가입 신청 거절 시 거절 사유에 대한 유효성 검증을 실시한다.
            가입 대기 목록에서 상세 화면 상황 중 승인을 거절할 시
            거절 사유를 입력하지 않으면 에러를 발생시킨다.

            또한 거절 권한이 없을 경우 self.errors에 에러 내용이 저장되어
            화면에 나타난다.


        Raises:
            ValidationError: 거절 사유 미입력 시 발생한다.
            - 거절이 없을 경우 발생

        Returns:
            str: 입력된 거절 사유가 반환된다.
        """
        if "refusal-btn" in self.data:
            reason_for_refusal = self.cleaned_data.get("reason_for_refusal")
            if self.errors:
                return reason_for_refusal
            elif not reason_for_refusal:
                raise ValidationError("거절 사유를 입력해야 거절할 수 있습니다.")
            return reason_for_refusal


class EmployeeForm(forms.ModelForm):
    authorization_choices = [("", ""), ("MA", "관리자"), ("ST", "일반")]
    authorization_grade = forms.ChoiceField(
        label="등급",
        choices=authorization_choices,
        initial={"authorization_choices": ""},
        required=False,
    )

    class Meta:
        model = Employee
        fields = [
            "authorization_grade",
            "signup_approval_authorization",
            "list_read_authorization",
            "update_authorization",
            "resign_authorization",
            "is_resigned",
        ]


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
            attrs={"placeholder": "탈퇴 시킬 시 탈퇴 사유를 기입하세요.", "rows": 2},
        ),
    )

    class Meta:
        model = Resignation
        fields = ["reason_for_resignation", "resigned_at"]

    def clean_reason_for_resignation(self) -> str:
        """퇴사 사유에 대해 유효성 검증을 실시한다.
            회원 목록의 상세 화면에서 임직원을 퇴사시킬 시 퇴사 사유를 입력 되었는지
            퇴사 시킬 권한이 있는지 확인한다.

        Raises:
            ValidationError: 퇴사 사유 미 입력 시 발생
            - 또한 resign_authorization이 false이면 발생
            - view와 utils.py에서 확인할 수 있다.

        Returns:
            str: 유효성 검증을 통과한 퇴사 사유를 반환한다.
        """
        if "resignation-btn" in self.data:
            reason_for_resignation = self.cleaned_data.get("reason_for_resignation")
            if not reason_for_resignation:
                raise ValidationError("퇴사 사유를 입력해야 탈퇴시킬 수 있습니다.")
            return reason_for_resignation

    def clean(self) -> dict:
        """ResignationForm에 입력된 전체 데이터에 대한 유효성 검증을 실시한다.

        Raises:
            ValidationError: 이미 탈퇴된 유저인 경우 (Resignation 인스턴스인 경우)

        Returns:
            dict: 유효성 검증이 통과된 ResignationForm 데이터를 반환한다.
        """
        if "resignation-btn" in self.data:
            cleaned_data = super(ResignationForm, self).clean()

            user = User.objects.filter(
                name=self.data.get("name"), phone=self.data.get("phone"),
            ).last()

            employee = Employee.objects.filter(user_id=user.id).last()
            resigned_user = Resignation.objects.filter(
                resigned_user_id=employee.id,
            ).last()

            if resigned_user:
                raise ValidationError({"reason_for_resignation": "이미 탈퇴된 유저입니다."})

            return cleaned_data
