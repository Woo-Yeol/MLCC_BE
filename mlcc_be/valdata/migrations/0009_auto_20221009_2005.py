# Generated by Django 3.2.13 on 2022-10-09 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('valdata', '0008_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Modelinfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('path', models.CharField(max_length=50)),
                ('acc', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='data',
            name='source_pc',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='state',
            name='progress',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='state',
            name='target_model',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='state',
            name='work',
            field=models.BooleanField(default=False),
        ),
    ]
