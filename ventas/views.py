from django.contrib import messages
from django.core import serializers
from django.shortcuts import render,HttpResponse,HttpResponseRedirect,Http404,get_list_or_404,get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from .cart import Cart
from .forms import ConsultaPedidoVentaForm
from .pedidoventamanager import PedidoVentaManager
from .models import EstadoPedidoVenta,PedidoVenta,PedidoVentaPosicion,PosicionVentaCompra,MotivoCancelacionPedidoVenta
from tercero.models import Cliente
from compras.models import PedidoCompra

# from django.contrib.auth.decorators import login_required,permission_required
# from django.utils.decorators import method_decorator
import json

def cart(request):
	cart = request.session.get('shop_cart',None)
	# Si existe el carro y tiene cantidades pero no tiene items, se debe eliminar el carro
	if cart != None and cart.cantidad_total > 0 and len(cart.items) == 0:
		del request.session['shop_cart']
	return render(request,"ventas/cart.html",{ 'cart' : cart})

def add_cart(request,idSaldoInventario,cantidad):
	carrito = None
	if not 'shop_cart' in request.session:
		carrito = Cart()
	else:
		carrito =  request.session.get('shop_cart')
	try:
		carrito.add_item(int(idSaldoInventario),int(cantidad))
	except Exception as e:
		# Si la excepción es en la consulta de un modelo
		if e.__class__.__name__ is "DoesNotExist":
			raise Http404('Upps! No se encontró el producto')
	
	request.session['shop_cart'] = carrito
	dic_carro = { 'cart' : {'cantidad_total':str(carrito.cantidad_total),'valor_total':str(carrito.valor_total)} }
	return HttpResponse(json.dumps(dic_carro),content_type='application/json')

def ajustar_cantidad_cart(request,idSaldoInventario,cantidad):
	carrito = None
	if not 'shop_cart' in request.session:
		carrito = Cart()
	else:
		carrito =  request.session.get('shop_cart')

	try:
		carrito.ajustar_cantidad(int(idSaldoInventario),int(cantidad))
	except Exception as e:
		# Si la excepción es en la consulta de un modelo
		if e.__class__.__name__ is "DoesNotExist":
			raise Http404('Upps! No se encontró el producto')
	
	request.session['shop_cart'] = carrito
	dic_carro = { 'cart' : {'cantidad_total':str(carrito.cantidad_total),'valor_total':str(carrito.valor_total)} }
	return HttpResponse(json.dumps(dic_carro),content_type='application/json')

def remove_item(request,idSaldoInventario):
	if 'shop_cart' in request.session:
		carrito =  request.session.get('shop_cart')
		if carrito.remove_item(int(idSaldoInventario)):
			messages.success(request,carrito.get_last_log_success())
		else:
			messages.success(request,carrito.get_last_log_error())
		if carrito.cantidad_total <=0:
			del request.session['shop_cart']
		else:
			request.session['shop_cart'] = carrito
	else:
		raise Http404()
	return HttpResponseRedirect(reverse('cart'))


def solicitud_pedido(request):
	if not 'shop_cart' in request.session:
		return HttpResponseRedirect(reverse('cart'))

	cart  = request.session.get('shop_cart')
	if len(cart.items) <= 0:
		messages.info(request,"No se encontró ningún producto en el carro!")
		return HttpResponseRedirect(reverse('cart'))

	# Se valida que el usuario ya esté creado como cliente
	try:
		cliente = Cliente.objects.get(usuario = request.user)
	except Cliente.DoesNotExist:
		messages.info(request,"Favor Actualice sus datos")
		# Se redirige el cliente al profile.
		# cuando éste realice la actualización de datos, se redigirá a cart nuevamente
		return HttpResponseRedirect(reverse('profile') + "?next="+reverse('cart'))
	# se crea el objeto PedidoVenta
	pedidoVenta = PedidoVentaManager(request.user.pk)
	# se agregan los detalles del pedido
	for item in cart.items:
		pedidoVenta.add_posicion(item.saldoInventario.producto,item.saldoInventario.proveedor,item.cantidad,item.valor_total)
	# Se guarda el pedido
	if pedidoVenta.save():
		# se elimina el carro
		del request.session['shop_cart']
		#messages.success(request,"Tu pedido ha sido enviado satisfactoriamente, muy pronto nos comunicaremos contigo.")
		return HttpResponseRedirect(reverse('pedido_enviado',kwargs={'numeroPedido': pedidoVenta.get_numero_pedido()}))
	else:
		#messages.info(request,"No se ha podido enviar tu pedido. Te pedimos disculpas.")
		#return HttpResponse(pedidoVenta.error)
		return HttpResponseRedirect(reverse('pedido_no_generado'))

def pedido_enviado(request,numeroPedido):
	return render(request,'ventas/pedido_enviado.html',{ 'numeroPedido':numeroPedido })
def pedido_no_generado(request,numeroPedido):
	return render(request,'ventas/pedido_no_generado.html',{ 'numeroPedido':numeroPedido })

class autorizar_pedido(View):
	#@permission_required('PedidoVenta.autorizar_pedido')
	
	def get(self,request,*args,**kwargs):
		# Se consultan los estados de pedido 02 - Autorizado y 06 - Cancelado
		listado_estado_pedido = get_list_or_404(EstadoPedidoVenta,codigo__in = ['02','06'])
		return render(request,"ventas/autorizar_pedido.html",{ 'listado_estado_pedido' : listado_estado_pedido })

	def post(self,request,*args,**kwargs):
		data = request.POST
		pedidoVenta = PedidoVentaManager()
		if pedidoVenta.autorizar_pedido(data.get('idPedidoVenta'),data.get('idEstadoPedidoVenta'),request.user):
			messages.success(request,"El pedido venta ha sido autorizado")
		else:
			messages.error(request,pedidoVenta.error)
		return HttpResponseRedirect(reverse('autorizar_venta'))

	#@method_decorator(permission_required('ventas.autorizar_pedido',login_url='/'))
	#def dispatch(self, *args, **kwargs):
	#	return super(autorizar_pedido, self).dispatch(*args, **kwargs)

class consulta_pedido(View):

	def get(self,request, *args,**kwargs):
		return render(request,'ventas/consulta_pedido_venta.html',{'form':ConsultaPedidoVentaForm()})

	def post(self,request, *args,**kwargs):
		form = ConsultaPedidoVentaForm(request.POST)
		
		listado_pedido = None
		if form.is_valid():
			data = form.cleaned_data
			numeroPedido = data.get('numeroPedido')
			idCliente = data.get('idCliente')
			idEstadoPedidoVenta = data.get('estadoPedidoVenta')
			
			kwargs = {}
			if len(numeroPedido)>0:
				kwargs['numeroPedido']= numeroPedido
			if len(idEstadoPedidoVenta)>0:			
				kwargs['estadoPedidoVenta'] = idEstadoPedidoVenta
			if len(idCliente) >0:
				kwargs['cliente'] = idCliente
			try:
				listado_pedido = PedidoVenta.objects.filter(**kwargs)
			except PedidoVenta.DoesNotExist:
				pass				
		return render(request,'ventas/consulta_pedido_venta.html',{'form':form,'listado_pedido_venta':listado_pedido})

def consulta_avanzada_pedido(request):
		return render(request,'ventas/consulta_avanzada_pedido.html')

# Solo para solicitados
def modificar_pedido(request):
	pedidoVenta = None
	if request.GET.get('idPedidoVenta',None):
		pedidoVenta = get_object_or_404(PedidoVenta,pk=request.GET.get('idPedidoVenta'))
		# Solo los pedidos con estado solicitado se pueden modificar
		if pedidoVenta.estadoPedidoVenta.codigo != "01":
			messages.warning(request,'El pedido no se puede modificar porque esta con estado %s' % estadoPedidoVenta.descripcion)
			pedidoVenta = None
		else:
			pedidoVenta.listadoPedidoVentaPosicion = PedidoVentaPosicion.objects.filter(pedidoVenta = pedidoVenta.pk)
	listado_motivo_cancelacion = MotivoCancelacionPedidoVenta.objects.all()
	return render(request,"ventas/modificar_pedido.html",{ 'pedidoVenta': pedidoVenta,'listado_motivo_cancelacion':listado_motivo_cancelacion })

# Permite modificar la posicion de un pedido devolviendo True o False
def modificar_pedido_posicion(request,idPedidoVentaPosicion):
	cantidad = request.GET.get('cantidad',None)
	costoTotal = request.GET.get('costoTotal',None)
	cancelado = request.GET.get('cancelado',None)
	idMotivoCancelacion = request.GET.get('idMotivoCancelacion',None)

	respuesta = {'resultado':'True','cantidad':cantidad,'costoTotal':costoTotal,'cancelado':cancelado,'motivoCancelacion':idMotivoCancelacion}
	try:
		pedidoVentaPosicion = PedidoVentaPosicion.objects.get(pk=idPedidoVentaPosicion)
		if cancelado != None:
			cancelado = bool(int(cancelado))
			pedidoVentaPosicion.cancelado = cancelado
			if idMotivoCancelacion != None:
				pedidoVentaPosicion.motivoCancelacionPedidoVenta = MotivoCancelacionPedidoVenta.objects.get(pk=idMotivoCancelacion)
		elif cantidad != None and costoTotal != None:
			pedidoVentaPosicion.cantidad = cantidad
			pedidoVentaPosicion.costoTotal = costoTotal
		pedidoVentaPosicion.save()
	except Exception as e:
		raise
		respuesta['resultado']='False'
	return HttpResponse(json.dumps(respuesta),content_type='application/json')
	

# Retorna un json con los pedidos ventas con estado 01 - Solicitado si no se envía el código
def pedido_venta_json(request):
	# serializamos en json todos los pedidos
	# Se consultan todos los pedidos venta que esten con estado 01 - Solicitados
	datos = json.loads(serializers.serialize('json',PedidoVenta.objects.filter(estadoPedidoVenta__codigo = '01'),
					   fields=('numeroPedido','cliente','fecha','estadoPedidoVenta'),use_natural_foreign_keys=True))
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'data': datos}
	return HttpResponse(json.dumps(dic),content_type='application/json')

def pedido_venta_json_all(request):
	# serializamos en json todos los pedidos
	# Se consultan todos los pedidos venta
	datos = json.loads(serializers.serialize('json',PedidoVenta.objects.all(),
					   fields=('numeroPedido','cliente','fecha','estadoPedidoVenta'),use_natural_foreign_keys=True))
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'data': datos}
	return HttpResponse(json.dumps(dic),content_type='application/json')

# Retorna un json con los pedidos ventas posicion de un pedido
def pedido_venta_posicion_json(request,idPedidoVenta):
	# serializamos en json todos los pedidos
	# Se consultan todos las posiciones del pedido venta
	datos = json.loads(serializers.serialize('json',PedidoVentaPosicion.objects.filter(pedidoVenta = idPedidoVenta),
					   						 fields=('producto','proveedor','cantidad','costoTotal'),use_natural_foreign_keys=True))
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'data': datos}
	return HttpResponse(json.dumps(dic),content_type='application/json')

# Abre la busqueda en el modal de los pedidos venta
def busqueda_pedido_venta_modal(request):
	# columnas del DataTable ejemplo ('column name': 'valor')
	columns = { 'Numero Pedido':'fields.numeroPedido','Cliente':'fields.cliente','Fecha': 'fields.fecha','Estado':'fields.estadoPedidoVenta'}
	# objeto donde se almacenará el PK del registro seleccionado
	objectPk = '#idPedidoVenta'
	if request.GET.get("objectPk",None) is not None:
		objectPk = "#"+request.GET.get("objectPk")
	
	url = reverse('pedido_venta_json')
	if request.GET.get('all',None) is not None:
		url = reverse('pedido_venta_json_all')
	# objeto donde se visualizará el registro seleccionado
	# { 'objeto','columna' }
	objectShow = {'#numeroPedido':'fields.numeroPedido','#cliente':'fields.cliente'}
	return render(request,"base/tabla-dinamica-modal.html",{ 'title': 'Busqueda de Pedido Venta','url':url, 
															 'columns': columns, 'objectPk':objectPk, 'objectShow':objectShow })


# Retorna un json de pedidoCompraPosicion relacionados con el pedidoVentaPosicion
def pedido_venta_compra_json(request,idPedidoVentaPosicion):
	# serializamos en json
	listado_posicion = list(({'pk':p.pk,'numeroPedido':p.pedidoCompraPosicion.pedidoCompra.numeroPedido,
							  'proveedor': str(p.pedidoCompraPosicion.pedidoCompra.proveedor),
							  'producto':str(p.pedidoCompraPosicion.producto),
							  'cantidad':p.cantidad} for p in PosicionVentaCompra.objects.filter(pedidoVentaPosicion = idPedidoVentaPosicion)))
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'data': listado_posicion}
	return HttpResponse(json.dumps(dic),content_type='application/json')