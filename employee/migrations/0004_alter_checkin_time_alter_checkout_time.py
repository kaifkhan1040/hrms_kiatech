# Generated by Django 5.1.7 on 2025-03-17 06:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0003_alter_checkin_time_alter_checkout_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkin',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 17, 6, 14, 59, 806580, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='checkout',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 17, 6, 14, 59, 839582, tzinfo=datetime.timezone.utc)),
        ),
    ]
