# Generated by Django 3.2.1 on 2021-12-07 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blacklist', '0004_ipupdates'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ipupdates',
            old_name='parent_id',
            new_name='parent',
        ),
    ]
