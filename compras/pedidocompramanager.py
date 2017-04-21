from inventario.models import Producto,SaldoInventario,MovimientoInventario
from compras.models import *
from tercero.models import Proveedor
from django.db import transaction

class PedidoCompraManager:

	rangoNumeroPedidoCompra = None
	pedidoCompra = None
	listadoPedidoCompraPosicion = None
	estadoPedidoCompra = None
	proveedor = None
	usuario = None

	error = ""

	def __init__(self,idProveedor,idEstadoPedidoCompra,user):
		self.proveedor = Proveedor.objects.get(pk=idProveedor)
		self.estadoPedidoCompra = EstadoPedidoCompra.objects.get(pk=idEstadoPedidoCompra)
		self.listadoPedidoCompraPosicion = []
		self.usuario = user
	

	def add_posicion(self,idProducto,cantidad,costoTotal):
		posicion = PedidoCompraPosicion(cantidad = cantidad,costoTotal = costoTotal)
		posicion.producto = Producto.objects.get(pk = idProducto)
		self.listadoPedidoCompraPosicion.append(posicion)

	#@transaction.atomic
	def save(self):
		transaction.set_autocommit(False)
		try:
			if len(self.listadoPedidoCompraPosicion) is 0:
				raise Exception("El pedido no tiene posiciones!")
				#raise "ERROR:Agregue un pedido compra posición"
			self.pedidoCompra= PedidoCompra(proveedor=self.proveedor,estadoPedidoCompra=self.estadoPedidoCompra,idUsuarioCreacion = self.usuario.pk)
			self.rangoNumeroPedidoCompra = RangoNumeroPedidoCompra.objects.get(estado = True)
			if self.rangoNumeroPedidoCompra.numeroActual > self.rangoNumeroPedidoCompra.numeroHasta:
				raise Exception("No hay rango disponible para el pedido a generar")
			self.pedidoCompra.numeroPedido = self.rangoNumeroPedidoCompra.numeroActual
			# Se actualiza el numeroActual del rango numero pedido compra
			self.rangoNumeroPedidoCompra.numeroActual +=1
			self.rangoNumeroPedidoCompra.save()

			# Se giarda la cabecera del pedido
			self.pedidoCompra.save()
			
			# Se asigna el id de la cabecera a cada posición y se guarda
			for posicion in self.listadoPedidoCompraPosicion:
				posicion.pedidoCompra = self.pedidoCompra
				posicion.save()
			
			# Se guarda el movimiento del inventario
			movimientoInventario = MovimientoInventario(pedidoCompra = self.pedidoCompra,idUsuarioCreacion=self.usuario.pk)
			movimientoInventario.save()
		except Exception as e:
			transaction.rollback()
			self.error = e
			return False
		else: 
			transaction.commit()
		finally:
			transaction.set_autocommit(True)
		return True