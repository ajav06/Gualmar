# Generated by Django 2.2.4 on 2019-08-21 04:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20190820_2336'),
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_session', models.CharField(max_length=50, verbose_name='Id de la Sesión')),
                ('phrase', models.CharField(max_length=50, verbose_name='Frase de Búsqueda')),
                ('time', models.FloatField(max_length=10, verbose_name='Tiempo de Búsqueda')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'búsqueda de artículo',
                'verbose_name_plural': 'búsqueda de artículos',
            },
        ),
    ]
