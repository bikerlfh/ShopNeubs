from django.db import models
from filer.fields.file import FilerFileField


class EstadoPedidoVenta(models.Model):
	idEstadoPedidoVenta = models.AutoField(primary_key=True)
	codigo = models.CharField(max_length=2, unique=True)
	descripcion = models.CharField(max_length=25)

	def natural_key(self):
		return '%s - %s' % (self.codigo, self.descripcion)

	def __str__(self):
		return '%s - %s' % (self.codigo, self.descripcion)

	class Meta:
		db_table = 'EstadoPedidoVenta'
		verbose_name = "Estado Pedido Venta"
		verbose_name_plural = verbose_name


class RangoNumeroPedidoVenta(models.Model):
	idRangoNumeroPedidoVenta = models.AutoField(primary_key=True)
	codigo = models.CharField(max_length=2, unique=True)
	descripcion = models.CharField(max_length=15)
	numeroDesde = models.BigIntegerField(verbose_name="Número Desde")
	numeroHasta = models.BigIntegerField(verbose_name="Número Hasta")
	# Almacena el numero con el que se debe generar el pedido
	numeroActual = models.BigIntegerField(verbose_name="Número Actual")
	estado = models.BooleanField(default=True)

	def __str__(self):
		return 'N° desde: %s, N° hasta: %s, N° Actual: %s' % (str(self.numeroDesde), str(self.numeroHasta), str(self.numeroActual))

	def save(self, *args, **kwargs):
		if self.idRangoNumeroPedidoVenta is None:
			self.numeroActual = self.numeroDesde
		super(RangoNumeroPedidoVenta, self).save(*args, **kwargs)

	class Meta:
		db_table = 'RangoNumeroPedidoVenta'
		verbose_name = "Rango Número Pedido"
		verbose_name_plural = verbose_name


class PedidoVenta(models.Model):
	idPedidoVenta = models.BigAutoField(primary_key=True)
	cliente = models.ForeignKey("tercero.Cliente", db_column='idCliente', on_delete=models.PROTECT)
	estadoPedidoVenta = models.ForeignKey("EstadoPedidoVenta", db_column='idEstadoPedidoVenta', on_delete=models.PROTECT)
	numeroPedido = models.BigIntegerField(verbose_name='Número Pedido', unique=True)
	fecha = models.DateTimeField(auto_now_add=True)
	fechaAutorizacion = models.DateTimeField(null=True, blank=True, db_column='fechaAutorizacion')
	urlFactura = FilerFileField(blank=True, null=True, max_length=250, verbose_name='Url Factura')
	motivoCancelacionPedidoVenta = models.ForeignKey("MotivoCancelacionPedidoVenta",
													 db_column='idMotivoCancelacionPedidoVenta', blank=True, null=True,
													 default=None, on_delete=models.PROTECT,
													 verbose_name='Motivo Cancelación')
	idUsuarioCreacion = models.IntegerField()
	# listado de pedidos posicion
	listadoPedidoVentaPosicion = []

	# retorna el valor total del pedido
	def get_valor_total(self):
		return sum(
			posicion.costoTotal for posicion in PedidoVentaPosicion.objects.filter(pedidoVenta=self.idPedidoVenta))

	def get_cantidad_total(self):
		return sum(posicion.cantidad for posicion in PedidoVentaPosicion.objects.filter(pedidoVenta=self.idPedidoVenta))

	def __str__(self):
		return '%s - %s' % (str(self.numeroPedido), self.cliente)

	def save(self, *args, **kwargs):
		super(PedidoVenta, self).save(*args, **kwargs)
		if len(self.listadoPedidoVentaPosicion) > 0:
			for posicion in self.listadoPedidoVentaPosicion:
				posicion.pedidoVenta = self
				posicion.save()

	class Meta:
		db_table = 'PedidoVenta'
		permissions = (
			("autorizar_pedido", "Puede autorizar pedidos de venta"),
			("consultar_pedido", "Puede consultar los pedidos de venta"),
			("reportes", "Puede generar reportes"),
		)


class PedidoVentaPosicion(models.Model):
	idPedidoVentaPosicion = models.BigAutoField(primary_key=True)
	pedidoVenta = models.ForeignKey("PedidoVenta", db_column='idPedidoVenta', on_delete=models.PROTECT)
	producto = models.ForeignKey("inventario.Producto", db_column='idProducto', on_delete=models.PROTECT)
	proveedor = models.ForeignKey("tercero.Proveedor", db_column='idProveedor', on_delete=models.PROTECT)
	cantidad = models.IntegerField()
	costoTotal = models.DecimalField(db_column='costoTotal', max_digits=10, decimal_places=2)
	cancelado = models.BooleanField(default=False)
	motivoCancelacionPedidoVenta = models.ForeignKey("MotivoCancelacionPedidoVenta",
													 db_column='idMotivoCancelacionPedidoVenta', blank=True, null=True,
													 default=None, on_delete=models.PROTECT,
													 verbose_name='Motivo Cancelación')

	def save(self, *args, **kwargs):
		# Cuando no ha sido cancelado no se debe tener motivo de cancelación
		if not self.cancelado:
			self.motivoCancelacionPedidoVenta = None
		super(PedidoVentaPosicion, self).save(*args, **kwargs)

	def __str__(self):
		return '%s / %s / %s' % (self.pedidoVenta, self.producto, self.proveedor)

	class Meta:
		db_table = 'PedidoVentaPosicion'
		permissions = (
			("cancelar_pedido_venta_posicion", "Puede cancelar pedidos de venta"),
		)


class PosicionVentaCompra(models.Model):
	idPosicionVentacompra = models.BigAutoField(primary_key=True)
	pedidoVentaPosicion = models.ForeignKey("PedidoVentaPosicion", db_column='idPedidoVentaPosicion', on_delete=models.PROTECT)
	pedidoCompraPosicion = models.ForeignKey("compras.PedidoCompraPosicion", db_column='idPedidoCompraPosicion', on_delete=models.PROTECT)
	cantidad = models.IntegerField()

	def __str__(self):
		return '(%s) - (%s)' % (self.pedidoVentaPosicion, self.pedidoCompraPosicion)

	class Meta:
		db_table = 'PosicionVentaCompra'


class ParametroImpuesto(models.Model):
	idParametroImpuesto = models.AutoField(primary_key=True)
	codigo = models.CharField(max_length=5, unique=True)
	descripcion = models.CharField(max_length=20)
	porcentaje = models.DecimalField(max_digits=4, decimal_places=2)

	def __str__(self):
		return '%s %s %s' % (self.codigo, self.descripcion, str(self.porcentaje))

	class Meta:
		db_table = 'ParametroImpuesto'


class MotivoCancelacionPedidoVenta(models.Model):
	idMotivoCancelacionPedidoVenta = models.AutoField(primary_key=True)
	codigo = models.CharField(max_length=2, unique=True)
	descripcion = models.CharField(max_length=25)

	def __str__(self):
		return '%s - %s' % (self.codigo, self.descripcion)

	class Meta:
		db_table = 'MotivoCancelacionPedidoVenta'