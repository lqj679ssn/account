# Generated by Django 2.2.5 on 2019-10-08 13:45

import SmartDjango.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Config', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='config',
            options={'default_manager_name': 'objects'},
        ),
        migrations.AlterField(
            model_name='config',
            name='key',
            field=SmartDjango.models.fields.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='config',
            name='value',
            field=SmartDjango.models.fields.CharField(max_length=255),
        ),
    ]
