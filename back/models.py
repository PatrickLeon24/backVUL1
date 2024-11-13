from django.db import models
from django.utils import timezone
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
    disponibilidad = models.IntegerField(default=0)

    def __str__(self):
        return f'Cupon de {self.local} - {self.costo_puntos} puntos'

# Gestor Cupon
class GestorCupon(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    cupon = models.ForeignKey(Cupon, on_delete=models.CASCADE, null=True)
    url_qr = models.URLField(max_length=300, null=True, blank=True)
    fecha_canje = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.usuario} - {self.cupon}'
    
# Trayectoria
class Trayectoria(models.Model):
    estado = models.CharField(max_length=2)

    def __str__(self):
        return self.estado

# Pago    
class Pago(models.Model):
    estado = models.CharField(max_length=30)
    metodo_pago = models.CharField(max_length=15)
    fecha_pago = models.DateField()
    monto_pago = models.FloatField(default=0)

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
    validado = models.BooleanField(default=False)

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

# Recojo_trayectoria
class Recojo_trayectoria(models.Model):
    estado_ingreso = models.DateTimeField()
    recojo = models.ForeignKey(Recojo, on_delete=models.CASCADE, null=True)
    trayectoria = models.ForeignKey(Trayectoria, on_delete=models.CASCADE, null=True)
    administrador = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.recojo}'

# CodigoInvitacion
class CodigoInvitacion(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    utilizado = models.BooleanField(default=False) 
    creado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo
    
# Token
class Token(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    
    token = models.CharField(max_length=10, unique=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    activo = models.BooleanField(default=False)

    def __str__(self):
        return f'Token de {self.usuario} - {self.token}'
    
class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="notificaciones")
    administrador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name="notificaciones_enviadas")
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.usuario.email} - Leído: {self.leido}"