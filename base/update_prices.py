import xlrd
from inventario.models import SaldoInventario
from decimal import Decimal


class SASerializer:

		def __init__(self,referencia,producto,valor):
				self.referencia = referencia
				self.producto = producto
				self.valor = valor
				self.saldoInventario = None

		def __str__(self):
				return "%s-%s  $ %s" % (self.referencia,self.producto,str(self.valor))

		def diferencia(self):
				if self.saldoInventario is None:
						return -1
				return Decimal(self.valor) - Decimal(self.saldoInventario.precioCompraUnitario)

		def precioVentaNuevo(self):
				if self.saldoInventario is None:
						return -1
				return self.saldoInventario.precioVentaUnitario + self.diferencia()

		def precioOfertaNuevo(self):
				if self.saldoInventario is None:
						return -1
				if self.saldoInventario.precioOferta:
						return self.saldoInventario.precioOferta + self.diferencia()
				return None

		# Especifia si el cambio fue muy grande, >= 30%
		def isDanger(self):
				if self.saldoInventario is None:
						return False

				diferencia = self.diferencia()
				if diferencia < 0:
						diferencia *=-1
				porcentaje = None
				if self.saldoInventario.precioCompraUnitario == 0:
						porcentaje = diferencia * 100 / self.saldoInventario.costoTotal
				else:
						porcentaje = diferencia * 100 / self.saldoInventario.precioCompraUnitario
				return porcentaje >= 30

		def isEquals(self):
				if self.saldoInventario is None:
						return False
				elif self.saldoInventario.precioCompraUnitario == self.valor:
						return True

		# Modifica el saldo Inventario
		def updateSaldoInventario(self):
				if self.saldoInventario is not None:

						# se ajustan los precios de venta y oferta con la diferencia que hay en el precio
						self.saldoInventario.precioVentaUnitario += self.diferencia()
						if self.saldoInventario.precioOferta is not None:
								self.saldoInventario.precioOferta += self.diferencia()

						# si la cantidad es 1 se modifica el costoTotal
						if self.saldoInventario.cantidad == 1:
								self.saldoInventario.costoTotal = Decimal(self.valor)
						elif self.saldoInventario.cantidad == 0:
								self.saldoInventario.cantidad = 1

						self.saldoInventario.estado=True
						# se modifica el precioCompraUnitario
						self.saldoInventario.precioCompraUnitario = Decimal(self.valor)
						self.saldoInventario.save()

# clase con la que interactua la vista
# dependiendo del proveedor, ejecuta la clase de actualización
class ActualizacionPrecio:
		def __init__(self,archivoModificacionPrecio):
				self.proveedor = archivoModificacionPrecio.proveedor
				self.file = archivoModificacionPrecio.file.path
				# almacena los Pofo sin cambios
				self.listado_sin_cambio = []
				# almacena los Pofo pendiente por actualizar
				self.listado_pendiente_actualizar = []
				# almacena los Pofo pendiente crear
				self.listado_pendiente_crear = []

				self.mensajeError = None

		def make_actualizacion(self):
				if self.proveedor.datoBasicoTercero.nit is 1:
						pofo = PofoActualizacion(self.proveedor.pk)
						if pofo.analizar_actualizacion(self.file) != 1:
								self.mensajeError = pofo.mensajeError
						else:
								self.listado_pendiente_actualizar = pofo.listado_pendiente_actualizar
								self.listado_pendiente_crear = pofo.listado_pendiente_crear
								self.listado_sin_cambio = pofo.listado_sin_cambio

				elif self.proveedor.datoBasicoTercero.nit is 2:
						tense = TenseActualizacion(self.proveedor.pk)
						if tense.analizar_actualizacion(self.file) != 1:
								self.mensajeError = tense.mensajeError
						else:
								self.listado_pendiente_actualizar = tense.listado_pendiente_actualizar
								self.listado_pendiente_crear = tense.listado_pendiente_crear
								self.listado_sin_cambio = tense.listado_sin_cambio

				return self.mensajeError is None or self.mensajeError is ""

# clase para actualizar precios de POFO
class PofoActualizacion:

		def __init__(self,idProveedor):
				self.idProveedor = idProveedor
				# almacena los Pofo sin cambios
				self.listado_sin_cambio = []
				# almacena los Pofo pendiente por actualizar
				self.listado_pendiente_actualizar = []
				# almacena los Pofo pendiente crear
				self.listado_pendiente_crear = []

				self.mensajeError = None

		""" Obtiene las columnas donde dice codigo"""
		def get_columns_codigo(self,xl_sheet):
				columns_codigo = []
				nrows = xl_sheet.nrows
				ncols = xl_sheet.ncols
				# se recorren las filas
				for row in range(0, nrows):
						# se recorren las columnas
						for col in range(0, ncols):
								# si el tipo de la columna es TEXT
								if xl_sheet.cell_type(row,col) is 1:
										# se obtiene el valor de la celda
										value_cell = xl_sheet.cell(row, col).value
										# comparamos si la celta es "COD"
										if value_cell.upper().__eq__("COD"):
												if not col in columns_codigo:
														columns_codigo.append(col)
				columns_codigo.sort()
				return columns_codigo

		# analiza la actualización de datos
		def analizar_actualizacion(self,file):
				try:
						# se abre el libro
						xl_wordbook = xlrd.open_workbook(file)
						if xl_wordbook is not None:
								#  se consulta la primera sheet
								xl_sheet = xl_wordbook.sheet_by_index(0)
								# obtenemos las columnas donde están los códigos
								columns_codigo = self.get_columns_codigo(xl_sheet)
								if len(columns_codigo) == 0:
										self.mensajeError = "No se encontraron columnas con códigos"
										return 0
								#recorremos las filas
								for row in range(0,xl_sheet.nrows):
										# recorremos las columnas de los códigos
										for col_cod in columns_codigo:
												value_cell = str(xl_sheet.cell(row,col_cod).value)
												#  Se valida que el valor de la celda sea NUMBER(2)
												if xl_sheet.cell_type(row,col_cod) is 2:

														codigo = int(xl_sheet.cell(row,col_cod).value)
														producto = xl_sheet.cell(row,col_cod + 1).value
														# si el campo valor es un text quiere decir que no tiene precio
														if xl_sheet.cell_type(row,col_cod+ 2) is 1:
																continue
														valor = (xl_sheet.cell(row,col_cod+ 2).value)
														# se crea el objeto
														pofo = SASerializer(codigo,producto,valor)
														# si existe el saldo inventario con referencia proveedor = codigo
														if SaldoInventario.objects.filter(referenciaProveedor=pofo.referencia,proveedor_id = self.idProveedor).exists():
																listado_saldo_inventario = SaldoInventario.objects.filter(referenciaProveedor=pofo.referencia,proveedor_id = self.idProveedor)

																# si se encuentran más de un saldo inventario con el mismo código
																if listado_saldo_inventario.count() > 1:
																		# se recorren los saldos inventario
																		for saldo in listado_saldo_inventario:
																				pofo_repetido = SASerializer(codigo,producto,valor)
																				pofo_repetido.saldoInventario = saldo
																				# si el saldo inventario no tiene igual los precios se agrega al listado pendiente por actualizar
																				if not pofo_repetido.isEquals():
																						self.listado_pendiente_actualizar.append(pofo_repetido)
																				else:
																						# si el saldoinventario tiene precios iguales se agrega al listado sin cambio
																						self.listado_sin_cambio.append(pofo_repetido)
																else:
																		pofo.saldoInventario = listado_saldo_inventario.first()

																		# si el saldo inventario no tiene igual los precios se agrega al listado pendiente por actualizar
																		if not pofo.isEquals():
																				self.listado_pendiente_actualizar.append(pofo)
																		else:
																				# si el saldoinventario tiene precios iguales se agrega al listado sin cambio
																				self.listado_sin_cambio.append(pofo)
														else:
																# se agrega pofo al listado pendiente por crear
																self.listado_pendiente_crear.append(pofo)

								return 1
				except Exception as ex:
						self.mensajeError = ex
						self.listado_pendiente_crear = []
						self.listado_sin_cambio = []
						self.listado_pendiente_actualizar = []
						return -1

# clase para actualizar precios de Tense
class TenseActualizacion:

		def __init__(self,idProveedor):
				self.idProveedor = idProveedor
				# almacena los sa sin cambios
				self.listado_sin_cambio = []
				# almacena los sa pendiente por actualizar
				self.listado_pendiente_actualizar = []
				# almacena los sa pendiente crear
				self.listado_pendiente_crear = []

				self.mensajeError = None

		# elimina los espacios en blanco de mas
		def format_referencia(self, referencia):
				return " ".join(referencia.split())

		# se ajusta el valor del producto
		def format_valor(self,valor):
				#  se multiplica por 1000 el valor, debido a que el archivo viene en decimales
				if valor < 10000:
						valor *= 1000
				# se resta el 5%
				valor -= (valor * 5 / 100)
				return valor

		def analizar_actualizacion(self,file):
				try:
						xl_wordbook = xlrd.open_workbook(file)
						if xl_wordbook is not None:
								#  se consulta la primera sheet
								xl_sheet = xl_wordbook.sheet_by_index(0)
								for row in range(0,xl_sheet.nrows):
										for col in range(0,xl_sheet.ncols):
												#  se verifica que el typo de la celda sea TEXT
												if xl_sheet.cell_type(row,col) == 1:
														referencia = self.format_referencia(xl_sheet.cell(row,col).value)

														# si el campo valor no es numerico quiere decir que no tiene precio
														if xl_sheet.cell_type(row, col + 1) is not 2:
																continue
														valor = self.format_valor(xl_sheet.cell(row, col + 1).value)
														if not referencia.__eq__("") and SaldoInventario.objects.filter(referenciaProveedor__istartswith=referencia,proveedor_id=self.idProveedor).exists():
																listado_saldo_inventario = SaldoInventario.objects.filter(referenciaProveedor__istartswith=referencia,proveedor_id=self.idProveedor)
																if len(listado_saldo_inventario) > 0:
																		listado_saldo_inventario = listado_saldo_inventario.filter(referenciaProveedor__iexact=referencia,proveedor_id=self.idProveedor)
																for sa in listado_saldo_inventario:
																		tense = SASerializer(referencia,referencia,valor)
																		tense.saldoInventario = sa
																		if not tense.isEquals():
																				self.listado_pendiente_actualizar.append(tense)
																		else:
																				self.listado_sin_cambio.append(tense)
														else:
																tense = SASerializer(referencia,referencia,valor)
																self.listado_pendiente_crear.append(tense)

						return 1
				except Exception as ex:
						self.mensajeError = ex
						return -1



