# Generated by Django 3.2.13 on 2022-10-09 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('valdata', '0010_rename_modelinfo_inferencepath'),
    ]

    operations = [
        migrations.AlterField(
            model_name='state',
            name='progress',
            field=models.IntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='state',
            name='threshold',
            field=models.FloatField(default=85),
        ),
    ]