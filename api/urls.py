from django.conf.urls import url,include
from .tercero import views as views_tercero
from .inventario import views as views_inventario
from .ventas import views as views_ventas
from . import views as views_base

urlpatterns = [
	url(r'^rest-auth/', include('rest_auth.urls')),
    #url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),

	url(r'^register/$', views_tercero.register.as_view(), name = 'register'),
	#url(r'^login/$', views_tercero.login.as_view(), name = 'login'),
	url(r'^categoria/$', views_inventario.CategoriaListView.as_view(), name = 'lista_categoria'),
	url(r'^marca/$', views_inventario.MarcaListView.as_view(), name = 'lista_marca'),
	url(r'^categoria/(?P<pk>[\d]{1,2})/$', views_inventario.CategoriaDetailView.as_view(), name = 'categoria_detalle'),

	url(r'^producto/(?P<pk>[\d]{1,4})/$', views_inventario.producto_detalle.as_view(), name = 'producto_detalle'),

	url(r'^search/$', views_inventario.search_producto.as_view(), name = 'search_producto'),
	url(r'^producto-marca/$', views_inventario.producto_marca.as_view(), name = 'producto_marca'),
	url(r'^ofertas/$', views_inventario.oferta.as_view(), name = 'oferta'),
	
	url(r'^ventas/solicitud/$', views_ventas.solicitud_pedido.as_view(), name = 'solicitud_pedido'),
	url(r'^ventas/mis-pedidos/$', views_ventas.mis_pedidos.as_view(), name = 'mis_pedidos'),

	url(r'^api-tabla/$', views_base.APITabla.as_view(), name = 'api_tabla'),
	url(r'^api-sincronizacion/$', views_base.APISincronizacion.as_view(), name = 'api_sincronizacion'),

	
	url(r'^$', views_inventario.producto_categoria.as_view(), name = 'producto_categoria'),
]