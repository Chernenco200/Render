from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app2.forms import TODAY , LoginForm,Cliente,Producto
from django.views.generic import ListView
from django.utils.decorators import method_decorator
import os
from datetime import date, datetime , timedelta
HOY = datetime.today().strftime('%Y-%m-%d')


# Create your views here.
from .models import Egreso, Empresa

def logout_view(request):
    logout(request)
    return redirect('Login')

def login_view(request):
    user = request.user

    if user.is_authenticated:
        return redirect('Index')

    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                return redirect('app2')
    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, 'login.html', context)

@login_required(login_url='Login')
def egresos_view(request):
    empresa_id = 1  # Cambia esto según tus necesidades
    try:
        egresos = Egreso.objects.all()
        empresa = Empresa.objects.get(pk=empresa_id)
        moneda = empresa.moneda
    except Empresa.DoesNotExist:
        # Manejo de errores si la empresa no existe
        pass
    context = {
        'egresos': egresos,
        'moneda': "S/"
    }

    return render(request, 'egresos.html', context)


@login_required(login_url='Login')
def inventario_view(request):
    
    form_producto = ProductoForm()
    form_editar_producto = EditarProductoForm()
    form_ajustar = InventarioForm()
    productos = Producto.objects.all()
    num_productos = len(productos)
    empresa = Empresa.objects.get(pk=1)
    moneda = empresa.moneda

    context = {
        'form_producto': form_producto,
        'form_editar_producto': form_editar_producto,
        'productos': productos,
        'num_productos': num_productos, 
        'form_ajustar_producto': form_ajustar,
        'moneda': moneda
    }
    return render(request, 'inventario.html', context)

class ventas(ListView):
    model = Egreso
    template_name = 'ventas.html'

    @method_decorator(login_required(login_url='Login'))
    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request, *args, **kwargs)
    """
    def get_queryset(self):
        return ProductosPreventivo.objects.filter(
            preventivo=self.kwargs['id']
        )
    """
    def post(self, request,*ars, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'autocomplete':
                data = []
                for i in Producto.objects.filter(descripcion__icontains=request.POST["term"])[0:10]:
                    item = i.toJSON()
                    item['value'] = i.descripcion
                    data.append(item)
            else:
                data['error'] = "Ha ocurrido un error"
        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data,safe=False)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context["preventivo"] = Preventivo.objects.get(pk=self.kwargs['id'])
        context["cliente"] = Cliente.objects.get(pk=1)
        context["productos_lista"] = Producto.objects.all()
        context["HOY"] = HOY
        context["clientes_lista"] = Cliente.objects.all()
        empresa = Empresa.objects.all()
        #moneda = empresa.moneda
        #context["moneda"] = moneda
        try:
            context["last_id"] = int(Egreso.objects.latest('id').id) + 1
        except Exception as e:
            context["last_id"] = 1
        return context


@login_required(login_url='Login')
def save_venta_view(request):
    if request.POST:
        data =[]
        try:
            action = request.POST['action']
            if action == "save":
                datos = json.loads(request.POST["verts"])
                id_cliente = request.POST["id_cliente"]
                comentarios = request.POST["comentarios"]
                cliente = Cliente.objects.get(pk=id_cliente)
                total = float(datos["total"])
                fecha = request.POST["fecha"]
                ticket_num = float( request.POST["ticket"])
                efectivo = float( request.POST["efectivo"])
                tarjeta = float( request.POST["tarjeta"])
                transferencia = float( request.POST["transferencia"])
                vales = float( request.POST["vales"])
                otro = float( request.POST["otro"])
                pagado = efectivo + tarjeta + transferencia + vales + otro
                desglosar_num = float( request.POST["desglosar"])

                if ticket_num == 1:
                    ticket =True
                elif ticket_num == 0:
                    ticket = False
                
                if desglosar_num == 1:
                    desglosar =True
                elif desglosar_num == 0:
                    desglosar = False

                venta = Egreso(cliente=cliente, fecha_pedido=fecha, total=total, pagado=pagado, comentarios=comentarios, ticket=ticket, desglosar=desglosar)
                venta.save()

                metodo = MetodoPago(egreso=venta,efectivo=efectivo, tarjeta=tarjeta, transferencia=transferencia, vales=vales, otro=otro)
                metodo.save()

                data.append(venta.id)
                data.append(venta.ticket)
                data.append(venta.desglosar)

                for i in datos["products"]:
                    pr_save = Producto.objects.get(pk=float(i["id"]))

                    if pr_save.servicio == False:
                        porcion_convertida = float(i["cantidad"]) * (1/float(pr_save.porcion))
                        suma = float(pr_save.cantidad) - porcion_convertida
                        pr_save.cantidad = suma
                        pr_save.save()

                   
                    iva_producto = float(pr_save.iva)

                    if iva_producto != 0:
                        subtotal = float(i["subtotal"]) / (1+iva_producto)
                        iva = subtotal * iva_producto
                    else:
                        subtotal = float(i["subtotal"])
                        iva = 0

                    product = ProductosEgreso(egreso=venta, producto=pr_save,cantidad=float(i["cantidad"]),precio=float(i["precio"]),subtotal=subtotal,iva=iva,total=float(i["subtotal"]))
                    product.save()
                    print(i["subtotal"])

                messages.info(request,"Venta agregada con éxito")
        except Exception as e:
            data['error'] = str(e)

    return JsonResponse(data,safe=False)

@login_required(login_url='Login')
def export_pdf_view(request, id, iva):
    #print(id)
    template = get_template("ticket.html")
    #print(id)
    subtotal = 0 
    iva_suma = 0 

    venta = Egreso.objects.get(pk=float(id))
    datos = ProductosEgreso.objects.filter(egreso=venta)
    for i in datos:
        subtotal = subtotal + float(i.subtotal)
        iva_suma = iva_suma + float(i.iva)

    empresa = Empresa.objects.get(pk=1)
    context ={
        'num_ticket': id,
        'iva': iva,
        'fecha': venta.fecha_pedido,
        'cliente': venta.cliente.nombre,
        'items': datos, 
        'total': venta.total, 
        'empresa': empresa,
        'comentarios': venta.comentarios,
        'subtotal': subtotal,
        'iva_suma': iva_suma,
    }
    html_template = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; ticket.pdf"
    css_url = os.path.join(settings.BASE_DIR,'index\static\index\css/bootstrap.min.css')
    #HTML(string=html_template).write_pdf(target="ticket.pdf", stylesheets=[CSS(css_url)])
   
    font_config = FontConfiguration()
    HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf(target=response, font_config=font_config,stylesheets=[CSS(css_url)])

    return response

