# Generated by Django 2.2.4 on 2019-08-23 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_shoppingcart_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='preferences',
            field=models.ManyToManyField(related_name='preferencia', to='core.CategoryArticle', verbose_name='Preferencias'),
        ),
    ]