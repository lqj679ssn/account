# Generated by Django 2.2.5 on 2019-10-08 13:45

import SmartDjango.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0028_auto_20190401_1714'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'default_manager_name': 'objects'},
        ),
        migrations.AddField(
            model_name='user',
            name='is_dev',
            field=models.BooleanField(default=False, verbose_name='是否开发者'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=SmartDjango.models.fields.CharField(blank=True, default=None, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='birthday',
            field=SmartDjango.models.fields.DateField(default=None, null=True, verbose_name='生日'),
        ),
        migrations.AlterField(
            model_name='user',
            name='card_image_back',
            field=SmartDjango.models.fields.CharField(default=None, max_length=1024, null=True, verbose_name='身份证背面照'),
        ),
        migrations.AlterField(
            model_name='user',
            name='card_image_front',
            field=SmartDjango.models.fields.CharField(default=None, max_length=1024, null=True, verbose_name='身份证正面照'),
        ),
        migrations.AlterField(
            model_name='user',
            name='description',
            field=SmartDjango.models.fields.CharField(blank=True, default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='idcard',
            field=SmartDjango.models.fields.CharField(choices=[(0, '中国大陆身份证认证'), (1, '其他地区身份认证')], default=None, max_length=18, null=True, verbose_name='身份证号'),
        ),
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=SmartDjango.models.fields.CharField(default=None, max_length=10),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=SmartDjango.models.fields.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=SmartDjango.models.fields.CharField(default=None, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='pwd_change_time',
            field=SmartDjango.models.fields.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='qitian',
            field=SmartDjango.models.fields.CharField(default=None, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='qitian_modify_time',
            field=SmartDjango.models.fields.IntegerField(default=0, help_text='一般只能修改一次', verbose_name='齐天号被修改的次数'),
        ),
        migrations.AlterField(
            model_name='user',
            name='real_name',
            field=SmartDjango.models.fields.CharField(default=None, max_length=32, null=True, verbose_name='真实姓名'),
        ),
        migrations.AlterField(
            model_name='user',
            name='real_verify_type',
            field=SmartDjango.models.fields.SmallIntegerField(default=None, null=True, verbose_name='实名认证类型'),
        ),
        migrations.AlterField(
            model_name='user',
            name='salt',
            field=SmartDjango.models.fields.CharField(default=None, max_length=10),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_str_id',
            field=SmartDjango.models.fields.CharField(blank=True, default=None, max_length=32, null=True, unique=True, verbose_name='唯一随机用户ID'),
        ),
        migrations.AlterField(
            model_name='user',
            name='verify_status',
            field=SmartDjango.models.fields.SmallIntegerField(choices=[(0, '没有认证'), (1, '自动认证阶段'), (2, '人工认证阶段'), (3, '成功认证')], default=0, verbose_name='是否通过实名认证'),
        ),
    ]
