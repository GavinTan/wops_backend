# Generated by Django 3.1 on 2020-08-17 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kvm', '0005_auto_20200814_1826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kvmdomains',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
