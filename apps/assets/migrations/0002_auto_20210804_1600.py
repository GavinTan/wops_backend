# Generated by Django 3.1.7 on 2021-08-04 08:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='treenodes',
            options={'verbose_name': '资产树节点'},
        ),
        migrations.RenameField(
            model_name='treenodes',
            old_name='name',
            new_name='title',
        ),
    ]
