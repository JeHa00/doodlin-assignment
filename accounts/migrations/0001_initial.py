# Generated by Django 4.2.3 on 2023-07-12 19:13

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login",
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists.",
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator(),
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성일"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="갱신일")),
                (
                    "email",
                    models.EmailField(max_length=254, unique=True, verbose_name="이메일"),
                ),
                ("name", models.CharField(max_length=50)),
                ("phone", models.CharField(max_length=11, verbose_name="연락처")),
                (
                    "state",
                    models.CharField(
                        choices=[("AW", "대기"), ("AP", "승인"), ("RJ", "거절")],
                        default="AW",
                        max_length=2,
                        verbose_name="회원가입 상태",
                    ),
                ),
                (
                    "rejected_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="회원가입 신청 거절일시",
                    ),
                ),
                (
                    "reason_for_refusal",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="회원가입 신청 거절 사유",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "회원가입 내역",
                "verbose_name_plural": "회원가입 내역 목록",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "authorization_grade",
                    models.CharField(
                        choices=[("MS", "마스터"), ("MA", "관리자"), ("ST", "일반")],
                        max_length=2,
                        verbose_name="등급",
                    ),
                ),
                (
                    "signup_approval_authorization",
                    models.BooleanField(default=False, verbose_name="가입 승인 권한"),
                ),
                (
                    "list_read_authorization",
                    models.BooleanField(default=True, verbose_name="조회 권한"),
                ),
                (
                    "update_authorization",
                    models.BooleanField(default=False, verbose_name="수정 권한"),
                ),
                (
                    "resign_authorization",
                    models.BooleanField(default=False, verbose_name="탈퇴 권한"),
                ),
                (
                    "is_resigned",
                    models.BooleanField(default=False, verbose_name="퇴사 유무"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="임직원",
                    ),
                ),
            ],
            options={
                "verbose_name": "임직원",
                "verbose_name_plural": "임직원 목록",
            },
        ),
        migrations.CreateModel(
            name="Resignation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "reason_for_resignation",
                    models.CharField(max_length=50, verbose_name="퇴사 사유"),
                ),
                (
                    "resigned_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="퇴사일"),
                ),
                (
                    "resigned_user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.employee",
                        verbose_name="퇴사자",
                    ),
                ),
            ],
            options={
                "verbose_name": "퇴사자",
                "verbose_name_plural": "퇴사자 목록",
            },
        ),
    ]
