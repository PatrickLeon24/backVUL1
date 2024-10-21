from django.db import models
# Create your models here.

# Tipo de Usuario
class Tipo_Usuario(models.Model):
    tipo = models.CharField(max_length=15)

    def __str__(self):
        return self.tipo
# Usuario
class Usuario(models.Model):
    nombre = models.CharField(max_length=30, null=True)
    apellido = models.CharField(max_length=30, null=True)
    direccion = models.CharField(max_length=100, null=True)
    numero_contacto = models.CharField(max_length=15, null=True)
    DNI = models.CharField(max_length=10, null=True)
    genero = models.CharField(max_length=10, null=True)
    email = models.EmailField(max_length=50, null=True)
    contrasena = models.CharField(max_length=30, null=True)
    cantidad_residuos_acumulados = models.IntegerField(default=0)
    puntaje_acumulado = models.IntegerField(default=0)
    tipousuario = models.ForeignKey(Tipo_Usuario, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
   
# Cupon
class Cupon(models.Model):
    costo_puntos = models.IntegerField()
    local = models.CharField(max_length=30)
    descripcion = models.TextField()
    descuento = models.FloatField()
    imagen = models.URLField(max_length=200)

    def __str__(self):
        return f'Cupón de {self.local} - {self.costo_puntos} puntos'
    
# Trayectoria
class Trayectoria(models.Model):
    estado = models.CharField(max_length=2)

    def __str__(self):
        return self.estado
    
class Pago(models.Model):
    estado = models.CharField(max_length=30)
    metodo_pago = models.CharField(max_length=15)
    fecha_pago = models.DateField()

    def __str__(self):
        return f'{self.metodo_pago} - {self.estado}'
    
# Plan de Recojo
class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.URLField(max_length=200)
    descripcion = models.TextField()
    precio = models.FloatField()
    aserrin = models.IntegerField(default=0)
    baldes = models.IntegerField(default=0)
    duracion = models.IntegerField(default=0)
    frecuencia_recojo = models.IntegerField()
    cantidad_compostaje = models.FloatField()
    puntos_plan = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre
    
# Gestor de Plan
class GestorPlan(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
    recojos_solicitados = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.usuario} - {self.plan}'
    
# Recojo
class Recojo(models.Model):
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    gestor_plan = models.ForeignKey(GestorPlan, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f'Recojo {self.gestor_plan} - {self.fecha_ingreso}'

class Recojo_trayectoria(models.Model):
    estado_ingreso = models.DateTimeField()
    recojo = models.ForeignKey(Recojo, on_delete=models.CASCADE, null=True)
    trayectoria = models.ForeignKey(Trayectoria, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.recojo}'

class CodigoInvitacion(models.Model):
    codigo = models.CharField(max_length=10, unique=True)  # Código único
    utilizado = models.BooleanField(default=False)  # Estado del código
    creado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Quién generó el código
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación

    def __str__(self):
        return self.codigo