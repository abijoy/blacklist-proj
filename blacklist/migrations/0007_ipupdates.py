# Generated by Django 3.2.1 on 2021-12-07 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blacklist', '0006_delete_ipupdates'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpUpdates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_addr', models.CharField(max_length=15, verbose_name='IP Address')),
                ('listed', models.BooleanField(default=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('iphistory', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='blacklist.iphistory')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blacklist.netblock')),
            ],
        ),
    ]
