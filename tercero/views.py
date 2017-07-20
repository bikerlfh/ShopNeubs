import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.core import serializers
from django.db import transaction
from django.shortcuts import render, HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import View

from division_territorial.models import *
from ventas.models import PedidoVenta, PedidoVentaPosicion
from .forms import ClienteForm
from .models import TipoDocumento, Proveedor, DatoBasicoTercero, Cliente


# Create your views here.

class profile(View):
	def get(self,request,*args,**kwargs):
		if not request.user.is_authenticated:
			raise Http404
		formCliente = None
		try:
			cliente = Cliente.objects.get(usuario = request.user.pk)
			tercero = DatoBasicoTercero.objects.get(pk = cliente.datoBasicoTercero.pk)
			municipio = Municipio.objects.get(pk = cliente.municipio.pk)

			initial = {'nit': tercero.nit, 'correo':cliente.correo,'primerNombre':tercero.primerNombre,
					   'segundoNombre':tercero.segundoNombre,'primerApellido': tercero.primerApellido,
					   'segundoApellido':tercero.segundoApellido,'direccion': tercero.direccion,
					   'telefono': tercero.telefono}
			formCliente = ClienteForm(initial=initial)
			formCliente.fields['tipoDocumento'].initial = tercero.tipoDocumento.pk
			formCliente.set_municipio_value(municipio.pk)
		except Exception as e:
			if e.__class__.__name__ == 'DoesNotExist':
				user = User.objects.get(pk = request.user.pk)
				formCliente = ClienteForm(initial = {'correo':user.email})
				pass
			else:
				raise Http404
		return render(request,"tercero/profile.html",{'form':formCliente,'next': request.GET.get('next')})

	@transaction.atomic
	def post(self,request,*args,**kwargs):
		if not request.user.is_authenticated:
			raise Http404
		
		form = ClienteForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			# se valida el nit del usuario
			if DatoBasicoTercero.objects.filter(nit = data.get('nit'), tipoDocumento=data.get('tipoDocumento')).exists():
				messages.error(request,'Ya existe un usuario con nit %s' % data.get('nit'))
				return render(request,"tercero/profile.html",{'form':form})
			cliente = None
			tercero = None
			user = User.objects.get(pk = request.user.pk)
			municipio = Municipio.objects.get(pk = data.get('municipio'))
			try:
				cliente = Cliente.objects.get(usuario = request.user.pk)
				tercero = DatoBasicoTercero.objects.get(pk = cliente.datoBasicoTercero.pk)
				
				# se modifican los campos del tercero
				tercero.tipoDocumento = TipoDocumento.objects.get(pk = data.get('tipoDocumento'))
				tercero.nit = data.get('nit')
				tercero.primerNombre = data.get('primerNombre')
				tercero.segundoNombre = data.get('segundoNombre')
				tercero.primerApellido = data.get('primerApellido')
				tercero.segundoApellido = data.get('segundoApellido')
				tercero.direccion = data.get('direccion')
				tercero.telefono = data.get('telefono')
				# Se modifican los campos del cliente
				cliente.correo = data.get('correo')
				cliente.datoBasicoTercero = tercero
				cliente.municipio = municipio
			except Exception as e:
				# Si el cliente no existe, se registra
				if e.__class__.__name__ == 'DoesNotExist':
					tercero = DatoBasicoTercero(tipoDocumento = TipoDocumento.objects.get(pk=data.get('tipoDocumento')),nit = data.get('nit'),
												primerNombre = data.get('primerNombre'),segundoNombre = data.get('segundoNombre'),primerApellido = data.get('primerApellido'),
												segundoApellido  = data.get('segundoApellido'),direccion = data.get('direccion'),telefono = data.get('telefono'))
					cliente = Cliente(correo = data.get('correo'),datoBasicoTercero = tercero,municipio = municipio)
					user = User.objects.get(pk = request.user.pk)
					cliente.usuario = user
				else: 
					raise Http404(e)

			tercero.save()
			cliente.datoBasicoTercero = tercero
			cliente.save()
			# Se modifica el Email del Usuario
			user.email = data.get('correo')
			user.save()
			messages.success(request,"Tu perfil ha sido modificado")
			if request.POST.get('next'):
				return HttpResponseRedirect(request.POST.get('next'))
			else:
				return HttpResponseRedirect(reverse('home'))
		else:
			return render(request,"tercero/profile.html",{'form':form})

def mis_pedidos(request):
	listado_pedidos = None
	try:
		cliente = Cliente.objects.get(usuario = request.user.pk)
		select_extra = {'cantidad':'SELECT COUNT(*) FROM \"PedidoVentaPosicion\" WHERE \"idPedidoVenta\"=\"PedidoVenta\".\"idPedidoVenta\"',
						'costoTotal':'SELECT SUM(\"costoTotal\") FROM \"PedidoVentaPosicion\" WHERE \"idPedidoVenta\"=\"PedidoVenta\".\"idPedidoVenta\"'}
		listado_pedidos = PedidoVenta.objects.filter(cliente = cliente).extra(select=select_extra).order_by('-fecha').values('idPedidoVenta','numeroPedido','cantidad','costoTotal','estadoPedidoVenta__descripcion','fecha')
	except Exception as e:
		pass
	return render(request,"tercero/mis-pedidos.html", {'listado_pedido': listado_pedidos})

def pedido_detalle(request,idPedidoVenta):
	pedidoVenta = PedidoVenta.objects.values('numeroPedido','estadoPedidoVenta__descripcion','fecha').get(pk=idPedidoVenta)
	listado_pedido_posicion = PedidoVentaPosicion.objects.filter(pedidoVenta = idPedidoVenta).values('producto__numeroProducto','producto__nombre','cantidad','costoTotal')
	return render(request,"tercero/pedido_detalle.html",{'pedidoVenta':pedidoVenta,'listado_pedido_posicion':listado_pedido_posicion})

def proveedor_json(request):
	# serializamos en json todos los proveedores e usamos los natural_key de las llaves foraneas
	datos = json.loads(serializers.serialize('json',Proveedor.objects.all(),fields=('correo','webSite','datoBasicoTercero'),use_natural_foreign_keys=True))
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'data': datos}
	return HttpResponse(json.dumps(dic),content_type='application/json')

def busqueda_proveedor_modal(request):
	# columnas del DataTable ejemplo ('column name': 'valor')
	columns = { 'Nombre': 'fields.datoBasicoTercero','Web Site':'fields.webSite','Email':'fields.correo'}
	# objeto donde se almacenará el PK del registro seleccionado
	objectPk = '#idProveedor'
	# objeto donde se visualizará el registro seleccionado
	# { 'objeto','columna' }
	objectShow = {'#proveedor':'fields.datoBasicoTercero'}
	return render(request,"base/tabla-dinamica-modal.html",{ 'title': 'Busqueda de Proveedores','url':"/tercero/proveedor/json/", 'columns': columns, 'objectPk':objectPk, 'objectShow':objectShow })



def cliente_json(request):
	# serializamos en json todos los proveedores e usamos los natural_key de las llaves foraneas
	datos = json.loads(serializers.serialize('json',Cliente.objects.all(),fields=('datoBasicoTercero'),use_natural_foreign_keys=True))
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'data': datos}
	return HttpResponse(json.dumps(dic),content_type='application/json')

def busqueda_cliente_modal(request):
	# columnas del DataTable ejemplo ('column name': 'valor')
	columns = { 'Nombre': 'fields.datoBasicoTercero'}
	# objeto donde se almacenará el PK del registro seleccionado
	objectPk = '#idCliente'
	# objeto donde se visualizará el registro seleccionado
	# { 'objeto','columna' }
	objectShow = {'#cliente':'fields.datoBasicoTercero'}
	return render(request,"base/tabla-dinamica-modal.html",{ 'title': 'Busqueda de Clientes','url':"/tercero/cliente/json/", 'columns': columns, 'objectPk':objectPk, 'objectShow':objectShow })
