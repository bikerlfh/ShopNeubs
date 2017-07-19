import xlrd
from inventario.models import SaldoInventario
from decimal import Decimal

class PofoSerializer:
		def __init__(self,codigo,producto,valor):
				self.codigo = codigo
				self.producto = producto
				self.valor = valor
				self.saldoInventario = None

		def __str__(self):
				return "%s-%s  $ %s" % (self.codigo,self.producto,str(self.valor))

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
						self.saldoInventario.precioVentaUnitario = self.saldoInventario.precioVentaUnitario + self.diferencia()
						if self.saldoInventario.precioOferta is not None:
								self.saldoInventario.precioOferta = self.saldoInventario.precioOferta + self.diferencia()

						# si la cantidad es 1 se modifica el costoTotal
						if self.saldoInventario.cantidad == 1:
								self.saldoInventario.costoTotal = Decimal(self.valor)
						# se modifica el precioCompraUnitario
						self.saldoInventario.precioCompraUnitario = Decimal(self.valor)
						self.saldoInventario.save()

class Pofo:

		def __init__(self):
				# almacena los Pofo sin cambios
				self.listado_sin_cambio = []
				# almacena los Pofo pendiente por actualizar
				self.listado_pendiente_actualizar = []
				# almacena los Pofo pendiente crear
				self.listado_pendiente_crear = []

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
				# se abre el libro
				xl_wordbook = xlrd.open_workbook(file)
				if xl_wordbook is not None:
					#  se consulta la primera sheet
					xl_sheet = xl_wordbook.sheet_by_index(0)
					# obtenemos las columnas donde están los códigos
					columns_codigo = self.get_columns_codigo(xl_sheet)

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
								pofo = PofoSerializer(codigo,producto,valor)
								# si existe el saldo inventario con referencia proveedor = codigo
								if SaldoInventario.objects.filter(referenciaProveedor = pofo.codigo).exists():
										pofo.saldoInventario = SaldoInventario.objects.get(referenciaProveedor = pofo.codigo)

										# si el saldo inventario no tiene igual los precios se agrega al listado pendiente por actualizar
										if not pofo.isEquals():
												self.listado_pendiente_actualizar.append(pofo)
										else:
												# si el saldoinventario tiene precios iguales se agrega al listado sin cambio
												self.listado_sin_cambio.append(pofo)
								else:
										# se agrega pofo al listado pendiente por crear
										self.listado_pendiente_crear.append(pofo)




