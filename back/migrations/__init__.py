from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[(
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30)),
                ('apellido', models.CharField(max_length=30)),
                ('direccion', models.CharField(max_length=100)),
                ('numero_contacto', models.CharField(max_length=15))
            )]
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[(
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntaje_acumulado', models.IntegerField()),
                ('cantidad_residuos_acumulados', models.IntegerField()),
                ('email', models.CharField(max_length=30)),
                ('contrasena', models.CharField(max_length=30)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.cliente'))
            )]
        ),
        migrations.CreateModel(
            name='EstadoServicio',
            fields=[(
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(max_length=30))
            )]
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[(
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.CharField(max_length=150)),
                ('nombre', models.CharField(max_length=30)),
                ('descripcion', models.CharField(max_length=60)),
                ('precio', models.FloatField()),
                ('frecuencia_recojo', models.IntegerField()),
                ('cantidad_compostaje', models.FloatField()),
                ('materiales', models.CharField(max_length=30))
            )]
        ),
        migrations.CreateModel(
            name='ServicioCompostaje',
            fields=[(
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_ingreso', models.DateField()),
                ('fecha_salida', models.DateField(null=True, blank=True))
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.estadoservicio')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.usuario')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.plan'))
            )]
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[(
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(max_length=30)),
                ('metodoPago', models.CharField(max_length=30)),
                ('fechaPago', models.DateField()),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.servicio'))
            )]
        ),
        migrations.CreateModel(
            name='Puntos',
            fields=[(
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_de_puntos' , models.IntegerField()),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.plan'))
            )]
        ),
        migrations.CreateModel(
            name='Cupon',
            fields=[(
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.CharField(max_length=150)),
                ('costo_puntos', models.IntegerField()),
                ('descripcion', models.CharField(max_length=60)),
                ('descuento', models.FloatField()),
                ('puntos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.puntos'))
            )]
        )

    ]