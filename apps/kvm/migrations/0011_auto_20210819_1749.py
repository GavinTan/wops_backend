# Generated by Django 3.1.7 on 2021-08-19 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kvm', '0010_auto_20210819_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domains',
            name='memory',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='内存'),
        ),
        migrations.AlterField(
            model_name='nodes',
            name='memory',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='内存'),
        ),
    ]
