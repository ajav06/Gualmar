# Generated by Django 2.2.4 on 2019-08-23 19:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20190823_0202'),
    ]

    operations = [
        migrations.AddField(
            model_name='billdetails',
            name='sponsored',
            field=models.BooleanField(default=False, verbose_name='Compra patrocinada'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='sponsored',
            field=models.BooleanField(default=False, verbose_name='Compra patrocinada'),
        ),
        migrations.CreateModel(
            name='ArticleClick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Fecha del click')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Article', verbose_name='Id del Artículo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'click a artículo',
                'verbose_name_plural': 'clicks a artículos',
            },
        ),
    ]
