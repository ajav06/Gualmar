from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True, verbose_name = "Fecha de Nacimiento")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name = "Número Telefonico")
    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ['-date_joined']

    def __str__(self):
        return self.username
    

class Address(models.Model):
    user = models.ForeignKey(User, verbose_name = "Usuario", on_delete=models.CASCADE)
    country = models.CharField(max_length=100, blank=True, verbose_name = "País")
    location = models.CharField(max_length=50, blank=True, verbose_name = "Estado")
    city = models.CharField(max_length=50, blank=True, verbose_name="Ciudad")
    address = models.TextField(max_length=500, blank=True, null=True, verbose_name = "Dirección")

    class Meta:
        verbose_name = "dirección"
        verbose_name_plural = "direcciones"

    def __str__(self):
        return self.user.username
    