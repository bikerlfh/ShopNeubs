from datetime import datetime
from decimal import *

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.db.models import Q
from easy_thumbnails.signal_handlers import generate_aliases
from easy_thumbnails.signals import saved_file
from filer.fields.image import FilerImageField

from compras.models import PedidoCompra, PedidoCompraPosicion
from ventas.models import PedidoVenta, PedidoVentaPosicion

saved_file.connect(generate_aliases)


# Categoria
class Categoria(models.Model):
	idCategoria = models.AutoField(primary_key = True)
	categoriaPadre = models.ForeignKey("Categoria",db_column = 'idCategoriaPadre',blank = True,null = True,on_delete= models.CASCADE,verbose_name = 'Categoría Padre')
	codigo = models.CharField(max_length = 5, unique = True)
	descripcion = models.CharField(max_length = 50)
	estado = models.BooleanField(default=True)

	def __str__(self):
		if self.categoriaPadre != None:
			return '%s - %s (%s)' % (self.codigo , self.descripcion,self.categoriaPadre.descripcion)
		return '%s - %s' % (self.codigo , self.descripcion)

	class Meta:
		db_table = 'Categoria'
		verbose_name = 'Categoría'
		verbose_name_plural = 'Categorías'

# class MarcaManager(models.Manager):
#     def get_queryset(self):
#     	# Se excluye la marca '36 - Sin Marca' 
#         return super(MarcaManager, self).get_queryset().exclude(codigo = '36')

# Marca
class Marca(models.Model):
	idMarca = models.AutoField(primary_key = True)
	codigo = models.CharField(max_length = 5,unique = True)
	descripcion = models.CharField(max_length = 20)

	#objects = MarcaManager()
	def __str__(self):
		return '%s - %s' % (self.codigo , self.descripcion)

	class Meta:
		db_table = 'Marca'

class ProductoImagen(models.Model):
	idProductoImagen = models.BigAutoField(primary_key = True)
	producto  = models.ForeignKey("Producto",null=False, blank=False,db_column='idProducto')
	imagen = FilerImageField(null=False, blank=False)
	order = models.SmallIntegerField(default=0,blank=False,null=False)

	def __str__(self):
		return '%s - %s' % (self.producto ,str(self.imagen))

	def save(self, *args, **kwargs):
		if self.idProductoImagen is None:
			ordenamiento = ProductoImagen.objects.filter(producto = self.producto_id).aggregate(Max('order'))
			if ordenamiento['order__max'] == None:
				self.order = 0
			else:
				self.order = ordenamiento['order__max'] +1
		super(ProductoImagen, self).save(*args, **kwargs)

	class Meta:
		db_table = "ProductoImagen"
		verbose_name = "Producto Imagen"
		verbose_name_plural = "Producto Imagenes"
		unique_together = (("producto","imagen"),)

# Producto
class Producto(models.Model):
	idProducto = models.BigAutoField(primary_key = True)
	categoria = models.ForeignKey('Categoria',db_column = 'idCategoria',on_delete = models.PROTECT)
	marca = models.ForeignKey("Marca",db_column = "idMarca", on_delete = models.PROTECT)
	numeroProducto = models.BigIntegerField(verbose_name = 'Número Producto', unique = True)
	nombre = models.CharField(max_length=150)
	referencia = models.CharField(max_length=50,null=True,blank=True)
	descripcion = models.TextField(max_length=3000,null= True,blank = True)
	especificacion = models.TextField(max_length=3000, null = True,blank = True)
	urldescripcion = models.URLField(max_length=200, blank = True,null = True,verbose_name='Url')

	# Retorna la imagen principal del producto
	def imagen(self):
		try:
			productoImagen = ProductoImagen.objects.get(producto = self.idProducto,order = 0)
			return productoImagen.imagen
		except ProductoImagen.DoesNotExist:
			return None

	# Retorna un listado con las imagenes del producto
	def imagenes(self):
		lista_imagenes = []
		try:
			for producto_imagen in ProductoImagen.objects.filter(producto = self.idProducto).order_by('order'):
				lista_imagenes.append(producto_imagen.imagen)
		except ProductoImagen.DoesNotExist:
			pass
		return lista_imagenes

	def natural_key(self):
		return ((str(self.numeroProducto) + " - " + self.nombre))

	def __str__(self):
		return '%s - %s' % (str(self.numeroProducto),self.nombre)

	def save(self, *args, **kwargs):
		if self.idProducto is None or self.idProducto <= 0:
			numeroProducto = Producto.objects.all().aggregate(Max('numeroProducto'))
			if numeroProducto['numeroProducto__max'] == None:
				self.numeroProducto = 1
			else:
				self.numeroProducto = numeroProducto['numeroProducto__max'] +1
		super(Producto, self).save(*args, **kwargs)

	class Meta:
		db_table = "Producto"


# SaldoInventario
class SaldoInventarioManager(models.Manager):
	def filter(self,*args,**kwargs):
		# Se filtran los saldos inventarios que esten activos y que tengan cantidades
		return super(SaldoInventarioManager,self).filter(*args,**kwargs).filter(cantidad__gt=0)

	# Filtra el saldo inventario (SA)
	# Si en el resultado hay mas de un SA con el mismo producto
	# Solo deja el SA con el menor precio de venta
	def filter_products(self,*args,**kwargs):
		# Se consulta el saldo inventario ordenandolo por precioVentaUnitario (para mostrar siempre el de menor precio)
		listado_saldo_inventario = self.filter(*args,**kwargs).order_by('precioVentaUnitario')
		listado_pk_exclude = []
		for sa in listado_saldo_inventario:
			# Si existe mas de un saldo inventario con el mismo producto
			if listado_saldo_inventario.filter(producto_id = sa.producto_id).count()>1 and not sa.pk in listado_pk_exclude:

				""" Si el saldo inventario actual esta con estado False o
				    si existe un SA con el mismo producto y con un precioOferta menor al precioVentaUnitario, se debe excluir
				"""
				menorPrecio = sa.precioVentaUnitario
				if sa.precioOferta != None and sa.precioOferta > 0:
					menorPrecio = sa.precioOferta
				if not sa.estado or listado_saldo_inventario.filter(producto_id = sa.producto_id,
																    precioOferta__gt = 0,
																    precioOferta__lt = menorPrecio,
																    estado=True).exclude(pk=sa.pk).exists():
					listado_pk_exclude.append(sa.pk)
				else:
					# Se filtran los saldos inventarios a excluir (dejando el actual en la lista)
					for exclude in listado_saldo_inventario.filter(producto_id = sa.producto_id).exclude(pk=sa.pk).values_list('pk',flat = True):
						listado_pk_exclude.append(exclude)

		return listado_saldo_inventario.exclude(pk__in = listado_pk_exclude)


class Plataforma(models.Model):
	idPlataforma = models.AutoField(primary_key = True)
	codigo = models.CharField(max_length=2)
	descripcion = models.CharField(max_length=25)

	def __str__(self):
		return '%s - %s' % (self.codigo,self.descripcion)

	class Meta:
			db_table = "Plataforma"


class SaldoInventario(models.Model):
	idSaldoInventario = models.BigAutoField(primary_key = True)
	producto = models.ForeignKey("Producto",db_column = 'idProducto', on_delete = models.PROTECT)
	proveedor = models.ForeignKey("tercero.Proveedor",db_column = 'idProveedor', on_delete = models.PROTECT)
	garantia = models.ForeignKey("Garantia",db_column = 'idGarantia',on_delete = models.PROTECT, blank = True,null = True)
	referenciaProveedor = models.CharField(max_length=254,null= True,blank = True,verbose_name='Referencia Proveedor')
	cantidad = models.IntegerField()
	costoTotal = models.DecimalField(max_digits=10, decimal_places=2,verbose_name = 'Costo Total')
	precioCompraUnitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name = 'Precio Compra Unitario',default=0)
	precioVentaUnitario = models.DecimalField(max_digits=10, decimal_places=2,verbose_name = 'Precio venta Unitario')
	precioOferta = models.DecimalField(max_digits=10,decimal_places=2, null=True,blank = True, verbose_name = 'Precio Oferta')
	# si es un software se debe escoger las plataformas (windows, Steam, etc..)
	plataformas = models.ManyToManyField(Plataforma,blank=True)
	estado = models.BooleanField(default = True)
	usuarioCreacion = models.ForeignKey(User,db_column ='idUsuarioCreacion',on_delete = models.PROTECT)
	fechaCreacion = models.DateTimeField(auto_now_add = True,verbose_name = 'Fecha Creación')

	objects = SaldoInventarioManager()
	def __str__(self):
		return '%s (%s)' % (self.producto,self.proveedor)

	def save(self, *args, **kwargs):

		if self.cantidad == 0:
			self.costoTotal = 0
			self.estado = False
		# Porcentaje Ganancia solo valido cuando la accion es guardar
		# y el precioVentaUnitario es <= 0
		if self.idSaldoInventario is None and self.precioVentaUnitario <= 0:
			try:
				# Se consulta el porcentajeGanancia por idProducto o idCategoria
				porcentajeGanancia = PorcentajeGanancia.objects.filter(Q(producto = self.producto_id) | Q(categoria = self.producto.categoria_id)).order_by('producto')
				if len(porcentajeGanancia) > 0:
					porcentajeGanancia = porcentajeGanancia[0]
				else:
					raise PorcentajeGanancia.DoesNotExist
			except PorcentajeGanancia.DoesNotExist:
				# Se consulta el procentaje de la ganancia general
				porcentajeGanancia = PorcentajeGanancia.objects.get(producto = None,categoria=None)
			if self.cantidad > 0:
				self.precioVentaUnitario = Decimal(self.costoTotal/self.cantidad) * (1 + porcentajeGanancia.porcentaje/100)
			else:
				self.costoTotal = 0
				self.precioVentaUnitario = 0
		super(SaldoInventario, self).save(*args, **kwargs)
		# Se guarda el historico de la promocion
		if self.precioOferta != None and self.precioOferta > 0:
			if Promocion.objects.filter(saldoInventario = self,estado = True).exists():
				promocion = Promocion.objects.get(saldoInventario = self,estado = True)
				# Si se cambia la promocion, se debe deshactivar la que ya habia y crear otra
				if promocion.precioOferta != self.precioOferta:
					promocion.estado = False
					promocion.save()
					promocionNueva = Promocion(saldoInventario = self,precioOferta = self.precioOferta,estado = True)
					promocionNueva.save()
			else:
				promocion = Promocion(saldoInventario = self,precioOferta = self.precioOferta,estado = True)
				promocion.save()
		else:
			# Se deshabilita la promocion activa
			if Promocion.objects.filter(saldoInventario = self,estado = True).exists():
				promocion = Promocion.objects.get(saldoInventario = self,estado = True)
				promocion.estado = False
				promocion.save()
	class Meta:
		db_table = 'SaldoInventario'
		verbose_name = 'Saldo Inventario'
		verbose_name_plural = 'Saldo Inventario'
		unique_together = (("producto", "proveedor"),)
		permissions = (
			("consultar_saldo_inventario","Puede consultar los saldos de inventario"),
		)
		#managed = False

class Garantia(models.Model):
	idGarantia = models.AutoField(primary_key = True)
	codigo = models.CharField(max_length = 2,unique = True)
	descripcion = models.CharField(max_length = 150)

	def __str__(self):
		return '%s - %s' % (self.codigo,self.descripcion)

	class Meta:
		db_table = 'Garantia'


class PromocionManager(models.Manager):
	def filter(self,*args,**kwargs):
		# Se filtran las promociones que esten activas
		return super(PromocionManager,self).filter(*args,**kwargs).filter(fechaFin__isnull=True,estado = True)

	# Filtra las promociones
	# Si el filtro trae una promoción, pero existe otra con el mismo producto y de menor valor,
	# visualiza ésta ultima
	def filter_promocion(self,*args,**kwargs):
		# Se consulta el saldo inventario ordenandolo por precioVentaUnitario (para mostrar siempre el de menor precio)
		listado_promocion = self.filter(*args,**kwargs)
		listado_pk = []
		listado_pk_exclude = []
		for p in listado_promocion:
			if Promocion.objects.filter(saldoInventario__producto_id = p.saldoInventario.producto_id,
										fechaFin__isnull=True,estado=True,
										precioOferta__lt=p.precioOferta).exclude(pk=p.pk).exists():
				listado_pk.append(Promocion.objects.filter(saldoInventario__producto_id = p.saldoInventario.producto_id,
															fechaFin__isnull=True,estado=True,
															precioOferta__lt=p.precioOferta).exclude(pk=p.pk)[0].pk)
			else:
				listado_pk.append(p.pk)
		return Promocion.objects.filter(pk__in=listado_pk)

class Promocion(models.Model):
	idPromocion = models.BigAutoField(primary_key=True)
	saldoInventario = models.ForeignKey("SaldoInventario",db_column='idSaldoInventario',on_delete = models.PROTECT,verbose_name='Saldo Inventario')
	precioVenta = models.DecimalField(max_digits = 18, decimal_places = 2,verbose_name = 'Precio Venta')
	precioOferta = models.DecimalField(max_digits = 18, decimal_places = 2,verbose_name='Precio Oferta')
	fechaInicio = models.DateTimeField(auto_now_add = True,verbose_name = 'Fecha Inicio')
	fechaFin = models.DateTimeField(null = True,blank = True,verbose_name = 'Fecha Fin')
	estado = models.BooleanField(default = True)

	objects = PromocionManager()
	def __str__(self):
		return '%s'% self.saldoInventario
	def save(self,*args,**kwargs):
		self.precioVenta = self.saldoInventario.precioVentaUnitario
		# Se deshabilita la promocion que este activa
		if self.estado == True:
			try:
				listadoPromocion = Promocion.objects.filter(saldoInventario = self.saldoInventario, estado = True).exclude(pk = self.pk)
				for promo in listadoPromocion:
					promo.estado = False
					promo.save()
			except Promocion.DoesNotExist:
				pass
		else:
			self.fechaFin = datetime.now()
		super(Promocion,self).save(*args,**kwargs)

	class Meta:
		db_table = "Promocion"
		verbose_name = "Promoción"
		verbose_name_plural = "Promociones"

# MovimientoInventario
class MovimientoInventario(models.Model):
	idMovimientoInventario = models.BigAutoField(primary_key = True)
	pedidoVenta = models.ForeignKey("ventas.PedidoVenta",db_column = 'idPedidoVenta', on_delete = models.PROTECT, blank=True,null=True)
	pedidoCompra = models.ForeignKey("compras.PedidoCompra",db_column = 'idPedidoCompra', on_delete = models.PROTECT, blank=True,null=True)
	fecha = models.DateTimeField(auto_now_add = True)
	idUsuarioCreacion = models.IntegerField()

	def __str__(self):
		return '%s %s %s' % (self.pedidoVenta,self.pedidoCompra,str(self.fecha))

	class Meta:
		db_table = 'MovimientoInventario'
		#managed = False

	def save(self, *args, **kwargs):
		# Se obtiene la session del usuario
		# session = Session.objects.filter().last()
		# self.idUsuarioCreacion = int(session.get_decoded().get('_auth_user_id'))

		super(MovimientoInventario, self).save(*args, **kwargs)

		# Si el pedido es de compras se realiza la salida
		if self.pedidoCompra != None:
			for posicion in PedidoCompraPosicion.objects.filter(pedidoCompra = self.pedidoCompra):
				MovimientoInventarioPosicion(movimientoInventario = self,
											 producto = posicion.producto,
											 proveedor = self.pedidoCompra.proveedor,
											 entradaSalida = 1,
											 cantidadMovimiento = posicion.cantidad,
											 cantidad = posicion.cantidad,
											 valorMovimiento=posicion.costoTotal).save()
		# Si el pedido es de venta se realiza la salida
		elif self.pedidoVenta != None:
			for posicion in PedidoVentaPosicion.objects.filter(pedidoVenta = self.pedidoVenta):
				MovimientoInventarioPosicion(movimientoInventario = self,
											 producto = posicion.producto,
											 proveedor = posicion.proveedor,
											 entradaSalida = 0,
											 cantidadMovimiento = posicion.cantidad,
											 valorMovimiento=posicion.costoTotal).save()

# MovimientoInventarioPosicion
class MovimientoInventarioPosicion(models.Model):
	idMovimientoInventarioPosicion = models.BigAutoField(primary_key = True)
	movimientoInventario = models.ForeignKey("MovimientoInventario",db_column = 'idMovimientoInventario',on_delete = models.PROTECT)
	producto = models.ForeignKey("Producto",db_column = 'idProducto', on_delete = models.PROTECT)
	proveedor = models.ForeignKey("tercero.Proveedor",db_column = 'idProveedor', on_delete = models.PROTECT)
	entradaSalida = models.BooleanField()
	cantidadMovimiento = models.IntegerField()
	valorMovimiento = models.DecimalField(max_digits = 10, decimal_places = 2)
	# Solo se llena cuando es un movimiento de entrada (compra)
	# Guarda la cantidad restante que tiene aún la compra
	cantidad = models.IntegerField(blank = True, null = True)

	def __str__(self):
		return '%s %s %s Entrada: %s' % (self.movimientoInventario,self.producto,self.proveedor,self.entradaSalida)

	def save(self, *args, **kwargs):
		# Si se va a guardar el movimiento inventario posicion, ajusta o se genera el Saldo Inventario
		if self.idMovimientoInventarioPosicion is None or self.idMovimientoInventarioPosicion <=0:
			try:
				saldoInventario = SaldoInventario.objects.get(proveedor = self.proveedor_id,producto = self.producto_id)
				# si es una entrada se suma al inventario de lo contrario se resta
				if self.entradaSalida == 1:
					saldoInventario.cantidad += self.cantidadMovimiento
					saldoInventario.costoTotal += self.valorMovimiento
				else:
					costoUnitario = saldoInventario.costoTotal / saldoInventario.cantidad
					saldoInventario.cantidad -= self.cantidadMovimiento
					saldoInventario.costoTotal -= saldoInventario.cantidad * costoUnitario
				saldoInventario.save()
			except SaldoInventario.DoesNotExist:
				# si no existe el inventario y se va a realizar una salida
				# se genera una excepción
				if self.entradaSalida == 0:
					raise Exception("La salida del inventario no se puede realizar. No existe inventario!")
				# se crea el saldoInventario
				saldoInventario = SaldoInventario(producto = self.producto,proveedor = self.proveedor, cantidad = self.cantidad, costoTotal = self.valorMovimiento)
				saldoInventario.save()

		super(MovimientoInventarioPosicion, self).save(*args, **kwargs)

	class Meta:
		db_table = 'MovimientoInventarioPosicion'
		#managed = False

# Procentaje Ganancia
class PorcentajeGanancia(models.Model):
	idPorcentajeGanancia = models.BigAutoField(primary_key = True)
	producto = models.ForeignKey("inventario.Producto",db_column = 'idProducto',blank = True, null=True,on_delete = models.PROTECT)
	categoria = models.ForeignKey("inventario.Categoria",db_column = 'idCategoria',blank = True, null=True,on_delete = models.PROTECT)
	porcentaje = models.DecimalField(max_digits = 4, decimal_places = 2)

	def __str__(self):
		return '%s %s %s' % (self.producto,self.categoria,str(self.porcentaje))

	class Meta:
		db_table = 'PorcentajeGanancia'

class ProductoReview(models.Model):
	idProductoReview = models.BigAutoField(primary_key = True)
	producto = models.ForeignKey("Producto",db_column = 'idProducto',on_delete = models.PROTECT)
	numeroVista = models.BigIntegerField()
	numeroVenta = models.BigIntegerField()

	def __str__(self):
		return 'Producto:%s  vistas: %s ventas: %s' % (self.producto,str(self.numeroVista),str(self.numeroVenta))

	def save(self, *args, **kwargs):
		if self.idProductoReview == None:
			try:
				review = ProductoReview.objects.get(producto = self.producto_id)
				if review != None:
					review.numeroVista += self.numeroVista
					review.numeroVenta += self.numeroVenta
					review.save()
					return True
			except ProductoReview.DoesNotExist:
				pass
		super(ProductoReview, self).save(*args, **kwargs)
	class Meta:
		db_table = 'ProductoReview'
