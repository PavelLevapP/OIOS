from django.db import models


class User(models.Model):
    telegram_id = models.IntegerField(max_length=25, unique=True)
    user_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
