# Generated by Django 5.1.1 on 2024-10-25 03:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0017_codigoinvitacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='cantidad_residuos_acumulados',
        ),
        migrations.AddField(
            model_name='cupon',
            name='disponibilidad',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='recojo_trayectoria',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='back.usuario'),
        ),
        migrations.CreateModel(
            name='GestorCupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cupon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='back.cupon')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='back.usuario')),
            ],
        ),
    ]
