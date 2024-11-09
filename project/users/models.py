from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nickname = models.CharField(max_length=8, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,  # 이렇게 하면 마이그레이션 시 기본값 지정 문제가 해결됩니다
        blank=True
    )

    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.nickname
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nickname

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
