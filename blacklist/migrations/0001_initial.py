# Generated by Django 3.2.1 on 2021-12-05 00:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Netblock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_addr', models.CharField(max_length=15, verbose_name='IP Address')),
                ('cidr', models.PositiveSmallIntegerField(choices=[(32, '/32'), (31, '/31'), (30, '/30'), (29, '/29'), (28, '/28'), (27, '/27'), (26, '/26'), (25, '/25'), (24, '/24'), (23, '/23'), (22, '/22'), (21, '/21'), (20, '/20'), (19, '/19'), (18, '/18'), (16, '/16'), (8, '/8')], default=32, help_text='Choose cidr')),
                ('label', models.CharField(blank=True, max_length=20, verbose_name='label')),
                ('split', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('total_listed_ip', models.PositiveIntegerField(default=0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['cidr'],
            },
        ),
        migrations.CreateModel(
            name='Iptable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_addr', models.CharField(max_length=15, verbose_name='IP Address')),
                ('listed', models.BooleanField(default=False)),
                ('listed_by', models.CharField(blank=True, max_length=1000)),
                ('check_datetime', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blacklist.netblock')),
            ],
        ),
        migrations.CreateModel(
            name='IPhistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_addr', models.CharField(max_length=15, verbose_name='IP Address')),
                ('listed', models.BooleanField(default=False)),
                ('listed_by', models.CharField(blank=True, max_length=1000)),
                ('check_datetime', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blacklist.netblock')),
            ],
            options={
                'ordering': ['-check_datetime'],
            },
        ),
        migrations.AddIndex(
            model_name='iptable',
            index=models.Index(fields=['ip_addr', 'check_datetime'], name='blacklist_i_ip_addr_ad774d_idx'),
        ),
        migrations.AddConstraint(
            model_name='iptable',
            constraint=models.UniqueConstraint(fields=('parent', 'ip_addr'), name='unique_parent_ip'),
        ),
        migrations.AddIndex(
            model_name='iphistory',
            index=models.Index(fields=['ip_addr', 'check_datetime'], name='blacklist_i_ip_addr_4bec45_idx'),
        ),
    ]