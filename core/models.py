from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.

class CategoryArticle(models.Model):
    """ Modelo de Categoria por Artículo """
    name = models.CharField(verbose_name='Nombre', max_length=100)
    created = models.DateTimeField(verbose_name='Fecha de Creación', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Fecha de Edición', auto_now=True)

    class Meta:
        verbose_name = 'categoría de artículo'
        verbose_name_plural = 'categorías de artículos'
        ordering = ['-created']

    def __str__(self):
        return '{}'.format(self.id)


class User(AbstractUser):
    """ Modelo Extendido del Usuario """
    birth_date = models.DateField(null=True, blank=True, verbose_name = "Fecha de Nacimiento")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name = "Número Telefonico")
    preferences = models.ManyToManyField(CategoryArticle, verbose_name='Preferencias', related_name='preferencia')
    last_access = models.DateTimeField(default=datetime.now())
    image = models.ImageField(verbose_name='Foto', upload_to='foto', null=True, blank=True, default='foto/default.jpg')

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ['-date_joined']

    def __str__(self):
        return self.username    

class Address(models.Model):
    """ Modelo de Dirección por Usuario """
    user = models.ForeignKey(User, verbose_name = "Usuario", on_delete=models.CASCADE)
    country = models.CharField(max_length=100, blank=True, verbose_name = "País")
    location = models.CharField(max_length=50, blank=True, verbose_name = "Estado")
    city = models.CharField(max_length=50, blank=True, verbose_name="Ciudad")
    address = models.TextField(max_length=500, blank=True, null=True, verbose_name = "Dirección")

    class Meta:
        verbose_name = "dirección"
        verbose_name_plural = "direcciones"

    def __str__(self):
        return self.address

class Article(models.Model):
    """ Modelo de Artículo """
    code = models.CharField(max_length=10, primary_key=True, verbose_name="Código")
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    price = models.FloatField(verbose_name="Precio", max_length=30)
    categories = models.ManyToManyField(CategoryArticle, verbose_name='Categorías', related_name='get_posts')
    created = models.DateTimeField(verbose_name='Fecha de Creación', auto_now_add=True)
    status = models.BooleanField(verbose_name="Estado", default=True)
    image = models.ImageField(verbose_name='Imagen', upload_to='article', null=True, blank=True)

    class Meta:
        verbose_name = 'artículo'
        verbose_name_plural = 'artículos'
        ordering = ['code']

    def __str__(self):
        return self.name

class Search(models.Model):
    """ Modelo de Busqueda de Artículos o Categorias por Usuario """
    id_session = models.CharField(max_length=50, verbose_name="Id de la Sesión", blank=True, null=True)
    user = models.ForeignKey(User, verbose_name="Usuario",on_delete=models.CASCADE, blank=True, null=True)
    phrase = models.CharField(max_length=50, verbose_name="Frase de Búsqueda", blank=True, null=True)
    category = models.ForeignKey(CategoryArticle, verbose_name="Categoria de Búsqueda", on_delete=models.CASCADE, blank=True, null=True)
    time = models.DateField(verbose_name="Fecha de Búsqueda", blank=True, null=True, auto_now=True)

    class Meta:
        verbose_name = 'búsqueda de artículo'
        verbose_name_plural = 'búsqueda de artículos'

class ShoppingCart(models.Model):
    """ Modelo del Carrito de Compra por Usuario """
    user = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name="Artículo a Comprar", on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Cantidad del Artículo")
    amount = models.FloatField(max_length=30, verbose_name="Monto por Cantidad de Artículo")
    sponsored = models.BooleanField(verbose_name="Compra patrocinada", default=False)
    TYPE_STATUS = (
        ('a', 'Activo'),
        ('c', 'Comprado'),
        ('e', 'Eliminado')
    )
    status = models.CharField(max_length=1, choices=TYPE_STATUS, verbose_name="Estado del ítem en carrito")

    class Meta:
        verbose_name = 'carrito de compra'
        verbose_name_plural = 'carritos de compra'

    def __str__(self):
        return "{}".format(self.id)

class PaymentDetails(models.Model):
    """ Modelo de Detalles de Pago realizados por el Usuario """
    user = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)
    PAYMENT_TYPE = (
        ('tc', 'Tarjeta de Crédito'),
        ('pp', 'Paypal')
    )
    payment_type = models.CharField(max_length=2, choices=PAYMENT_TYPE, verbose_name="Tipo de Pago")
    transaction_code = models.CharField(max_length=20, verbose_name="Código de la Transacción")
    TYPE_STATUS = (
        ('e', 'Exitosa'),
        ('f', 'Fallida')
    )
    status = models.CharField(max_length=1, choices=TYPE_STATUS, verbose_name="Estado de la Transacción")

    class Meta:
        verbose_name = 'detalles de pago'
        verbose_name_plural = 'detalles de pagos'

    def __str__(self):
        return self.transaction_code

class Bill(models.Model):
    """ Modelo de la Factura de compra realizada por Usuario """
    user = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)
    amount = models.FloatField(max_length=30, verbose_name="Monto Total de la Compra")
    payment = models.ForeignKey(PaymentDetails, verbose_name="Detalles del Pago", on_delete=models.CASCADE)
    address = models.ForeignKey(Address, verbose_name="Dirección de Envio", on_delete=None)
    date = models.DateField(verbose_name="Fecha de Facturación", auto_now_add=True)
    TYPE_STATUS = (
        ('a', 'Activa'),
        ('d','Devuelta'),
        ('i', 'Inactiva')
    )
    status = models.CharField(max_length=1, choices=TYPE_STATUS, verbose_name="Estado de la Factura")

    class Meta:
        verbose_name = 'factura'
        verbose_name_plural = 'facturas'

    def __str__(self):
        return "{}".format(self.id)


class BillDetails(models.Model):
    """ Modelo de Detalle Factura de compra """
    bill = models.ForeignKey(Bill, verbose_name="Id de la Factura", on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name="Artículo Comprado", on_delete=None)
    quantity = models.IntegerField(verbose_name="Cantidad del Artículo")
    amount = models.FloatField(max_length=30, verbose_name="Monto por Cantidad de Artículo")
    sponsored = models.BooleanField(verbose_name="Compra patrocinada", default=False)

    class Meta:
        verbose_name = 'detalle de factura'
        verbose_name_plural = 'detalles de facturas'

    def __str__(self):
        return "{}".format(self.id)

class ArticleClick(models.Model):
    article = models.ForeignKey(Article, verbose_name="Id del Artículo", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)
    date = models.DateField(verbose_name="Fecha del click", auto_now_add=True)

    class Meta:
        verbose_name = 'click a artículo'
        verbose_name_plural = 'clicks a artículos'
    
    def __str__(self):
        return "{}".format(self.id)