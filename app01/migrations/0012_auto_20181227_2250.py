# Generated by Django 2.1.3 on 2018-12-27 14:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0011_auto_20181223_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_info',
            name='login_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 27, 22, 50, 35, 402840)),
        ),
    ]
