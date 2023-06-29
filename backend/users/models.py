from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_NAME_LENGTH: int = 150
MAX_EMAIL_LENGTH: int = 254


class User(AbstractUser):
    username = models.CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        blank=False,
        null=False,
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=True
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} follow {self.author}'
