# Generated by Django 3.1.7 on 2021-08-12 09:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0014_proxy_platform'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='proxy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='assets.proxy'),
        ),
    ]
