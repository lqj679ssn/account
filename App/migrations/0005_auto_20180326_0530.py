# Generated by Django 2.0 on 2018-03-26 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0004_scope_always'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scope',
            name='name',
            field=models.CharField(max_length=10, unique=True, verbose_name='权限英文简短名称'),
        ),
    ]
