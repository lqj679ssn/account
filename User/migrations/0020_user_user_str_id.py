# Generated by Django 2.0 on 2019-03-03 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0019_user_qitian_modify_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_str_id',
            field=models.CharField(blank=True, default=None, max_length=6, null=True, unique=True, verbose_name='唯一随机用户ID，弃用user_id'),
        ),
    ]
