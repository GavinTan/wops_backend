# Generated by Django 3.1.7 on 2021-08-10 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0006_treenodes_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treenodes',
            name='key',
            field=models.CharField(max_length=60, verbose_name='Key'),
        ),
        migrations.AlterField(
            model_name='treenodes',
            name='parent',
            field=models.CharField(max_length=60, verbose_name='父级ID'),
        ),
        migrations.AlterField(
            model_name='treenodes',
            name='title',
            field=models.CharField(db_index=True, max_length=120, verbose_name='名称'),
        ),
    ]
