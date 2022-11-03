# Generated by Django 3.1.7 on 2021-10-07 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kvm', '0016_auto_20210930_1816'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vminstance',
            name='current_memory',
        ),
        migrations.AddField(
            model_name='vminstance',
            name='max_vcpu',
            field=models.IntegerField(blank=True, null=True, verbose_name='最大vCPU'),
        ),
        migrations.AddField(
            model_name='vminstance',
            name='memory',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='内存'),
        ),
        migrations.AlterField(
            model_name='vminstance',
            name='vcpu',
            field=models.IntegerField(blank=True, null=True, verbose_name='当前vCPU'),
        ),
    ]
