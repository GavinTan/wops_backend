# Generated by Django 3.1.7 on 2021-09-07 06:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0015_asset_proxy'),
        ('kvm', '0011_auto_20210819_1749'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Domains',
            new_name='VmInstance',
        ),
        migrations.RenameModel(
            old_name='Nodes',
            new_name='VmServer',
        ),
    ]
