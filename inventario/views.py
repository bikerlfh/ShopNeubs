from django.core import serializers
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render,render_to_response,HttpResponse,get_object_or_404,get_list_or_404,Http404
from django.views.decorators.cache import cache_page
from inventario import core
from inventario.models import Producto,Categoria,Marca,SaldoInventario,ProductoReview,ProductoImagen,Promocion
import operator
from functools import reduce
import json

SESSION_CACHE_TIEMOUT = getattr(settings,'SESSION_CACHE_TIEMOUT',7200)
# vista de marcas registradas
@cache_page(SESSION_CACHE_TIEMOUT)
def marcas(request):
	if not cache.get('marcas'):
		marcas = Marca.objects.all().order_by('descripcion')
		cache.set('marcas',marcas,SESSION_CACHE_TIEMOUT)
	else:
		marcas = cache.get('marcas')
	return render(request,"inventario/marcas.html",{'listado_marcas': marcas})

@cache_page(SESSION_CACHE_TIEMOUT)
def productos_categoria(request,descripcion_categoria,descripcion_marca = None):
	page_title = descripcion_categoria
	order = request.GET.get('order','rel')
	page = request.GET.get('page', 1)

	categoria = get_object_or_404(Categoria,descripcion = descripcion_categoria)
	filtro_Q = Q(producto__categoria = categoria.pk) | Q(producto__categoria__categoriaPadre = categoria.pk)
	if descripcion_marca is not None:
		marca = get_object_or_404(Marca,descripcion__iexact = descripcion_marca)
		filtro_Q = Q(producto__marca = marca.pk) & (filtro_Q)
		page_title = "%s %s" % (descripcion_categoria,descripcion_marca)

	# Se consulta el inventario
	#listado_saldo_inventario = SaldoInventario.objects.filter(filtro_Q).order_by(order)
	listado_saldo_inventario = core.consultar_saldo_inventario_paginado(filtro_Q,order,page)
	listado_marcas = None
	# se consultan las marcas de los productos del inventario siempre y cuando no se halla filtrado por marca
	if descripcion_marca == None:
		# se consultan las marcas de los productos del inventario
		listado_marcas = core.cargar_marcas_desde_listado_saldo_inventario(listado_saldo_inventario)

	meta_descriptions = "%s en ShopNeubs" % page_title
	return render(request,"inventario/filtro_producto.html",{ 'listado_saldo_inventario': listado_saldo_inventario,
															  'listado_marcas': listado_marcas,
															  'listado_categorias' : core.get_menu_categorias(),
															  'page_title': page_title,
															  'meta_descriptions':meta_descriptions})

@cache_page(SESSION_CACHE_TIEMOUT)
def productos_marca(request,descripcion_marca):
	order = request.GET.get('order','rel')
	page = request.GET.get('page', 1)
	#listado_saldo_inventario = get_list_or_404(SaldoInventario,producto__marca__descripcion = descripcion_marca)
	listado_saldo_inventario = core.consultar_saldo_inventario_paginado(Q(producto__marca__descripcion = descripcion_marca),order,page)
	return render(request,"inventario/filtro_producto.html",{ 'listado_saldo_inventario': listado_saldo_inventario , 
															  'listado_categorias' : core.get_menu_categorias(),
															  'page_title':descripcion_marca,
															  'meta_descriptions': "Productos %s en ShopNeubs" % descripcion_marca })	

@cache_page(SESSION_CACHE_TIEMOUT)
def producto_detalle(request,descripcion_categoria,descripcion_marca,idSaldoInventario):
	print("ENTRA AL PRODUCTO DETALLE %s" % idSaldoInventario)
	# Solo se consulta con la categoria y marca para evitar que el usuario ponga cualquier
	saldoInventario = get_object_or_404(SaldoInventario,
										pk = idSaldoInventario,
										producto__categoria__descripcion = descripcion_categoria,
										producto__marca__descripcion = descripcion_marca)
	# Cada vez que el producto se visualiza por un usuario, se debe registrar esa visita
	review = ProductoReview(producto = saldoInventario.producto,numeroVista = 1,numeroVenta = 0)
	review.save()
	# se envia el item que esta en el carro
	item = None
	if 'shop_cart' in request.session:
		cart = request.session.get('shop_cart')
		item = cart.get_item(saldoInventario.pk)
	context = {
		'saldoInventario' : saldoInventario,
		'item_cart':item,
		'titulo_producto_relacionado' : 'Productos Relacionados', 
		'listado_producto_relacionado': core.get_productos_relacionados(saldoInventario)
	}
	return render(request,"inventario/producto_detalle.html",context)


# realiza una busqueda por el filtro que escriba el usuario
@cache_page(SESSION_CACHE_TIEMOUT)
def search_producto(request):
	if not request.GET.get('filtro'):
		raise Http404
	filtro = request.GET.get('filtro').strip()
	list_filtro = filtro.replace('+',' ').split(' ')

	objects_Q = Q()
	listado_categorias = Categoria.objects.filter(reduce(operator.or_, (Q(descripcion__icontains=x) for x in list_filtro)))
	if listado_categorias:
		for categoria in listado_categorias:
			objects_Q |= Q(producto__categoria = categoria.pk) | Q(producto__categoria__categoriaPadre = categoria.pk)

	marca = Marca.objects.filter(Q(descripcion__in = list_filtro))
	if len(marca) > 0:
		objects_Q = objects_Q and Q(producto__marca = marca.first().pk)
	
	for filtro in list_filtro:
		objects_Q |= Q(producto__nombre__icontains = filtro) | Q(producto__referencia__icontains = filtro)
	#listado_saldo_inventario = get_list_or_404(SaldoInventario,objects_Q)

	order = request.GET.get('order','rel')
	page = request.GET.get('page', 1)
	listado_saldo_inventario = core.consultar_saldo_inventario_paginado(objects_Q,order,page)

	listado_marcas = None
	# se consultan las marcas de los productos del inventario siempre y cuando no se halla filtrado por marca
	if listado_saldo_inventario:
		# se consultan las marcas de los productos del inventario
		listado_marcas = core.cargar_marcas_desde_listado_saldo_inventario(listado_saldo_inventario)
	else:
		listado_marcas = Marca.objects.all()
	return render(request,"inventario/filtro_producto.html",{'listado_saldo_inventario' : listado_saldo_inventario,
															 'listado_marcas':listado_marcas, 
															 'page_title': 'Búsqueda (%s)' % request.GET.get('filtro'),
															 'listado_categorias' : core.get_menu_categorias() })
	#return render_to_response("inventario/filtrar_producto.html",{'listadoProductos' : list_productos })

@cache_page(SESSION_CACHE_TIEMOUT)
def ofertas(request,descripcion_marca = None):
	page_title = "Ofertas"

	order = request.GET.get('order','rel')
	page = request.GET.get('page', 1)

	filtro_Q = Q(precioOferta__isnull=False,precioOferta__gt=0,estado = True)
	listado_marcas = None
	if descripcion_marca != None:
		marca = get_object_or_404(Marca,descripcion__iexact = descripcion_marca)
		filtro_Q = filtro_Q & Q(producto__marca = marca.pk)
		page_title = "Ofertas (%s)" % marca.descripcion

	listado_saldo_inventario = core.consultar_saldo_inventario_paginado(filtro_Q,order,page)
	if descripcion_marca == None:
		listado_marcas = core.cargar_marcas_desde_listado_saldo_inventario(listado_saldo_inventario)
	return render(request,"inventario/filtro_producto.html",{'listado_saldo_inventario' : listado_saldo_inventario,
															 'listado_marcas':listado_marcas, 
															 'listado_categorias' : core.get_menu_categorias(),
															 'page_title':page_title })

# Esta vista se llama asincronamente

def busqueda_asincrona_producto(request):
	top = getattr(settings,'SELECT_TOP_MAX_INDEX_ITEM',10)
	# filas a consultar
	fields =['idSaldoInventario','estado','producto','fechaCreacion','producto__nombre',
			'precioOferta','precioVentaUnitario','producto__categoria__descripcion','producto__marca__descripcion']
	listado_saldo_inventario = None
	if request.GET.get("promocion",False):
		if not cache.get('index_promocion'):
			#listado_saldo_inventario = SaldoInventario.objects.filter_products(precioOferta__gt=0,estado=True).values(*fields)[:top]
			listado_promociones = Promocion.objects.only('saldoInventario_id').filter(fechaFin__isnull=True,estado=True,saldoInventario__precioOferta__gt=0,saldoInventario__estado=True).order_by('-fechaInicio')[:top]
			listado_saldo_inventario = SaldoInventario.objects.filter_products(pk__in=list(p.saldoInventario_id for p in listado_promociones)).values(*fields)
			cache.set('index_promocion',listado_saldo_inventario,SESSION_CACHE_TIEMOUT)
		else:
			listado_saldo_inventario = cache.get('index_promocion')
	elif request.GET.get("mas_vistos",False):
		if not cache.get('index_mas_vistos'):
			review = ProductoReview.objects.all().order_by('-numeroVista')[:top*2].values_list('producto',flat=True)
			listado_idSaldoInventario = []
			for idProducto in review:
				if SaldoInventario.objects.filter_products(estado=True,producto=idProducto).exists():
					listado_idSaldoInventario.append(SaldoInventario.objects.filter_products(estado=True,producto=idProducto).only('pk').first().pk)
				if len(listado_idSaldoInventario) >= top:
					break
			#listado_saldo_inventario = SaldoInventario.objects.filter_products(estado=True,producto__in = ProductoReview.objects.all().order_by('-numeroVista')[:top].values_list('producto',flat=True)).values(*fields)[:top]
			listado_saldo_inventario = SaldoInventario.objects.filter_products(estado=True,pk__in = listado_idSaldoInventario).values(*fields)
			cache.set('index_mas_vistos',listado_saldo_inventario,SESSION_CACHE_TIEMOUT)
		else:
			listado_saldo_inventario = cache.get('index_mas_vistos')
	# si existe inventario
	if listado_saldo_inventario:
		for saldo in listado_saldo_inventario:
			# se pone la descripción vacia porque no se necesita
			saldo['producto__descripcion']=''
			# se carga la imagen principal del producto
			try:
				saldo['producto__imagen'] = ProductoImagen.objects.only('imagen').get(producto = saldo['producto'],order = 0).imagen
			except Exception as e:
				saldo['producto_imagen'] = None
		return render(request,'inventario/div_producto.html',{'listado_saldo_inventario':listado_saldo_inventario})
	return HttpResponse("")

def busqueda_saldo_inventario(request):
	# objeto donde se almacenará el PK del registro seleccionado
	objectPk = '#idSaldoInventario'
	if request.GET.get("objectPk",None) is not None:
		objectPk = "#"+request.GET.get("objectPk")
		
	# objeto donde se visualizará el registro seleccionado
	# { 'objeto','columna' }
	objectShow = {'#producto':'fields.producto','#proveedor':'fields.proveedor','#precioVentaUnitario':'fields.precioVentaUnitario'}

	return render_to_response("inventario/busqueda_saldo_inventario.html",{'objectPk':objectPk, 'objectShow':objectShow})

"""Carga en json el saldo inventario filtrado por producto y/o proveedor"""
def saldo_inventario_json(request):
	idProducto = request.GET.get('idProducto',None)
	idProveedor = request.GET.get('idProveedor',None)
	estado = request.GET.get('estado',None)
	filtro_Q = Q()
	if idProducto != None:
		filtro_Q = filtro_Q & Q(producto = idProducto)
	if idProveedor != None:
		filtro_Q = filtro_Q & Q(proveedor = idProveedor)
	if estado != None:
		filtro_Q = filtro_Q & Q(estado = bool(int(estado)))
	datos = json.loads(serializers.serialize('json',SaldoInventario.objects.filter(filtro_Q),fields=('producto','proveedor','referenciaProveedor','cantidad','precioVentaUnitario','precioOferta','estado'),use_natural_foreign_keys=True))
	dic = {'data': datos}
	return HttpResponse(json.dumps(dic),content_type='application/json')
	
def producto_json(request):
	# serializamos en json todos los productos e usamos los natural_key de las llaves foraneas
	datos = json.loads(serializers.serialize('json',Producto.objects.all(),fields=('numeroProducto','nombre','referencia')))
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'data': datos}
	return HttpResponse(json.dumps(dic),content_type='application/json')

def busqueda_producto_modal(request):
	# columnas del DataTable ejemplo ('column name': 'valor')
	columns = { 'Numero Producto':'fields.numeroProducto','Nombre':'fields.nombre','Referencia': 'fields.referencia'}
	# objeto donde se almacenará el PK del registro seleccionado
	objectPk = '#idProducto'
	if request.GET.get("objectPk",None) is not None:
		objectPk = "#"+request.GET.get("objectPk")
		
	# objeto donde se visualizará el registro seleccionado
	# { 'objeto','columna' }
	objectShow = {'#producto':'fields.nombre'}
	if len(request.GET.get("objectShow",""))>0:
		objectShow = {"#"+request.GET.get("objectShow"):'fields.nombre'}
	
	return render(request,"base/tabla-dinamica-modal.html",{ 'title': 'Busqueda de Productos','url':"/producto/json/", 
															 'columns': columns, 'objectPk':objectPk, 'objectShow':objectShow })

def get_precioCompraUnitario_saldo_inventario(request):
	if request.GET.get('idProducto',None) != None and request.GET.get('idProveedor',None):
		if SaldoInventario.objects.filter(producto=request.GET.get('idProducto'),proveedor=request.GET.get('idProveedor')).exists():
			return HttpResponse(SaldoInventario.objects.get(producto=request.GET.get('idProducto'),proveedor=request.GET.get('idProveedor')).precioCompraUnitario)
	return HttpResponse(0)

