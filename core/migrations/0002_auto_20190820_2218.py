# Generated by Django 2.2.4 on 2019-08-21 02:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='username',
            new_name='user_name',
        ),
    ]
