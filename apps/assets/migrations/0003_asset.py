# Generated by Django 3.1.7 on 2021-08-04 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0002_auto_20210804_1600'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='名称')),
                ('ip', models.CharField(blank=True, db_index=True, max_length=120, null=True, verbose_name='IP')),
                ('description', models.TextField(verbose_name='描述')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '资产',
            },
        ),
    ]
