# Generated by Django 4.2.3 on 2023-07-14 10:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_resignation_resigned_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="authorization_grade",
            field=models.CharField(
                choices=[("MS", "마스터"), ("MA", "관리자"), ("ST", "일반")],
                max_length=2,
                null=True,
                verbose_name="등급",
            ),
        ),
    ]
