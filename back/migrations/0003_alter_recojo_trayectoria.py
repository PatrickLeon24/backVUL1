# Generated by Django 5.1.1 on 2024-10-03 04:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0002_remove_plan_pago_usuario_tipousuario_gestorplan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recojo',
            name='trayectoria',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='back.trayectoria'),
        ),
    ]
