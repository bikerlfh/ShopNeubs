from django.conf.urls import url
from django.contrib.auth.decorators import login_required,permission_required
from . import views

urlpatterns = [
	# detalle del producto
    #url(r'^item/(?P<idSaldoInventario>[\d]+)/$', views.producto_detalle, name='item'),
    # filtro
    url(r'^search/$', views.search_producto, name = 'search'),
    # Productos por marca
    url(r'^marca/$', views.marcas, name = 'marcas'),
    url(r'^marca/(?P<descripcion_marca>[\w ]{2,30})/$', views.productos_marca, name = 'productos_marca'),
    url(r'^ofertas/$', views.ofertas, name = 'ofertas'),
    url(r'^ofertas/(?P<descripcion_marca>[\w ]{2,30})/$', views.ofertas, name = 'ofertas_marca'),
    url(r'^producto/busqueda-asincrona-producto/$', views.busqueda_asincrona_producto, name = 'busqueda_asincrona_producto'),
    url(r'^producto/json/$', login_required(permission_required('compras.solicitar_compra',login_url='/')(views.producto_json))),
    url(r'^saldo-inventario/busqueda/$', login_required(permission_required('inventario.consultar_saldo_inventario',login_url='/')(views.busqueda_saldo_inventario)),name='busqueda_saldo_inventario'),
    url(r'^saldo-inventario/json/$', login_required(permission_required('inventario.consultar_saldo_inventario',login_url='/')(views.saldo_inventario_json)),name='saldo_inventario_json'),
    url(r'^saldo-inventario/precioCompraUnitario/$', login_required(permission_required('compras.solicitar_compra',login_url='/')(views.get_precioCompraUnitario_saldo_inventario)),name='get_precioCompraUnitario_saldo_inventario'),
    url(r'^busqueda/producto/modal/$', login_required(permission_required('compras.solicitar_compra',login_url='/')(views.busqueda_producto_modal)), name='busqueda_producto'),
    # productos por categoria
    url(r'^(?P<descripcion_categoria>[A-ZÁÉÍÓÚa-záéíóú0-9()%+ -]{2,50})/$', views.productos_categoria, name='productos_categoria'),
    url(r'^(?P<descripcion_categoria>[A-ZÁÉÍÓÚa-záéíóú0-9()%+ -]{2,50})/(?P<descripcion_marca>[\w ]{2,30})/$', views.productos_categoria, name='produtos_categoria_marca'),

    url(r'^(?P<descripcion_categoria>[A-ZÁÉÍÓÚa-záéíóú0-9()%+ -]{2,50})/(?P<descripcion_marca>[\w ]{2,30})/(?P<idSaldoInventario>[\d]+)/$', views.producto_detalle, name='item'),
]