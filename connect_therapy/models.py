from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1)
    mobile = models.CharField(max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
