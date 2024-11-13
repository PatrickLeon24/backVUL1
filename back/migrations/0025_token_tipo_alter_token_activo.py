# Generated by Django 5.1.1 on 2024-11-13 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0024_gestorplan_validado'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='tipo',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='token',
            name='activo',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
