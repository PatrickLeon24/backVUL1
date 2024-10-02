from django.db import models
from django.contrib.auth.hashers import make_password, check_password
# Create your models here.


from django.db import models

class Persona(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)

    class Meta:
        abstract = True  # Esta clase no creará una tabla en la base de datos.

# Cliente
class Cliente(Persona):
    direccion = models.CharField(max_length=100)
    numero_contacto = models.CharField(max_length=15)
    DNI = models.CharField(max_length=10)
    genero = models.CharField(max_length=10)

    def verificar_informacion(self):
        if len(self.DNI) != 8 or not self.DNI.isdigit():
            raise ValueError("El DNI debe tener 8 caracteres numéricos.")
        if not self.numero_contacto.isdigit() or len(self.numero_contacto) < 9:
            raise ValueError("El número de contacto debe tener al menos 9 dígitos y ser numérico.")
        # Puedes agregar más validaciones aquí según los requisitos de tu aplicación.
        print("Validación de información del cliente exitosa")  # Debugging
        return True

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

class Administrador(Persona):
    # Puedes agregar atributos específicos del administrador si es necesario
    def verificar_informacion(self):
        # Lógica para verificar la información del administrador
        pass


# Usuario (hereda de Cliente)
class Usuario(models.Model):
    puntaje_acumulado = models.IntegerField(default=0)
    cantidad_residuos_acumulados = models.IntegerField(default=0)
    email = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)

    def registrar_cuenta(self, email, contrasena, cliente_data):
        # Verificar si el email ya existe
        if Usuario.objects.filter(email=email).exists():
            raise ValueError("El correo electrónico ya está registrado.")
        
        # Crear cliente
        cliente = Cliente.objects.create(**cliente_data)

        # Crear usuario con contraseña encriptada
        usuario = Usuario.objects.create(
            email=email,
            contrasena=contrasena,
            cliente=cliente,
            puntaje_acumulado=0,  # Valor inicial
            cantidad_residuos_acumulados=0  # Valor inicial
        )
        return usuario

    def modificar_informacion(self, cliente_data):
        # Lógica para modificar la información del cliente
        for field, value in cliente_data.items():
            setattr(self.cliente, field, value)
        self.cliente.save()

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

    def iniciar_sesion(self, email, contrasena):
        # Lógica para iniciar sesión
        user = Usuario.objects.filter(email=email).first()
        if user and user.verificar_contrasena(contrasena):
            return user
        return None
    
# Plan de Recojo
class PlanRecojo(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.FloatField()
    aserrin = models.IntegerField(default=0)
    baldes = models.IntegerField(default=0)
    duracion = models.IntegerField(default=0)
    frecuencia_recojo = models.IntegerField()
    cantidad_compostaje = models.FloatField()
    puntos_plan = models.IntegerField()

    def ver_informacion_plan(self):
        pass
    
# Plan Gestor Plan
class GestorPlan(models.Model):
    plan = models.ForeignKey(PlanRecojo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def seleccionar_plan(self):
        pass
# Cupon
class Cupon(models.Model):
    costo_puntos = models.IntegerField()
    local = models.CharField(max_length=30)
    descripcion = models.TextField()
    descuento = models.FloatField()
    imagen = models.CharField(max_length=150)

    def ver_informacion_cupon(self):
        # Lógica para mostrar información del cupón
        pass


class GestorCupon(models.Model):
    cupon = models.ForeignKey(Cupon,on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)

    def canjear_cupon(self):
        # Lógica para canjear el cupón
        pass

    def ver_qr(self):
        # Lógica para mostrar el código QR del cupón
        pass

# Estado de Servicio
class EstadoServicio(models.Model):
    estado = models.CharField(max_length=50)

    def actualizar_estado(self):
        # Lógica para actualizar el estado del servicio
        pass

class Pago(models.Model):
    estado = models.CharField(max_length=30)
    metodo_pago = models.CharField(max_length=15)
    fecha_pago = models.DateField()

# ServicioCompostaje
class ServicioCompostaje(models.Model):
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    plan = models.ForeignKey(PlanRecojo, on_delete=models.CASCADE, null=True)
    estado = models.ForeignKey(EstadoServicio, on_delete=models.CASCADE)
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, null=True)

    def ver_informacion_servicio(self):
        # Lógica para mostrar la información del servicio
        pass



