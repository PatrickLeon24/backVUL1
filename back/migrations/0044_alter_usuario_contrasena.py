# Generated by Django 5.1.1 on 2024-11-21 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0043_alter_usuario_contrasena'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='contrasena',
            field=models.CharField(max_length=30, null=True),
        ),
    ]