# Generated by Django 5.1.1 on 2024-10-08 16:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0009_alter_cupon_imagen_alter_plan_imagen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recojo',
            name='plan',
        ),
        migrations.AddField(
            model_name='recojo',
            name='gestor_plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='back.gestorplan'),
        ),
    ]
