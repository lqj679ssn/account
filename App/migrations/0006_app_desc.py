# Generated by Django 2.0 on 2018-04-06 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0005_auto_20180326_0530'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='desc',
            field=models.CharField(default=None, max_length=32),
        ),
    ]