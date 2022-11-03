# Generated by Django 3.1.7 on 2021-08-11 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0010_auto_20210810_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(blank=True, db_index=True, max_length=120, null=True, verbose_name='IP')),
                ('account', models.JSONField(verbose_name='账号')),
                ('desc', models.TextField(verbose_name='描述')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '代理',
            },
        ),
        migrations.CreateModel(
            name='ProxyPlatform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(blank=True, db_index=True, max_length=120, null=True, verbose_name='IP')),
                ('account', models.JSONField(verbose_name='账号')),
                ('address', models.URLField(verbose_name='平台地址')),
                ('desc', models.TextField(verbose_name='描述')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '代理平台',
            },
        ),
    ]
