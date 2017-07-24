from django.db import models


class Pais(models.Model):
	idPais = models.AutoField(primary_key=True)
	codigo = models.CharField(blank=False, max_length=5, unique=True)
	descripcion = models.CharField(blank=False, max_length=20)

	class Meta:
		db_table = 'Pais'
		verbose_name_plural = 'Paises'

	def __str__(self):
		return '%s - %s' % (self.codigo, self.descripcion)


class Departamento(models.Model):
	idDepartamento = models.BigAutoField(primary_key=True)
	pais = models.ForeignKey('Pais', db_column='idPais', on_delete=models.PROTECT, )
	codigo = models.CharField(blank=False, max_length=5, unique=True)
	descripcion = models.CharField(blank=False, max_length=20)

	class Meta:
		db_table = 'Departamento'
		unique_together = (("pais", "codigo"),)

	def __str__(self):
		return '%s - %s' % (self.codigo, self.descripcion)


class Municipio(models.Model):
	idMunicipio = models.BigAutoField(primary_key=True)
	departamento = models.ForeignKey('Departamento', db_column='idDepartamento', on_delete=models.PROTECT, )
	codigo = models.CharField(blank=False, max_length=5)
	descripcion = models.CharField(blank=False, max_length=30)

	class Meta:
		db_table = 'Municipio'
		unique_together = (("departamento", "codigo"),)

	def __str__(self):
		return '%s - %s' % (self.codigo, self.descripcion)