from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from app2.models import Cliente, Empresa, Producto
from datetime import date

moneda: "S/"
TODAY = date.today()

class LoginForm(forms.ModelForm):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'id': 'usuario'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password')
    
    
    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not authenticate(username=username, password=password):
            raise forms.ValidationError("El usuario o contraseña son incorrectos")

class ProductoForm(forms.ModelForm):
    class Meta:
        imagen = forms.ImageField()
        model = Producto
        fields = ('codigo','descripcion', 'imagen', 'costo','iva', 'precio', 'cantidad',  'unidad', 'porcion', 'unidad_venta' ,'servicio', 'barcode')
        labels = {
            'codigo': 'Código interno:',
            'descripcion': 'Descripción: ',
            'imagen': 'Imagen: ',
            'costo': 'Costo: ',
            'iva': 'IVA %: ',
            'precio': 'Precio unit. : ',
            'cantidad': 'Cantidad: ',
            'barcode': 'Código de barras: ',
            'servicio': ' ¿Es servicio?: ', 
            'porcion': 'Relación unidad venta por unidad de compra: (Ejemp. 24 x 1, 1 x 1) ',
            'unidad_venta': 'Unidad venta: '
        }