# Generated by Django 5.1.1 on 2024-10-30 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0020_codigoqr_gestorcupon_codigoqr'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gestorcupon',
            name='codigoQR',
        ),
        migrations.AddField(
            model_name='gestorcupon',
            name='url_qr',
            field=models.URLField(blank=True, max_length=300, null=True),
        ),
        migrations.DeleteModel(
            name='CodigoQR',
        ),
    ]