from django.db import models
from filer.fields.image import FilerImageField

class Carousel(models.Model):
	idCarousel = models.AutoField(primary_key = True)
	imagen = FilerImageField(null=False, blank=False)
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