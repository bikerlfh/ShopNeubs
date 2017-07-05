from django.db import transaction
from datetime import datetime
from inventario.models import Producto,SaldoInventario,MovimientoInventario,MovimientoInventarioPosicion,ProductoReview
from ventas.models import *
from compras.models import PedidoCompraPosicion
from tercero.models import Cliente

class PedidoVentaManager:	

	error = None
	def __init__(self,idUsuario = None):
		self.__pedidoVenta = PedidoVenta()
		self.__pedidoVenta.listadoPedidoVentaPosicion = []
		if idUsuario != None:
			self.__cliente = Cliente.objects.get(usuario_id = idUsuario)
			self.__pedidoVenta.cliente = self.__cliente
			self.__pedidoVenta.idUsuarioCreacion = idUsuario
		self.error = ''

	# Agrega posiciones al Pedido Venta
	def add_posicion(self,saldoInventario,cantidad):
		costoTotal = saldoInventario.precioVentaUnitario
		if saldoInventario.precioOferta != None and saldoInventario.precioOferta > 0:
			costoTotal = saldoInventario.precioOferta
		self.__pedidoVenta.listadoPedidoVentaPosicion.append(PedidoVentaPosicion(producto = saldoInventario.producto,
																				 proveedor = saldoInventario.proveedor,
									   											 cantidad = cantidad,
									   											 costoTotal = costoTotal))
	#@transaction.atomic
	def save(self):
		transaction.set_autocommit(False)
		try:
			if len(self.__pedidoVenta.listadoPedidoVentaPosicion) is 0:
				raise Exception("El pedido no tiene posiciones!")
			# Se consulta el estado  01 -  Solicitado
			estadoPedidoVenta = EstadoPedidoVenta.objects.get(codigo = '01')
			self.__pedidoVenta.cliente = self.__cliente
			self.__pedidoVenta.estadoPedidoVenta = estadoPedidoVenta
			# Se consulta el rango numero pedido que este activo
			rangoNumeropedidoVenta = RangoNumeroPedidoVenta.objects.get(estado = True)
			if rangoNumeropedidoVenta.numeroActual > rangoNumeropedidoVenta.numeroHasta:
				raise Exception("No hay rango disponible para el pedido a generar")
			self.__pedidoVenta.numeroPedido = rangoNumeropedidoVenta.numeroActual
			# Se actualiza el numeroActual del rango numero pedido compra
			rangoNumeropedidoVenta.numeroActual +=1
			rangoNumeropedidoVenta.save()

			# Se guarda la cabecera del pedido
			self.__pedidoVenta.save()
		except Exception as e:
			transaction.rollback()
			self.error = e
			return False
		else: 
			transaction.commit()
		finally:
			transaction.set_autocommit(True)
		return True

	def get_pedidoVenta(self):
		return self.__pedidoVenta
		
	def get_numero_pedido(self):
		return self.__pedidoVenta.numeroPedido

	def guardar_posicion_venta_compra(self,pedidoVentaPosicion,pedidoCompraPoscion,cantidad):
		try:
			poscionVentaCompra = PosicionVentaCompra(pedidoVentaPosicion = pedidoVentaPosicion,
													 pedidoCompraPosicion = pedidoCompraPoscion,
													 cantidad = cantidad)
			poscionVentaCompra.save()
			return True
		except Exception as e:
			raise Exception(e)
			return False

	def autorizar_pedido(self,idPedidoVenta,idEstadoPedidoVenta,user):
		transaction.set_autocommit(False)
		listadoPosicionVentaCompra = []
		try:

			self.__pedidoVenta =  PedidoVenta.objects.get(pk=idPedidoVenta)
			#  Se cambia el estado al pedido venta
			self.__pedidoVenta.estadoPedidoVenta = EstadoPedidoVenta.objects.get(pk=idEstadoPedidoVenta)
			# Se guarda la fecha de autorización
			self.__pedidoVenta.fechaAutorizacion = datetime.now()
			# Método PEPS
			# Se consultan las posiciones de la venta que no esten Canceladas
			for posicionVenta in PedidoVentaPosicion.objects.filter(pedidoVenta = self.__pedidoVenta,cancelado = False):
				# Se consultan las posiciones del movimiento de entrada que tengan cantidad disponibles para realizar la salida
				listadoMovimientoInventarioPosicionCompra = MovimientoInventarioPosicion.objects.filter(producto = posicionVenta.producto_id,proveedor = posicionVenta.proveedor_id,
																									    entradaSalida = 1,cantidad__gt = 0).order_by('idMovimientoInventarioPosicion')
				# Se valida que halla movimiento para realizar la salida por el método PEPS
				if posicionVenta.cantidad > sum(p.cantidad for p in listadoMovimientoInventarioPosicionCompra):
					raise Exception("No existe movimiento para realizar la salida por el Método PEPS. Realize un pedido de Compra")
				
				cantidad = posicionVenta.cantidad
				cantidadPosicionVentaCompra = 0
				for posicionMovimientoCompra in listadoMovimientoInventarioPosicionCompra:
					if cantidad <= 0:
						break
					# Se consulta la posicion del pedido compra
					posicionCompra = PedidoCompraPosicion.objects.get(pedidoCompra=posicionMovimientoCompra.movimientoInventario.pedidoCompra_id,
																	  producto = posicionMovimientoCompra.producto_id)

					if cantidad <= posicionMovimientoCompra.cantidad:
						posicionMovimientoCompra.cantidad -= cantidad
						cantidadPosicionVentaCompra = cantidad
						cantidad = 0
					else:
						cantidad -= posicionMovimientoCompra.cantidad
						cantidadPosicionVentaCompra = posicionMovimientoCompra.cantidad
						posicionMovimientoCompra.cantidad = 0
					# Se guarda el movimiento inventario posicion de compra (ajustando el campo cantidad)
					posicionMovimientoCompra.save()
					# Se agrega la posicionVentacompra al listado
					if not self.guardar_posicion_venta_compra(posicionVenta,posicionCompra,cantidadPosicionVentaCompra):
						raise Exception("No se logro guardar la posicion venta compra")
				# Se guarda las ventas de los productos
				review = ProductoReview(producto = posicionVenta.producto,numeroVista = 0,numeroVenta = posicionVenta.cantidad)
				review.save()
			# Se modifica el pedido venta
			self.__pedidoVenta.save()
			# Se guarda el movimiento de Inventario
			movimientoInventario = MovimientoInventario(pedidoVenta = self.__pedidoVenta,idUsuarioCreacion=user.pk)
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