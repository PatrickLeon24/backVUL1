# Generated by Django 5.1.1 on 2024-11-16 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0034_alter_notificacion_fecha_creacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
