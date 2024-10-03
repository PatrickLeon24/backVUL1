from django.db import models
# Create your models here.

# Tipo de Usuario
class Tipo_Usuario(models.Model):
    tipo = models.CharField(max_length=15)

# Usuario
class Usuario(models.Model):
    nombre = models.CharField(max_length=30, null=True)
    apellido = models.CharField(max_length=30, null=True)
    direccion = models.CharField(max_length=100, null=True)
    numero_contacto = models.CharField(max_length=15, null=True)
    DNI = models.CharField(max_length=10, null=True)
    genero = models.CharField(max_length=10, null=True)
    email = models.CharField(max_length=30, null=True)
    contrasena = models.CharField(max_length=30, null=True)
    cantidad_residuos_acumulados = models.IntegerField(default=0)
    puntaje_acumulado = models.IntegerField(default=0)
    tipousuario = models.ForeignKey(Tipo_Usuario, on_delete=models.CASCADE, null=True)

    def verificar_informacion(self):
        if len(self.DNI) != 8 or not self.DNI.isdigit():
            raise ValueError("El DNI debe tener 8 caracteres numéricos.")
        if not self.numero_contacto.isdigit() or len(self.numero_contacto) < 9:
            raise ValueError("El número de contacto debe tener al menos 9 dígitos y ser numérico.")
        print("Validación de información del cliente exitosa")  # Debugging
        return True

    def modificar_informacion(self, cliente_data):
        # Lógica para modificar la información del cliente
        for field, value in cliente_data.items():
            setattr(self.cliente, field, value)
        self.save()

    def cambiar_contrasena(self, nueva_contrasena):
        # Lógica para cambiar la contraseña
        self.set_contrasena(nueva_contrasena)
        self.save()

    def set_contrasena(self, contrasena):
        self.contrasena = contrasena

    def verificar_contrasena(self, contrasena):
        print("Contraseña ingresada:", contrasena)  # Debug
        print("Contraseña almacenada:", self.contrasena)  # Debug
        return contrasena == self.contrasena  # Comparar directamente

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
   
# Cupon
class Cupon(models.Model):
    costo_puntos = models.IntegerField()
    local = models.CharField(max_length=30)
    descripcion = models.TextField()
    descuento = models.FloatField()
    imagen = models.CharField(max_length=150)

    def ver_informacion_cupon(self):
        pass

# Trayectoria
class Trayectoria(models.Model):
    estado = models.CharField(max_length=50)
    fecha_fin = models.DateField(null=True, blank=True)

class Pago(models.Model):
    estado = models.CharField(max_length=30)
    metodo_pago = models.CharField(max_length=15)
    fecha_pago = models.DateField()


# Plan de Recojo
class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.FloatField()
    aserrin = models.IntegerField(default=0)
    baldes = models.IntegerField(default=0)
    duracion = models.IntegerField(default=0)
    frecuencia_recojo = models.IntegerField()
    cantidad_compostaje = models.FloatField()
    puntos_plan = models.IntegerField(default=0)

    def ver_informacion_plan(self):
        pass

# Gestor de Plan
class GestorPlan(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)

# Recojo
class Recojo(models.Model):
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)
    trayectoria = models.ForeignKey(Trayectoria, on_delete=models.CASCADE, null=True)

    def ver_informacion_servicio(self):
        pass



