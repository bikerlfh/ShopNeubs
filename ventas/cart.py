from inventario.models import Producto, SaldoInventario
from datetime import datetime
from decimal import Decimal

class Item:
	saldoInventario = None
	cantidad = 0
	valor_total = 0

	def __init__(self,idSaldoIventanrio,cantidad):
		self.saldoInventario = SaldoInventario.objects.get(pk = idSaldoIventanrio)
		self.cantidad = cantidad
		self.calcular_valor_total()

	def __str__(self):
		return 'Producto: %s - Cantidad: %s - $%s' % (self.saldoInventario.producto,str(self.cantidad),str(self.valor_total))

	def change_cantidad(self,cantidad,reemplazar_cantidad = False):
		if reemplazar_cantidad == False:
			self.cantidad += cantidad
		else:
			self.cantidad = cantidad
		if self.cantidad > 0:
			self.calcular_valor_total()
		else:
			self.valor_total = 0
			self.cantidad = 0

	def calcular_valor_total(self):
		if self.saldoInventario.precioOferta:
			self.valor_total = Decimal(self.saldoInventario.precioOferta) * Decimal(self.cantidad)
		else:	
			self.valor_total = Decimal(self.saldoInventario.precioVentaUnitario) * Decimal(self.cantidad)		

class Cart:
	# Listado de Items agregados al carrito
	items = []
	# Cantidad Total del Carro
	cantidad_total = 0
	# Valor Total del Carro
	valor_total = 0
	# Guarda el log de los mensajes (SUCCESS Y ERROR)
	log = []

	def __init__(self):
		self.items = []
		self.cantidad_total = 0
		self.valor_total = 0
		self.log = []

	def get_items(self):
		return self.items

	""" Obtiene el item segun el pk del saldo inventario """
	def get_item(self,idSaldoIventanrio):
		filtro = list(filter(lambda item:item.saldoInventario.pk == idSaldoIventanrio,self.items))
		#filtro = list(producto for producto in self.items if producto.idProducto == idProducto)
		if len(filtro) > 0:
			return filtro[0]
		else:
			return None
	""" Agrega un nuevo item al carro
		parametros 
		idSaldoInventario = el inventario del producto
		cantidad = cantidad de producto
	"""
	def add_item(self,idSaldoInventario,cantidad):
		si = self.get_item(idSaldoInventario)
		if si == None:
			# si se va a agregar un nuevo item, la cantidad debe ser positiva
			if cantidad <= 0:
				self.add_log('error','La cantidad debe ser positiva.')	
				return False
			# Se crea el item
			item = Item(idSaldoInventario,cantidad)
			self.items.append(item)
			self.add_log('success','El producto ' + item.saldoInventario.producto.nombre + ' se agregó al carro')
			self.calcular_totales()
			return True
		else:
			return self.add_cantidad(idSaldoInventario,cantidad)

	# Agrega o disminuye la cantidad de un item del carro
	def add_cantidad(self,idSaldoIventario,cantidad):
		item = self.get_item(idSaldoIventario)
		if item != None:
			item.change_cantidad(cantidad)
			if item.cantidad <=0:
				return self.remove_item(item.saldoInventario.pk)
			else:
				self.add_log('success','Se ha actualizado la cantidad del producto ' + item.saldoInventario.producto.nombre)
			self.calcular_totales()
			return True
		else:
			self.add_log('error','El producto no se ha agregado al carrito!')
			return False

	def ajustar_cantidad(self,idSaldoInventario,cantidad):
		item = self.get_item(idSaldoInventario)
		if item == None:
			return self.add_item(idSaldoInventario,cantidad)
		else:
			item.change_cantidad(cantidad, True)
			self.add_log('success','Se ha actualizado la cantidad del producto ' + item.saldoInventario.producto.nombre)
			self.calcular_totales()
			return True

	# Remueve un item del carro
	def remove_item(self,idSaldoInventario):
		item = self.get_item(idSaldoInventario)
		if item != None:
			self.add_log('success','Se ha eliminado el producto ' + item.saldoInventario.producto.nombre + ' del carrito')
			self.items.remove(item)
			self.calcular_totales()
			return True
		else:
			self.add_log('error','El producto no se ha agregado al carrito!')
		return False

	def add_log(self,tipo,message):
		self.log.append({ 'type': tipo,'message':message,'fecha' : str(datetime.now())})

	# calcula la cantidad y valor total del carrito
	def calcular_totales(self):
		self.cantidad_total = sum(int(item.cantidad) for item in self.items)
		self.valor_total = sum(Decimal(item.valor_total) for item in self.items)

	def get_last_log_error(self,msg_only = True):
		return self.get_last_log('error',msg_only)

	def get_last_log_success(self,msg_only = True):
		return self.get_last_log('success',msg_only)

	def get_last_log(self,tipo,msg_only):
		if len(self.log) > 0:
			log = list(filter(lambda log:log['type'] == tipo, self.log))
			if len(log) >0:
				if msg_only:
					return log[len(log)-1]['message']	
				return log[len(log)-1]
		return None


	# add_log.alters_data = True
	# get_last_log.alters_data = True