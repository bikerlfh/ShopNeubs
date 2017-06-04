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


def generate_thumbnails(model, pk, field):
    instance = model._default_manager.get(pk=pk)
    fieldfile = getattr(instance, field)
    generate_aliases_carousel(fieldfile)


class ApiTabla(models.Model):
	idApiTabla = models.AutoField(primary_key=True)
	codigo = models.CharField(max_length=2,null=False,blank = False)
	descripcion = models.CharField(max_length = 20,null=False,blank=False)

	def __str__(self):
		return '%s - %s' % (self.codigo,self.descripcion)

	class Meta:
		db_table = 'ApiTabla'
		verbose_name = 'API Tabla'
		verbose_name_plural = 'API Tablas'

class ApiSincronizacion(models.Model):
	idApiSincronizacion = models.AutoField(primary_key = True)
	tabla = models.ForeignKey("ApiTabla",db_column = 'idApiTabla',blank = True,null = True,on_delete= models.CASCADE,verbose_name = 'API Tabla')
	fecha = models.DateTimeField(blank = False,null = False,verbose_name = 'Fecha Sincronización')
	ultima = models.BooleanField(default = True,blank=False,null=False)

	def __str__(self):
		return '(%s) %s' % (str(self.fecha),self.tabla)

	class Meta:
		db_table = 'ApiSincronizacion'
		verbose_name = 'API Sincronización'
		verbose_name_plural = verbose_name

	def save(self,*args,**kwargs):
		if self.idApiSincronizacion == 0:
			apiSincronizacion = ApiSincronizacion.objects.filter(tabla_id = self.tabla_id, ultima = True)
			if apiSincronizacion.exists():
				apiSincronizacion.ultima = False
				apiSincronizacion.save()
		super(ApiSincronizacion,self).save(*args,**kwargs)
