# Generated by Django 5.1.1 on 2024-11-14 04:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0032_alter_notificacion_fecha_creacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='fecha_creacion',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 14, 4, 50, 31, 541912, tzinfo=datetime.timezone.utc)),
        ),
    ]
