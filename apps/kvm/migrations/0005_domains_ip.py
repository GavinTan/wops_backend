# Generated by Django 3.1.7 on 2021-08-17 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kvm', '0004_auto_20210803_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='domains',
            name='ip',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='IP'),
        ),
    ]
