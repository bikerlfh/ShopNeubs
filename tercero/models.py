from django.contrib.auth.models import User
from django.db import models


# Create your models here.
# TipoDocumento
class TipoDocumento(models.Model):
	idTipoDocumento = models.AutoField(primary_key = True)	
	codigo = models.CharField(max_length = 3, unique = True)
	descripcion = models.CharField(max_length = 50)

	def __str__(self):
		return '%s - %s' % (self.codigo , self.descripcion)

	class Meta:
		db_table = 'TipoDocumento'
		verbose_name = "Tipo Documento"
		verbose_name_plural = verbose_name


# MetodoPago
class MetodoPago(models.Model):
	idMetodoPago = models.AutoField(primary_key = True)
	codigo = models.CharField(max_length = 2, unique = True)
	descripcion = models.CharField(max_length = 25)

	def __str__(self):
		return '%s - %s' % (self.codigo , self.descripcion)

	class Meta:
		db_table = 'MetodoPago'
		verbose_name = "Método Pago"
		verbose_name_plural = "Métodos de Pago"


# TipoCuenta
class TipoCuenta(models.Model):
	idTipoCuenta = models.AutoField(primary_key = True)
	codigo = models.CharField(max_length = 2, unique = True)
	descripcion = models.CharField(max_length = 10)

	def __str__(self):
		return '%s - %s' % (self.codigo , self.descripcion)

	class Meta:
		db_table = 'TipoCuenta'
		verbose_name = "Tipo Cuenta"
		verbose_name_plural = verbose_name

# Banco
class Banco(models.Model):
	idBanco = models.AutoField(primary_key = True)
	codigo = models.CharField(max_length = 2, unique = True)
	descripcion = models.CharField(max_length = 50)

	def __str__(self):
		return '%s - %s' % (self.codigo , self.descripcion)

	class Meta:
		db_table = 'Banco'

# DatoBasicoTercero
class DatoBasicoTercero(models.Model):
	idDatoBasicoTercero = models.BigAutoField(primary_key = True)
	tipoDocumento = models.ForeignKey("TipoDocumento",db_column = 'idTipoDocumento',on_delete = models.PROTECT,verbose_name = 'Tipo Documento')
	nit = models.BigIntegerField(unique = True)
	descripcion = models.CharField(max_length=150)
	primerNombre = models.CharField(max_length=15,blank = True, null = True,verbose_name = 'Primer Nombre')
	segundoNombre = models.CharField(max_length=15,blank = True, null = True,verbose_name = 'Segundo Nombre')
	primerApellido = models.CharField(max_length=15,blank = True, null = True,verbose_name = 'Primer Apellido')
	segundoApellido = models.CharField(max_length=15,blank = True, null = True,verbose_name = 'Segundo Apellido')
	direccion = models.CharField(max_length=50)
	telefono = models.CharField(max_length=50)

	def natural_key(self):
		return ((str(self.nit) + " - " + self.descripcion))

	def __str__(self):
		return '%s - %s' % (str(self.nit),self.descripcion)

	def save(self, *args, **kwargs):
		if self.tipoDocumento.codigo != 'NIT':
			self.descripcion = self.primerNombre + " " + self.segundoNombre + " " + self.primerApellido + " " + self.segundoApellido
		super(DatoBasicoTercero, self).save(*args, **kwargs)

	class Meta:
		db_table = 'DatoBasicoTercero'
		verbose_name = 'Tercero'
		verbose_name_plural = 'Terceros'

# Cliente
class Cliente(models.Model):
	idCliente = models.BigAutoField(primary_key = True)
	usuario = models.OneToOneField(User,db_column ='idUsuario',on_delete = models.PROTECT)
	datoBasicoTercero = models.OneToOneField("DatoBasicoTercero",db_column = 'idDatoBasicoTercero',on_delete = models.PROTECT,verbose_name = 'Tercero')
	municipio = models.ForeignKey("division_territorial.Municipio",db_column = 'idMunicipio', on_delete = models.PROTECT)
	correo = models.EmailField(max_length=150)

	def natural_key(self):
		#return self.datoBasicoTercero.natural_key()
		return '%s %s - %s' % (self.datoBasicoTercero.tipoDocumento.codigo,str(self.datoBasicoTercero.nit),self.datoBasicoTercero.descripcion)

	def __str__(self):
		return str(self.datoBasicoTercero)

	class Meta:
		db_table = 'Cliente'

# Proveedor
class Proveedor(models.Model):
	idProveedor = models.BigAutoField(primary_key = True)
	datoBasicoTercero =  models.OneToOneField(DatoBasicoTercero,db_column = 'idDatoBasicoTercero',on_delete = models.PROTECT,verbose_name = 'Tercero')
	correo = models.EmailField(max_length=150)
	webSite = models.CharField(max_length=150,verbose_name='Web Site')

	def natural_key(self):
		return '%s %s - %s' % (self.datoBasicoTercero.tipoDocumento.codigo,str(self.datoBasicoTercero.nit),self.datoBasicoTercero.descripcion)
	def __str__(self):
		return str(self.datoBasicoTercero)

	class Meta:
		db_table = 'Proveedor'
		verbose_name_plural = 'Proveedores'

# ProveedorOficina
class ProveedorOficina(models.Model):
	idProveedorOficina =  models.BigAutoField(primary_key = True)
	proveedor =  models.ForeignKey("Proveedor",db_column = 'idProveedor', on_delete = models.PROTECT)
	municipio =  models.ForeignKey("division_territorial.Municipio",db_column = 'idMunicipio', on_delete = models.PROTECT)
	direccion = models.CharField(max_length = 50)
	telefono = models.CharField(max_length = 50)

	def __str__(self):
		return '%s %s (%s)' % (self.proveedor, self.municipio.descripcion,self.telefono)

	class Meta:
		db_table = 'ProveedorOficina'
		verbose_name = 'Proveedor Oficina'
		verbose_name_plural = 'Proveedor Oficinas'

# ProveedoCuenta
class ProveedorCuenta(models.Model):
	idProveedorCuenta = models.BigAutoField(primary_key = True)
	proveedor = models.ForeignKey("Proveedor",db_column = 'idProveedor',on_delete = models.PROTECT)
	metodoPago = models.ForeignKey("MetodoPago",db_column = 'idMetodoPago',on_delete = models.PROTECT,verbose_name = 'Método Pago')
	tipoCuenta = models.ForeignKey("TipoCuenta",db_column = 'idTipoCuenta',on_delete = models.PROTECT,verbose_name = 'Tipo Cuenta')
	banco = models.ForeignKey("Banco",db_column = 'idBanco',on_delete = models.PROTECT)
	numeroCuenta = models.CharField(max_length=100,verbose_name = 'Número Cuenta')

	def __str__(self):
		return '%s (%s) (%s)' % (self.proveedor,self.metodoPago,self.tipoCuenta)

	class Meta:
		db_table = 'ProveedorCuenta'
		verbose_name = 'Proveedor Cuenta'
		verbose_name_plural = verbose_name
