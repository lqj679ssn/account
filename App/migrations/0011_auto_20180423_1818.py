# Generated by Django 2.0 on 2018-04-23 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0010_auto_20180423_0432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userapp',
            name='last_auth_code_time',
            field=models.CharField(default=None, max_length=20, verbose_name='上一次申请auth_code的时间，防止被多次使用'),
        ),
    ]
