# Generated by Django 5.1.7 on 2025-03-21 09:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0005_alter_checkin_time_alter_checkout_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkin',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 21, 9, 27, 6, 152464, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='checkout',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 21, 9, 27, 6, 183713, tzinfo=datetime.timezone.utc)),
        ),
    ]
