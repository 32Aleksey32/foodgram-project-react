from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField


class User(AbstractUser):
    first_name = CharField(
        'Имя',
        max_length=50,
    )
    last_name = CharField(
        'Фамилия',
        max_length=50
    )
    email = EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
