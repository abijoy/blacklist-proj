# Generated by Django 3.2.1 on 2021-12-09 18:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blacklist', '0008_testmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='iptable',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 12, 6, 18, 0, 2, 853886)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ipupdates',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 12, 6, 18, 0, 50, 458991)),
            preserve_default=False,
        ),
    ]