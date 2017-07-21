from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from filer.fields.image import FilerImageField


class Carousel(models.Model):
	idCarousel = models.AutoField(primary_key = True)
	imagen = FilerImageField(null=False, blank=False)
	url = models.CharField(max_length = 256,null=True,blank=True,default = None)
	order = models.SmallIntegerField(default=0,blank=False,null=False)
	estado  = models.BooleanField(default = True)

	def __str__(self):
		return '%s (%s)' % (self.imagen,str(self.order))

	def save(self, *args, **kwargs):
		if self.idCarousel is None and self.estado is True:
			try:
				carousel = Carousel.objects.get(estado = self.estado,order = self.order)
				carousel.estado = False
				carousel.save()
			except Carousel.DoesNotExist:
				pass
		super(Carousel, self).save(*args, **kwargs)


#def generate_thumbnails(model, pk, field):
#    instance = model._default_manager.get(pk=pk)
#    fieldfile = getattr(instance, field)


class ApiTabla(models.Model):
	idApiTabla = models.AutoField(primary_key=True)
	codigo = models.CharField(max_length=2, null=False, blank=False)
	descripcion = models.CharField(max_length=20, null=False, blank=False)

	def __str__(self):
		return '%s - %s' % (self.codigo,self.descripcion)

	class Meta:
		db_table = 'ApiTabla'
		verbose_name = 'API Tabla'
		verbose_name_plural = 'API Tablas'


class ApiSincronizacion(models.Model):
	idApiSincronizacion = models.AutoField(primary_key = True)
	tabla = models.ForeignKey("ApiTabla",db_column = 'idApiTabla',blank = True,null = True,on_delete= models.CASCADE,verbose_name = 'API Tabla')
	fecha = models.DateTimeField(auto_now_add = True,blank = False,null = False,verbose_name = 'Fecha Sincronización')
	ultima = models.BooleanField(default = True,blank=False,null=False)

	def __str__(self):
		return '(%s) %s' % (str(self.fecha),self.tabla)

	class Meta:
		db_table = 'ApiSincronizacion'
		verbose_name = 'API Sincronización'
		verbose_name_plural = verbose_name

	def save(self,*args,**kwargs):
		if self.idApiSincronizacion is None:
			try:
				apiSincronizacion = ApiSincronizacion.objects.get(tabla = self.tabla, ultima = True)
				apiSincronizacion.ultima = False
				apiSincronizacion.save()
			except Exception as e:
				pass
		super(ApiSincronizacion,self).save(*args,**kwargs)


# banner para los dispositivos moviles
class ApiBanner(models.Model):
	idApiBanner = models.AutoField(primary_key=True)
	imagen = FilerImageField(null=False, blank=False)
	isClickable = models.BooleanField(default=False,blank=False,null = False)
	saldoInventario = models.ForeignKey("inventario.SaldoInventario",db_column = 'idSaldoInventario',blank=True,null=True,on_delete=models.CASCADE,verbose_name = 'Saldo Inventario')
	urlRequest = models.CharField(max_length = 256,blank = True,null=True)
	fecha = models.DateTimeField(auto_now_add = True,blank = False,null=False)
	estado = models.BooleanField(default = True,blank=False,null=False)

	def __str__(self):
		return 'imagen (%s) fecha %s' % (self.imagen,str(self.fecha))

	class Meta:
		db_table = 'ApiBanner'
		verbose_name = 'Api Banner'
		verbose_name_plural = verbose_name

	def save(self,*args,**kwargs):
		self.guardar_apiSincronizacion()
		super(ApiBanner,self).save(*args,**kwargs)

	def delete(self, using=None, keep_parents=False):
		self.guardar_apiSincronizacion()
		#self.imagen.delete()
		super(ApiBanner, self).delete(using=using, keep_parents=keep_parents)

	# def delete(self, *args, **kwargs):
	# 	# se elimina la imagen
	# 	#self.imagen.delete()
	# 	self.guardar_apiSincronizacion()
	# 	super(ApiBanner, self).delete(*args, **kwargs)

	# Guarda un registro en tabla apiSincronización para indicar
	# la actualización de los datos de ésta tabla
	def guardar_apiSincronizacion(self):
		try:
			# se consulta la ApiTabla (ApiBanner "codigo = 04")
			apiTabla = ApiTabla.objects.get(codigo = '04')
			# se agrega una nueva apiSincronizacion
			apiSincronizacion = ApiSincronizacion(tabla = apiTabla,ultima = True)
			apiSincronizacion.save()
		except Exception as e:
			pass


	#def generate_thumbnails(model, pk, field):
	#   instance = model._default_manager.get(pk=pk)
	#   fieldfile = getattr(instance, field)
	#   generate_aliases_apibanner(fieldfile)

class ApiSection(models.Model):
	idApiSection = models.AutoField(primary_key = True)
	title = models.CharField(max_length = 25,blank = False,null	= False)
	subTitle = models.CharField(max_length = 50,blank = True,null	= True)
	urlRequestProductos = models.CharField(max_length = 256,blank = False,null = False)
	urlRequestMas = models.CharField(max_length = 256,blank = True,null	= True)
	orden = models.PositiveSmallIntegerField(default = 1,blank = False, null = False)
	estado = models.BooleanField(default = True,blank=False,null=False)

	def __str__(self):
		return '%s - %s' % (self.title, self.subTitle)

	class Meta:
		db_table = 'ApiSection'
		verbose_name = 'Api Section'
		verbose_name_plural = 'Api Sections'

	def save(self,*args,**kwargs):
		self.guardar_apiSincronizacion()
		super(ApiSection,self).save(*args,**kwargs)
		
	# Guarda un registro en tabla apiSincronización para indicar
	# la actualización de los datos de ésta tabla
	def guardar_apiSincronizacion(self):
		try:
			# se consulta la ApiSection (ApiBanner "codigo = 05")
			apiTabla = ApiTabla.objects.get(codigo = '05')
			# se agrega una nueva apiSincronizacion
			apiSincronizacion = ApiSincronizacion(tabla=apiTabla, ultima=True)
			apiSincronizacion.save()
		except Exception as e:
			pass


# clase para almacenar los archivos de modificación de precios
class ArchivoModificacionPrecio(models.Model):
		file = models.FileField(verbose_name="Archivo", upload_to="precios/", storage=FileSystemStorage(location=settings.LOCAL_FILES_UPLOAD_URL), blank=False, null=False)
		proveedor = models.OneToOneField("tercero.Proveedor")
		fecha = models.DateTimeField(auto_now_add=True)
		ultimo = models.BooleanField(default=True, blank=False)

		def __str__(self):
				return "%s - %s " % (self.proveedor,self.file.name)

		def delete(self, using=None, keep_parents=False):
				self.file.delete()
				super(ArchivoModificacionPrecio,self).delete(using=using, keep_parents=keep_parents)

		class Meta:
				db_table = "ArchivoModificacionPrecio"
				verbose_name = "Archivo modificación precios"
				verbose_name_plural = "Archivos modificación precios"






