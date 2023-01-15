# Generated by Django 3.2.13 on 2023-01-01 14:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('valdata', '0012_alter_inferencepath_acc'),
    ]

    operations = [
        migrations.RenameField(
            model_name='state',
            old_name='target_model',
            new_name='target_det_model',
        ),
        migrations.AddField(
            model_name='state',
            name='target_seg_model',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='bbox',
            name='data',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bbox', to='valdata.data'),
        ),
        migrations.AlterField(
            model_name='margin',
            name='bbox',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='margin', to='valdata.bbox'),
        ),
    ]
