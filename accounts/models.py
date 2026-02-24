from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    display_name = models.CharField('表示名', max_length=50, blank=True)

    def __str__(self):
        return self.display_name or self.username
