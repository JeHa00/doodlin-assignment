from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name="생성일", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="갱신일", auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    class StateChoices(models.TextChoices):
        AWAIT = "AW", "회원가입 승인 대기"
        APPROVAL = "AP", "회원가입 완료"
        REJECTED = "RJ", "회원가입 거절"

    email = models.EmailField(verbose_name="이메일", unique=True)
    phone = models.CharField(
        verbose_name="연락처",
        max_length=11,
        validators=[RegexValidator(r"^010-?[1-9]\d{3}-?\d{4}$")],
    )
    state = models.CharField(
        verbose_name="회원가입 상태", max_length=2, choices=StateChoices.choices
    )
    rejected_at = models.DateTimeField(verbose_name="회원가입 신청 거절일시", null=True)
    reason_for_refusal = models.CharField(
        verbose_name="회원가입 신청 거절 사유", blank=True, max_length=50
    )

    def __str__(self):
        return f"{self.username} {self.state}"

    class Meta:
        verbose_name = "회원가입 신청자"
        verbose_name_plural = "회원가입 신청 목록"


class Employee(models.Model):
    class AuthorizationGradeChoices(models.TextChoices):
        MASTER = "MS", "마스터"
        MANAGER = "MA", "관리자"
        STAFF = "ST", "일반"

    user = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name="임직원")
    authorization_grade = models.CharField(
        verbose_name="등급", max_length=2, choices=AuthorizationGradeChoices.choices
    )
    signup_approval_authorization = models.BooleanField(
        verbose_name="회원가입 승인 권한 유무", default=False
    )
    is_resigned = models.BooleanField(verbose_name="퇴사 유무", default=False)

    def __str__(self):
        return f"{self.user} ({self.authorization_grade})"

    class Meta:
        verbose_name = "임직원"
        verbose_name_plural = "임직원 목록"


class Resignation(models.Model):
    resigned_user = models.ManyToManyField(Employee, verbose_name="퇴사자")
    reason_for_resignation = models.CharField(verbose_name="퇴사 사유", max_length=50)
    resigned_at = models.DateTimeField(verbose_name="퇴사일", auto_now_add=True)

    def __str__(self):
        return f"{self.resigned_user} ({self.resigned_at})"

    class Meta:
        verbose_name = "퇴사자"
        verbose_name_plural = "퇴사자 목록"
