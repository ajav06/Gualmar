from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

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


class CategoryArticle(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=100)
    created = models.DateTimeField(verbose_name='Fecha de Creación', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Fecha de Edición', auto_now=True)

    class Meta:
        verbose_name = 'categoría de artículo'
        verbose_name_plural = 'categorías de artículos'
        ordering = ['-created']

    def __str__(self):
        return self.name

class Article(models.Model):
    code = models.CharField(max_length=10, primary_key=True, verbose_name="Código")
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    price = models.FloatField(verbose_name="Precio", max_length=30)
    categories = models.ManyToManyField(CategoryArticle, verbose_name='Categorías', related_name='get_posts')
    created = models.DateTimeField(verbose_name='Fecha de Creación', auto_now_add=True)
    status = models.BooleanField(verbose_name="Estado", default=True)

    class Meta:
        verbose_name = 'artículo'
        verbose_name_plural = 'artículos'
        ordering = ['-created']

    def __str__(self):
        return self.name


class Search(models.Model):
    id_session = models.CharField(max_length=50, verbose_name="Id de la Sesión")
    user = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)
    phrase = models.CharField(max_length=50, verbose_name="Frase de Búsqueda")
    time = models.FloatField(max_length=10, verbose_name="Tiempo de Búsqueda")

    class Meta:
        verbose_name = 'búsqueda de artículo'
        verbose_name_plural = 'búsqueda de artículos'

    def __str__(self):
        return self.phrase

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'carrito de compra'
        verbose_name_plural = 'carritos de compra'


class PaymentDetails(models.Model):
    user = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)
    TYPE_STATUTUS = (
        ('e', 'Exitosa'),
        ('f', 'Fallida'),
        ('i', 'Inactiva')
    )
    status = models.CharField(max_length=1, choices=TYPE_STATUTUS)

    class Meta:
        verbose_name = 'detalles de pago'
        verbose_name_plural = 'detalles de pagos'

class Bill(models.Model):
    user = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)
    amount = models.FloatField(max_length=30, verbose_name="Monto Total de la Compra")
    payment = models.ForeignKey(PaymentDetails, verbose_name="Detalles del Pago", on_delete=models.CASCADE)
    address = models.ForeignKey(Address, verbose_name="Dirección de Envio", on_delete=None)
    date = models.DateField(verbose_name="Fecha de Facturación", auto_now_add=True)
    TYPE_STATUTUS = (
        ('a', 'Activa'),
        ('d','Devuelta'),
        ('i', 'Inactiva')
    )
    status = models.CharField(max_length=1, choices=TYPE_STATUTUS, verbose_name="Estado de la Factura")

    class Meta:
        verbose_name = 'factura'
        verbose_name_plural = 'facturas'


class BillDetails(models.Model):
    bill = models.ForeignKey(Bill, verbose_name="Id de la Factura", on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name="Artículo", on_delete=None)
    quantity = models.FloatField(max_length=4, verbose_name="Cantidad del Artículo")
    amount = models.FloatField(max_length=30, verbose_name="Monto por Cantidad de Artículo")

    class Meta:
        verbose_name = 'detalle de factura'
        verbose_name_plural = 'detalles de facturas'
