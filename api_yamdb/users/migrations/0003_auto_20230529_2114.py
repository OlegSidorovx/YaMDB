# Generated by Django 3.2 on 2023-05-29 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230525_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='confirmation_code',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Код подтверждения'),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Пароль'),
        ),
    ]
