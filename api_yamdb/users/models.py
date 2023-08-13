from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    EMAIL_MAX_LEN: int = 254
    ROLE_MAX_LEN: int = 30
    USERNAME_MAX_LEN: int = 150
    CONF_CODE_MAX_LEN: int = 150
    PASS_MAX_LEN: int = 250

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    ROLE = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор')
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_MAX_LEN,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]',
                           message='Недопустимые символы в имени пользователя')
        ]
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=EMAIL_MAX_LEN,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=USERNAME_MAX_LEN,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=USERNAME_MAX_LEN,
        blank=True
    )
    bio = models.TextField(
        'Об авторе',
        blank=True
    )
    role = models.TextField(
        'Роль',
        choices=ROLE,
        default=USER
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=CONF_CODE_MAX_LEN,
        blank=True,
        null=True
    )
    password = models.CharField(
        'Пароль',
        max_length=PASS_MAX_LEN,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == User.ROLE[2][0]

    @property
    def is_moderator(self):
        return self.role == User.ROLE[1][0]

    def __str__(self):
        return self.username
