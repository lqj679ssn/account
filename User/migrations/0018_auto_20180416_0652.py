# Generated by Django 2.0 on 2018-04-16 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0017_auto_20180323_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='description',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
    ]