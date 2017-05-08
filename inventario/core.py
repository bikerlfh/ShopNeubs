from .models import ProductoImagen,Categoria,SaldoInventario,Marca
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q


def get_menu_categorias():
	categorias = []
	if not cache.get('menu_categorias'):
		categorias = get_categorias()
		cache.set('menu_categorias',categorias,getattr(settings,'SESSION_COOKIE_AGE',7200))
	else:
		categorias = cache.get('menu_categorias')
	return categorias

# consulta las categorias padres y sus hijos y retorna una lista
def get_categorias(idCategoriaPadre = None):
	categorias = []
	listado_categoria_padre = Categoria.objects.filter(categoriaPadre=idCategoriaPadre).values('idCategoria','descripcion').order_by('descripcion')
	if len(listado_categoria_padre) > 0:
		for i,categoria in enumerate(listado_categoria_padre):
			categorias.append({ 'categoriaPadre' : categoria, 'categoriaHijo':  get_categorias(categoria['idCategoria'])})
	return categorias
# retorna los productos relacionados de otro
# filtra por categoria, categoria padre y marca
def get_productos_relacionados(saldoInventario):
	filtro_Q = Q(producto__categoria = saldoInventario.producto.categoria.pk) | Q(producto__categoria__categoriaPadre = saldoInventario.producto.categoria.pk)
	filtro_Q |= Q(producto__categoria = saldoInventario.producto.categoria.categoriaPadre)
	filtro_Q |= Q(producto__marca = saldoInventario.producto.marca.pk)
	# Se filtran solo los que esten con estado True y tengan cantidades
	filtro_Q = filtro_Q & Q(estado=True) & Q(cantidad__gte = 1)
	try:
		fields=['idSaldoInventario','producto','producto__nombre','precioOferta','precioVentaUnitario','producto__categoria__descripcion','producto__marca__descripcion']
		listado_saldo = SaldoInventario.objects.filter_products(filtro_Q).exclude(producto = saldoInventario.producto).distinct().values(*fields)[:getattr(settings,'SELECT_TOP_MIN',5)]
		cargar_producto_imagen_principal(listado_saldo)
		return listado_saldo
	except SaldoInventario.DoesNotExist:
		return None
		
# Retorna un listado de saldoInventario paginado y ordenado
def consultar_saldo_inventario_paginado(filtro,order,page):
	# Se ajusta el order_by del saldo inventario
	if order == "desc":
		order = '-precioVentaUnitario'
	elif(order == 'asc'):
		order = 'precioVentaUnitario'
	elif order == 'rel':
		order = '-fechaCreacion'
	elif order == 'promo':
		order = 'precioOferta'
	# Solo se consultan estas filas
	fields =['idSaldoInventario','estado','producto','fechaCreacion','producto__nombre','producto__descripcion','producto__especificacion',
			'precioOferta','precioVentaUnitario','producto__categoria__descripcion','producto__marca__descripcion','producto__marca__idMarca']
	# se consulta el inventario con los filtros y el order_by
	# Se devuelve un diccionario con las filas (las de la variable fields) esto con el fin de 
	# solo realizar la consulta a l base de datos de los datos que necesitamos
	listado_saldo_inventario = SaldoInventario.objects.filter_products(filtro).order_by(order).values(*fields)
	cargar_producto_imagen_principal(listado_saldo_inventario)
	# se crea el objeto Paginator apartir de la lista del inventario
	paginator = Paginator(listado_saldo_inventario,getattr(settings,'NUM_ITEMS_DISPLAY',10))
	try:
		listado_saldo_inventario = paginator.page(page)
	except PageNotAnInteger:
		listado_saldo_inventario = paginator.page(1)
	except EmptyPage:
		listado_saldo_inventario = paginator.page(paginator.num_pages)
	listado_saldo_inventario.count = paginator.count
	listado_saldo_inventario.num_pages = paginator.num_pages
	return listado_saldo_inventario

# a partir de un listado saldo inventario (diccionario) se carga el producto__imagen
def cargar_producto_imagen_principal(listado_saldo_inventario):
	# Se recorre el listado de diccionarios de SaldoInventario
	for saldo in listado_saldo_inventario:
		try:
			# Se consulta la imagen 
			saldo['producto__imagen'] = ProductoImagen.objects.only('imagen').get(producto = saldo['producto'],order = 0).imagen
		except:
			saldo['producto__imagen'] = None
	return listado_saldo_inventario
# A partir de un listado de saldo inventario, retorna las marcas de los productos
def cargar_marcas_desde_listado_saldo_inventario(listado_saldo_inventario):
	if listado_saldo_inventario:
		return Marca.objects.filter(idMarca__in = list(p['producto__marca__idMarca'] for p in listado_saldo_inventario)).distinct().values('codigo','descripcion')
	return None
	