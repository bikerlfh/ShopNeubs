import json

from django.contrib import messages
from django.core import serializers
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import View

from compras.pedidocompramanager import PedidoCompraManager
from .forms import ConsultaPedidoCompraForm
from .models import EstadoPedidoCompra, PedidoCompra, PedidoCompraPosicion


class solicitud_pedido(View):
	def get(self,request,*args,**kwargs):
		try:
			context = { 'codigo_estado_pedido':'01','listado_estado_pedido_compra' : EstadoPedidoCompra.objects.all()}
		except EstadoPedidoCompra.DoesNotExist:
			messages.warning(request, 'No se encontrarón los estados de pedido compra!')
		return render(request,"compras/solicitud_pedido.html",context)

	
	def post(self,request,*args,**kwargs):
		data = request.POST
		# se instancia la clase PedidoCompraManager y le pasamos el idProveedor y el idEstadoPedidoCompra
		pedidoCompraManager = PedidoCompraManager(data.get('idProveedor'),data.get('idEstadoPedidoCompra'),request.user)
		# se sacan los indices del pedido posicion
		indice_posicion = [key.replace('idProducto','') for key in request.POST if key.startswith("idProducto")]		
		for indice in indice_posicion:
			pedidoCompraManager.add_posicion(data.get('idProducto'+indice),int(data.get('cantidad'+indice)),data.get('costo_total'+indice))
		# si todo guarda bien 
		if pedidoCompraManager.save():
			#messages.success(request,"Se ha guardado existosamente el pedido con el número: " + str(PedidoCompraManager.pedidoCompra.numeroPedido))
			request.POST = None
			messages.success(request,"Se ha guardado existosamente el pedido con el número: " + str(pedidoCompraManager.pedidoCompra.numeroPedido))
		else:
			messages.warning(request,pedidoCompraManager.error)
		return HttpResponseRedirect(reverse('solicitud_compra'))

class consulta_pedido(View):

	def get(self,request, *args,**kwargs):
		return render(request,'compras/consulta_pedido_compra.html',{'form':ConsultaPedidoCompraForm()})

	def post(self,request, *args,**kwargs):
		form = ConsultaPedidoCompraForm(request.POST)
		
		listado_pedido = None
		if form.is_valid():
			data = form.cleaned_data
			numeroPedido = data.get('numeroPedido')
			idCliente = data.get('idProveedor')
			idEstadoPedidoCompra = data.get('estadoPedidoCompra')
			
			kwargs = {}
			if len(numeroPedido)>0:
				kwargs['numeroPedido']= numeroPedido
			if len(idEstadoPedidoCompra)>0:			
				kwargs['estadoPedidoCompra'] = idEstadoPedidoCompra
			if len(idCliente) >0:
				kwargs['proveedor'] = idCliente
			try:
				listado_pedido = PedidoCompra.objects.filter(**kwargs)
			except PedidoCompra.DoesNotExist:
				pass				
		return render(request,'compras/consulta_pedido_compra.html',{'form':form,'listado_pedido_compra':listado_pedido})

# Retorna un json con los pedidos compra posicion de un pedido
def pedido_compra_posicion_json(request,idPedidoCompra):
	# serializamos en json todos los pedidos
	# Se consultan todos las posiciones del pedido compra
	datos = json.loads(serializers.serialize('json',PedidoCompraPosicion.objects.filter(pedidoCompra = idPedidoCompra),
					   						 fields=('producto','cantidad','costoTotal'),use_natural_foreign_keys=True))
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'data': datos}
	return HttpResponse(json.dumps(dic),content_type='application/json')



