# Generated by Django 5.1.1 on 2024-11-13 03:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0028_alter_token_tipo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='tipo',
        ),
    ]
