# Generated by Django 3.1.7 on 2021-08-10 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0009_asset_tree_node'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asset',
            old_name='description',
            new_name='desc',
        ),
    ]