# Generated by Django 5.1.1 on 2024-10-06 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0007_alter_tipo_usuario_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(max_length=50, null=True),
        ),
    ]
