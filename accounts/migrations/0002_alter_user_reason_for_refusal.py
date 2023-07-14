# Generated by Django 4.2.3 on 2023-07-12 19:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="reason_for_refusal",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="회원가입 신청 거절 사유"
            ),
        ),
    ]