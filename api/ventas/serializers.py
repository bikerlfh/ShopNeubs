from inventario.models import Categoria,Producto,SaldoInventario
from rest_framework.serializers import (ModelSerializer, HyperlinkedIdentityField,
										SerializerMethodField,ValidationError,IntegerField)
from inventario.models import SaldoInventario
from ventas.models import PedidoVenta,PedidoVentaPosicion,EstadoPedidoVenta,MotivoCancelacionPedidoVenta
from ventas.pedidoventamanager import PedidoVentaManager

class PedidoVentaListSerializer(ModelSerializer):
	#cliente = SerializerMethodField()
	idCliente = SerializerMethodField()
	estadoPedidoVenta = SerializerMethodField()
	numeroProductos = SerializerMethodField()
	valorTotal = SerializerMethodField()
	fecha = SerializerMethodField()
	motivoCancelacionPedidoVenta = SerializerMethodField()
	#listadoPedidoVentaPosicion = SerializerMethodField()
	class Meta:
		model = PedidoVenta
		fields = [
			'pk',
			'idCliente',
			'numeroProductos',
			'valorTotal',
			'estadoPedidoVenta',
			'numeroPedido',
			'fecha',
			'fechaAutorizacion',
			'motivoCancelacionPedidoVenta',
			
		]
	def get_idCliente(self,obj):
		return obj.cliente_id
	def get_fecha(self,obj):
		return obj.fecha.date()
	# def get_cliente(self,obj):
	# 	return obj.cliente.datoBasicoTercero.__str__()
	def get_estadoPedidoVenta(self,obj):
		return obj.estadoPedidoVenta.descripcion
	def get_motivoCancelacionPedidoVenta(self,obj):
		if obj.motivoCancelacionPedidoVenta:
			return obj.motivoCancelacionPedidoVenta.descripcion
		return None
	def get_numeroProductos(self,obj):
		return sum(p.cantidad for p in PedidoVentaPosicion.objects.filter(pedidoVenta_id = obj.pk))
	def get_valorTotal(self,obj):
		return sum(p.costoTotal for p in PedidoVentaPosicion.objects.filter(pedidoVenta_id = obj.pk))


	def validate_listadoPedidoVentaPosicion(self,value):
		data = self.get_initial()
		listadoPedidoVentaPosicion = data.get("listadoPedidoVentaPosicion",None)

		if not listadoPedidoVentaPosicion or len(listadoPedidoVentaPosicion) == 0:
			raise ValidationError("El pedido no tiene posiciones")
		else:
			for posicion in listadoPedidoVentaPosicion:
				saldoInventario = posicion['idSaldoInventario']
				if saldoInventario is None or not SaldoInventario.objects.filter(pk=saldoInventario).exists():
					raise ValidationError("No existe el saldo inventario %s" % idSaldoInventario)
		return value

	def create(self,validated_data):
		pedidoVentaManager = PedidoVentaManager(self.request.user.pk)
		listadoPedidoVentaPosicion = validated_data['listadoPedidoVentaPosicion']
		
		for posicion in listadoPedidoVentaPosicion:
			saldoInventario = SaldoInventario.objects.get(pk=posicion['idSaldoInventario'])
			pedidoVentaManager.add_posicion(saldoInventario.producto,saldoInventario.proveedor,posicion['cantidad'],posicion['costoTotal'])
		if not pedidoVenta.save():
			raise ValidationError("No se ha podido generar el pedido")
		return validated_data


		
# class PedidoVentaPosicionSerializer(ModelSerializer):
# 	pedidoVenta = IntegerField()
# 	idSaldoInventario = IntegerField()
# 	motivoCancelacionPedidoVenta = SerializerMethodField()
# 	class Meta:
# 		model = PedidoVentaPosicion
# 		fields =[
# 			'pk',
# 			'pedidoVenta',
# 			'idSaldoInventario',
# 			'cantidad',
# 			'costoTotal',
# 			'cancelado',
# 			'motivoCancelacionPedidoVenta',
# 		]

# 	def get_motivoCancelacionPedidoVenta(self,obj):
# 		return obj.motivoCancelacionPedidoVenta.descripcion

# 	def validate_idPedidoVenta(self,value):
# 		data = self.get_initial()
# 		pedidoVenta = data.get("pedidoVenta")

# 		if not PedidoVenta.objects.filter(pk = pedidoVenta).exists():
# 			raise ValidationError("No existe el pedido venta %s" % pedidoVenta)
# 		return value
# 	def validate_idSaldoInventario(self,value):
# 		data = self.get_initial()
# 		idSaldoInventario = data.get("idSaldoInventario")

# 		if not SaldoInventario.objects.filter(pk = idSaldoInventario).exists():
# 			raise ValidationError("No existe el saldo inventario %s" % idSaldoInventario)
# 		return value

	# def create(self,validated_data):
	# 	idPedidoVenta = validated_data['idPedidoVenta']
	# 	idSaldoInventario = validated_data['idSaldoInventario']
	# 	cantidad = validated_data['cantidad']
	# 	costoTotal = validated_data['costoTotal']
	# 	cancelado = validated_data['cancelado']

	# 	pedidoVenta = PedidoVenta.objects.get(pk = idPedidoVenta)
	# 	saldoInventario = SaldoInventario.objects.get(pk=idSaldoInventario)

	# 	posicion = PedidoVentaPosicion(pedidoVenta=pedidoVenta,
	# 								   producto=saldoInventario.producto,
	# 								   proveedor=saldoInventario.proveedor,
	# 								   cantidad=cantidad,
	# 								   costoTotal=costoTotal,
	# 								   cancelado = cancelado)
	# 	posicion.save()
	# 	return validated_data






