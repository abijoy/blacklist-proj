# Generated by Django 3.2.1 on 2021-12-07 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blacklist', '0005_rename_parent_id_ipupdates_parent'),
    ]

    operations = [
        migrations.DeleteModel(
            name='IpUpdates',
        ),
    ]
