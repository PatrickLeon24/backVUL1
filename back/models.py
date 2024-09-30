from django.db import models
from django.contrib.auth.hashers import make_password, check_password
# Create your models here.

# Cliente
class Cliente(models.Model):
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
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
            contrasena=make_password(contrasena),
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
        self.contrasena = make_password(contrasena)

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
    
# Estado de Servicio
class EstadoServicio(models.Model):
    estado = models.CharField(max_length=50)

    def actualizar_estado(self):
        # Lógica para actualizar el estado del servicio
        pass

# Plan de Recojo
class PlanRecojo(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.FloatField()
    materiales = models.CharField(max_length=30)  # Array de materiales
    frecuencia_recojo = models.IntegerField()  # Frecuencia en días
    cantidad_compostaje = models.FloatField()
    puntos_plan = models.IntegerField()

    def mostrar_materiales(self):
        # Lógica para mostrar materiales del plan
        pass

    def seleccionar_plan(self):
        # Lógica para seleccionar el plan
        pass

# ServicioCompostaje
class ServicioCompostaje(models.Model):
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    estado = models.ForeignKey(EstadoServicio, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    plan = models.ForeignKey(PlanRecojo, on_delete=models.CASCADE)

    def ver_informacion_servicio(self):
        # Lógica para mostrar la información del servicio
        pass

# Pago
class Pago(models.Model):
    estado = models.CharField(max_length=50)
    metodo_pago = models.CharField(max_length=50)
    fecha_pago = models.DateField()
    servicio = models.ForeignKey(ServicioCompostaje, on_delete=models.CASCADE)

    def procesar_pago(self):
        # Lógica para procesar el pago
        pass

    def actualizar_estado(self):
        # Lógica para actualizar el estado del pago
        pass

    def consultar_estado(self):
        # Lógica para consultar el estado del pago
        pass

    def mostrar_pago(self):
        # Lógica para mostrar los detalles del pago
        pass

# Puntos
class Puntos(models.Model):
    cantidad_de_puntos = models.IntegerField()
    plan = models.ForeignKey(PlanRecojo, on_delete=models.CASCADE)

    def calcular_puntos(self):
        # Lógica para calcular los puntos
        pass

# Cupon
class Cupon(models.Model):
    costo_puntos = models.IntegerField()
    local = models.CharField(max_length=30)
    descripcion = models.TextField()
    descuento = models.FloatField()
    imagen = models.CharField(max_length=150)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    puntos = models.ForeignKey(Puntos, on_delete=models.CASCADE)

    def canjear_cupon(self):
        # Lógica para canjear el cupón
        pass

    def ver_informacion_cupon(self):
        # Lógica para mostrar información del cupón
        pass

    def ver_qr(self):
        # Lógica para mostrar el código QR del cupón
        pass