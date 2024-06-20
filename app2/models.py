from django.contrib.auth.models import User
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.forms import model_to_dict
from django_resized import ResizedImageField

ESTADOS = ( 
    ("Programado", "Programado"), 
    ("En espera", "En espera"), 
    ("En proceso", "En proceso"), 
    ("Atrasado", "Atrasado"),  
    ("Realizado", "Realizado")
    )

UNIDAD_COMPRA = ( 
    ("Pieza", "Pieza"),  
    ("Kg", "Kg"), 
    ("gramos", "gramos"),
    ("Lt", "Lt"), 
    ("Metro", "Metro"),  
    ("Caja", "Caja"), 
    ("Onza", "Onza"),
    ("Charola", "Charola"),
    ("Otro", "Otro")
    )

def validate_image(imagen):
    max_height = 100
    max_width = 100
    height = imagen.height 
    width = imagen.width
    if width > max_width or height > max_height:
        raise ValidationError("El largo de la imagen no debe superar los {} px y ancho de la imagen no deben superar los {} px".format(max_height, max_width))


def validate_image_equipo(imagen):
    max_height = 300
    max_width = 400
    height = imagen.height 
    width = imagen.width
    if width > max_width or height > max_height:
        raise ValidationError("El largo de la imagen no debe superar los {} px y ancho de la imagen no deben superar los {} px".format(max_height, max_width))


class Iva (models.Model):
    monto = models.DecimalField(max_digits=15, decimal_places=2, null=False)

    class Meta:
        verbose_name='iva'
        verbose_name_plural = 'iva'
    
    def __str__(self):
        return str(self.monto)


class Cliente(models.Model):
    ruc = models.CharField(max_length=11, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()

    def __str__(self):
        return self.nombre

class Egreso(models.Model):
    fecha_pedido = models.DateField(max_length=255)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL , null=True , related_name='clientee')
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    pagado = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    comentarios = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    ticket = models.BooleanField(default=True)
    desglosar = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now_add=True , null=True)

    class Meta:
        verbose_name='egreso'
        verbose_name_plural = 'egresos'
        order_with_respect_to = 'fecha_pedido'
    
    def __str__(self):
        return str(self.id)


class Empresa (models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False, default="IC")
    domicilio = models.CharField(max_length=255, null=True)
    telefono = models.CharField(max_length=255, null=True)
    imagen = ResizedImageField(size=[100, 100], upload_to='empresa', blank=True, null=True)
    moneda = models.CharField(max_length=255, null=False, blank=False, default="$" )
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name='empresa'
        verbose_name_plural = 'empresa'
    
    def __str__(self):
        return self.nombre


class Producto (models.Model):
    codigo = models.CharField(max_length=255, null=True, blank = True)
    descripcion =  models.CharField(max_length=255, unique=True, null=False)
    imagen = ResizedImageField(size=[100, 100], upload_to='productos', blank=True, null=True)
    costo = models.DecimalField(max_digits=20, decimal_places=2, null=False, default = 0)
    precio = models.DecimalField(max_digits=20, decimal_places=2, null=False, default =0)
    iva = models.DecimalField(max_digits=20, decimal_places=2, null=False, default =0)
    cantidad = models.DecimalField(max_digits=20, decimal_places=2 , null=False,default=0)
    porcion = models.DecimalField(max_digits=20, decimal_places=2 , null=False,default=1)
    unidad = models.CharField(max_length=255, choices = UNIDAD_COMPRA, default='Pieza', null=False)
    unidad_venta = models.CharField(max_length=255, choices = UNIDAD_COMPRA, default='Pieza', null=False)
    servicio = models.BooleanField(default=False)
    barcode = models.CharField(max_length=255, unique=False, null=True, blank = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name='producto'
        verbose_name_plural = 'productos'
        order_with_respect_to = 'descripcion'
    
    def __str__(self):
        return self.descripcion

    def toJSON(self):
        item = model_to_dict(self, exclude=['imagen', 'created', 'updated'])
        return item
