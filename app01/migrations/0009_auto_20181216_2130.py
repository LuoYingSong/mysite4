# Generated by Django 2.1.2 on 2018-12-16 13:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0008_user_info_login_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_info',
            name='unread_msg',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='user_info',
            name='login_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 16, 21, 30, 20, 864147)),
        ),
    ]
