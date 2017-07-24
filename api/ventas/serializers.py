from rest_framework.serializers import (Serializer, ListSerializer, ModelSerializer, HyperlinkedIdentityField,
										SerializerMethodField, IntegerField)

from api.inventario.serializers import ProductoSimpleSerializer
from inventario.models import SaldoInventario
from ventas.models import PedidoVenta, PedidoVentaPosicion
from ventas.pedidoventamanager import PedidoVentaManager
from ventas.send_mail_venta import send_email_pedido_venta


class PedidoVentaSimpleSerializer(ModelSerializer):
	urlDetalle = HyperlinkedIdentityField(read_only=True, view_name='pedido_detalle_simple', lookup_field='idPedidoVenta')
	idCliente = SerializerMethodField()
	estadoPedidoVenta = SerializerMethodField()
	numeroProductos = SerializerMethodField()
	valorTotal = SerializerMethodField()
	fecha = SerializerMethodField()
	motivoCancelacionPedidoVenta = SerializerMethodField()

	class Meta:
		model = PedidoVenta
		fields = [
			'idPedidoVenta',
			'idCliente',
			'numeroProductos',
			'valorTotal',
			'estadoPedidoVenta',
			'numeroPedido',
			'fecha',
			'fechaAutorizacion',
			'motivoCancelacionPedidoVenta',
			'urlDetalle',

		]

	def get_idCliente(self, obj):
		return obj.cliente_id

	def get_fecha(self, obj):
		return obj.fecha.strftime("%d/%m/%Y %H:%M")

	# def get_cliente(self,obj):
	# 	return obj.cliente.datoBasicoTercero.__str__()
	def get_estadoPedidoVenta(self, obj):
		return obj.estadoPedidoVenta.descripcion

	def get_motivoCancelacionPedidoVenta(self, obj):
		if obj.motivoCancelacionPedidoVenta:
			return obj.motivoCancelacionPedidoVenta.descripcion
		return None

	def get_numeroProductos(self, obj):
		return sum(p.cantidad for p in PedidoVentaPosicion.objects.filter(pedidoVenta_id=obj.pk))

	def get_valorTotal(self, obj):
		return sum(p.costoTotal for p in PedidoVentaPosicion.objects.filter(pedidoVenta_id=obj.pk))


class PedidoVentaPosicionSerializer(ModelSerializer):
	producto = ProductoSimpleSerializer()
	idSaldoInventario = SerializerMethodField()
	motivoCancelacionPedidoVenta = SerializerMethodField()

	class Meta:
		model = PedidoVentaPosicion
		fields = [
			'idPedidoVentaPosicion',
			'producto',
			'cantidad',
			'idSaldoInventario',
			'costoTotal',
			'cancelado',
			'motivoCancelacionPedidoVenta'

		]

	def get_motivoCancelacionPedidoVenta(self, obj):
		if obj.motivoCancelacionPedidoVenta:
			return obj.motivoCancelacionPedidoVenta.descripcion
		return None

	def get_idSaldoInventario(self, obj):
		return SaldoInventario.objects.get(producto=obj.producto_id, proveedor=obj.proveedor_id).pk


class PedidoVentaCompletoSerializer(ModelSerializer):
	idCliente = SerializerMethodField()
	estadoPedidoVenta = SerializerMethodField()
	numeroProductos = SerializerMethodField()
	valorTotal = SerializerMethodField()
	fecha = SerializerMethodField()
	motivoCancelacionPedidoVenta = SerializerMethodField()
	pedidoVentaPosicion = SerializerMethodField()

	class Meta:
		model = PedidoVenta
		fields = [
			'idPedidoVenta',
			'idCliente',
			'numeroProductos',
			'valorTotal',
			'estadoPedidoVenta',
			'numeroPedido',
			'fecha',
			'fechaAutorizacion',
			'motivoCancelacionPedidoVenta',
			'pedidoVentaPosicion',
		]

	def get_idCliente(self, obj):
		return obj.cliente_id

	def get_fecha(self, obj):
		return obj.fecha.date()

	# def get_cliente(self,obj):
	# 	return obj.cliente.datoBasicoTercero.__str__()
	def get_estadoPedidoVenta(self, obj):
		return obj.estadoPedidoVenta.descripcion

	def get_motivoCancelacionPedidoVenta(self, obj):
		if obj.motivoCancelacionPedidoVenta:
			return obj.motivoCancelacionPedidoVenta.descripcion
		return None

	def get_numeroProductos(self, obj):
		return sum(p.cantidad for p in PedidoVentaPosicion.objects.filter(pedidoVenta_id=obj.pk))

	def get_valorTotal(self, obj):
		return sum(p.costoTotal for p in PedidoVentaPosicion.objects.filter(pedidoVenta_id=obj.pk))

	def get_pedidoVentaPosicion(self, obj):
		return (PedidoVentaPosicionSerializer(instance=p).data for p in
				PedidoVentaPosicion.objects.filter(pedidoVenta_id=obj.pk))


"""
Serializer para el detalle del pedido.
No es necesario visualizar todos los campos, solo las posiciones
"""


class PedidoVentaDetalleSerializer(ModelSerializer):
	pedidoVentaPosicion = SerializerMethodField()

	class Meta:
		model = PedidoVenta
		fields = [
			'idPedidoVenta',
			'pedidoVentaPosicion'
		]

	def get_pedidoVentaPosicion(self, obj):
		return (PedidoVentaPosicionSerializer(instance=p).data for p in
				PedidoVentaPosicion.objects.filter(pedidoVenta_id=obj.pk))


""" 
	*****************************************************
	SERIALIZERS DE SOLICITUD PEDIDO VENTA
    ***************************************************** 
"""


class PosicionPedidoListSerializer(ListSerializer):
	many = True

	# child = PedidoVentaPosicionCreateSerializer()

	# retorna el numero del pedido
	# -1 si no se guardó el pedido
	def create(self, validated_data):
		# se instancia el PedidoVentaManager pasandole el usuario_id
		pedidoVentaManager = PedidoVentaManager(validated_data[0].get('user'))
		for item in validated_data:
			saldoInventario = SaldoInventario.objects.get(pk=item.get('idSaldoInventario'))
			pedidoVentaManager.add_posicion(saldoInventario, item.get('cantidad'))

		pedidoVenta = None
		if pedidoVentaManager.save():
			send_email_pedido_venta(pedidoVentaManager.get_pedidoVenta())
			pedidoVenta = pedidoVentaManager.get_pedidoVenta()
		return pedidoVenta


class PosicionPedidoSerializer(Serializer):
	cantidad = IntegerField()
	idSaldoInventario = IntegerField()

	class Meta:
		list_serializer_class = PosicionPedidoListSerializer

	# retorna el numero del pedido
	# -1 si no se guardó el pedido
	def create(self, validated_data):
		pedidoVentaManager = PedidoVentaManager(validated_data.get('user'))
		saldoInventario = SaldoInventario.objects.get(pk=validated_data.get('idSaldoInventario'))
		pedidoVentaManager.add_posicion(saldoInventario, validated_data.get('cantidad'))

		pedidoVenta = -1
		if pedidoVentaManager.save():
			send_email_pedido_venta(pedidoVentaManager.get_pedidoVenta())
			pedidoVenta = pedidoVentaManager.get_pedidoVenta()
		return pedidoVenta
