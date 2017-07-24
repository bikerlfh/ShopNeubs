from django.contrib.sessions.models import Session
from django.db import models
from filer.fields.file import FilerFileField


# Create your models here.

# EstadoPedidoCompra
class EstadoPedidoCompra(models.Model):
	idEstadoPedidoCompra = models.AutoField(primary_key = True)
	codigo = models.CharField(max_length = 2, unique = True)
	descripcion = models.CharField(max_length = 25)

	class Meta:
		db_table = 'EstadoPedidoCompra'
		verbose_name = "Estado Pedido Compra"
		verbose_name_plural = verbose_name

	def __str__(self):
		return '%s - %s' % (self.codigo,self.descripcion)


class RangoNumeroPedidoCompra(models.Model):
	idRangoNumeroPedidoCompra = models.AutoField(primary_key = True)
	codigo = models.CharField(max_length = 2,unique = True)
	descripcion = models.CharField(max_length = 15)
	numeroDesde = models.BigIntegerField(verbose_name = "Número Desde")
	numeroHasta = models.BigIntegerField(verbose_name = "Número Hasta")
	# Almacena el numero con el que se debe generar el pedido
	numeroActual = models.BigIntegerField(verbose_name = "Número Actual")
	estado = models.BooleanField(default = True)

	class Meta:
		db_table = 'RangoNumeroPedidoCompra'
		verbose_name = "Rango Número Pedido"
		verbose_name_plural = verbose_name

	def __str__(self):
		return 'N° desde: %s, N° hasta: %s, N° Actual: %s' % (str(self.numeroDesde),str(self.numeroHasta),str(self.numeroActual))

	def save(self, *args, **kwargs):
		if self.idRangoNumeroPedidoCompra is None:
			self.numeroActual = self.numeroDesde
		super(RangoNumeroPedidoCompra, self).save(*args, **kwargs)


# PedidoCompra
class PedidoCompra(models.Model):
	idPedidoCompra = models.BigAutoField(primary_key = True)
	proveedor = models.ForeignKey("tercero.Proveedor",db_column = 'idProveedor', on_delete = models.PROTECT)
	estadoPedidoCompra = models.ForeignKey(EstadoPedidoCompra,db_column = 'idEstadoPedidoCompra', on_delete = models.PROTECT,verbose_name = 'Estado Pedido')
	numeroPedido = models.BigIntegerField(db_column = 'numeroPedido',verbose_name = 'Número Pedido',unique = True)
	fecha = models.DateTimeField(auto_now_add = True)
	urlFactura = FilerFileField(blank = True,null = True,max_length=250,verbose_name = 'Url Factura')
	idUsuarioCreacion =  models.BigIntegerField()

	class Meta:
		db_table = 'PedidoCompra'
		permissions= (
			('solicitar_compra','Puede solicitar pedido de compra'),
			('consultar_pedido','Puede consultar el pedido de compra'),
		)

	def __str__(self):
		return '%s %s' % (str(self.numeroPedido),self.proveedor)

	# retorna el valor total del pedido
	def get_valor_total(self):
		return sum(posicion.costoTotal for posicion in PedidoCompraPosicion.objects.filter(pedidoCompra  = self.idPedidoCompra))
	def get_cantidad_total(self):
		return sum(posicion.cantidad for posicion in PedidoCompraPosicion.objects.filter(pedidoCompra  = self.idPedidoCompra))


# PedidoCompraPosicion
class PedidoCompraPosicion(models.Model):
	idPedidoCompraPosicion = models.BigAutoField(primary_key = True)
	pedidoCompra = models.ForeignKey("PedidoCompra",db_column = 'idPedidoCompra', on_delete = models.PROTECT)
	producto = models.ForeignKey("inventario.Producto",db_column = 'idProducto', on_delete = models.PROTECT)
	cantidad = models.IntegerField()
	costoTotal = models.DecimalField(db_column = 'costoTotal',max_digits=10, decimal_places=2)

	class Meta:
		db_table = 'PedidoCompraPosicion'
		#managed = False

	def __str__(self):
		return '%s - %s' % (self.pedidoCompra,self.producto)
	
	def natural_key(self):
		return 'N° %s - %s' % (self.pedidoCompra.numeroPedido,self.producto)