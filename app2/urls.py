from django.urls import path
from app2 import views

urlpatterns = [
    path('', views.login_view, name='Login'),
    path('logout/', views.logout_view, name='Logout'),
    path('egresos/', views.egresos_view, name='Index'),
    path('productos/', views.inventario_view, name='Product'),
    path('ventas/',views.ventas.as_view(), name='Venta'),
    path('add_venta/', views.save_venta_view, name='AddVenta'),
    path('export/', views.export_pdf_view, name="ExportPDF" ),



]
        