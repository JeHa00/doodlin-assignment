from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name="생성일", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="갱신일", auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    class StateChoices(models.TextChoices):
        AWAIT = "AW", "대기"
        APPROVAL = "AP", "승인"
        REJECTED = "RJ", "거절"

    email = models.EmailField(verbose_name="이메일", unique=True)
    name = models.CharField(verbose_name="이름", max_length=50)
    phone = models.CharField(
        verbose_name="연락처",
        max_length=11,
    )
    state = models.CharField(
        verbose_name="회원가입 상태",
        max_length=2,
        choices=StateChoices.choices,
        default=StateChoices.AWAIT,
    )
    rejected_at = models.DateTimeField(
        verbose_name="회원가입 신청 거절일시",
        blank=True,
        null=True,
    )
    reason_for_refusal = models.CharField(
        verbose_name="회원가입 신청 거절 사유",
        blank=True,
        null=True,
        max_length=50,
    )

    def __str__(self):
        return f"{self.name} {self.state}"

    class Meta:
        verbose_name = "회원가입 내역"
        verbose_name_plural = "회원가입 내역 목록"

    def get_password(self) -> str:
        """User object의 패스워드를 반환한다.

        Returns:
            str: 문자열로 된 패스워드 정보
        """
        return self.password

    def update_last_login(self) -> bool:
        """User의 가장 마지막 로그인 시간을 업데이트한다.

        Returns:
            - bool: 성공시 True
        """
        self.last_login = timezone.now()
        self.save(update_fields=["last_login"])
        return True


class Employee(models.Model):
    class AuthorizationGradeChoices(models.TextChoices):
        MASTER = "MS", "마스터"
        MANAGER = "MA", "관리자"
        STAFF = "ST", "일반"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="임직원",
        on_delete=models.CASCADE,
    )
    authorization_grade = models.CharField(
        verbose_name="등급",
        max_length=2,
        choices=AuthorizationGradeChoices.choices,
        null=True,
    )
    signup_approval_authorization = models.BooleanField(
        verbose_name="가입 승인 권한",
        default=False,
    )

    list_read_authorization = models.BooleanField(
        verbose_name="조회 권한",
        default=True,
    )

    update_authorization = models.BooleanField(
        verbose_name="수정 권한",
        default=False,
    )

    resign_authorization = models.BooleanField(
        verbose_name="탈퇴 권한",
        default=False,
    )

    is_resigned = models.BooleanField(
        verbose_name="퇴사 유무",
        default=False,
    )

    def __str__(self):
        return f"{self.authorization_grade} ({self.signup_approval_authorization})"

    class Meta:
        verbose_name = "임직원"
        verbose_name_plural = "임직원 목록"


class Resignation(models.Model):
    resigned_user = models.OneToOneField(
        Employee,
        verbose_name="퇴사자",
        on_delete=models.CASCADE,
    )
    reason_for_resignation = models.CharField(verbose_name="퇴사 사유", max_length=50)
    resigned_at = models.DateTimeField(verbose_name="퇴사일", blank=True, null=True)

    def __str__(self):
        return f"{self.resigned_user} ({self.resigned_at})"

    class Meta:
        verbose_name = "퇴사자"
        verbose_name_plural = "퇴사자 목록"
