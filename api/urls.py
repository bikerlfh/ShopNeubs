from django.conf.urls import url,include
from .division_territorial import views as views_division_territorial
from .tercero import views as views_tercero
from .inventario import views as views_inventario
from .ventas import views as views_ventas
from . import views as views_base

urlpatterns = [
	url(r'^rest-auth/', include('rest_auth.urls')),
    #url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),

	url(r'^register/$', views_tercero.register.as_view(), name = 'register'),
	url(r'^profile/$', views_tercero.PerfilView.as_view(), name = 'profile'),
	url(r'^profile/create/$', views_tercero.PerfilCreateView, name = 'profile_create'),
	url(r'^profile/edit/$', views_tercero.PerfilUpdateView, name = 'profile_edit'),
	#url(r'^login/$', views_tercero.login.as_view(), name = 'login'),
	
	url(r'^categoria/(?P<pk>[\d]{1,2})/$', views_inventario.CategoriaDetailView.as_view(), name = 'categoria_detalle'),

	url(r'^producto/(?P<pk>[\d]{1,4})/$', views_inventario.producto_detalle.as_view(), name = 'producto_detalle'),
	url(r'^producto-simple/$', views_inventario.saldo_inventario_simple, name = 'producto_simple'),
	

	url(r'^search/$', views_inventario.search_producto.as_view(), name = 'search_producto'),
	url(r'^producto-marca/$', views_inventario.producto_marca.as_view(), name = 'producto_marca'),
	url(r'^ofertas/$', views_inventario.oferta.as_view(), name = 'oferta'),

	url(r'^index-oferta/$', views_inventario.oferta_index.as_view(), name = 'index_oferta'),
	url(r'^index-mas-vistos/$', views_inventario.mas_vistos_index.as_view(), name = 'index_mas_vistos'),

	
	#url(r'^ventas/solicitud/$', views_ventas.solicitud_pedido.as_view(), name = 'solicitud_pedido'),
	url(r'^ventas/solicitud/$', views_ventas.PedidoVentaCreateView, name = 'solicitud_pedido'),


	url(r'^mis-pedidos/$', views_ventas.mis_pedidos.as_view(), name = 'mis_pedidos'),
	url(r'^pedido-simple/(?P<idPedidoVenta>[\d]{1,4})/$', views_ventas.PedidoVentaDetalleView.as_view(), name = 'pedido_detalle_simple'),
	url(r'^pedido/(?P<idPedidoVenta>[\d]{1,4})/$', views_ventas.PedidoVentaCompletoView.as_view(), name = 'pedido_detalle'),
	

	url(r'^usuario/(?P<pk>[\d]{1,4})/$', views_tercero.UsuarioDetailView.as_view(), name = 'usuario_detalle'),

	url(r'^usuario/(?P<username>[\w]{1,25})/$', views_tercero.UsuarioDetailUsernameView.as_view(), name = 'usuario_detalle'),

	#sincronizacion
	url(r'^sync/banner/$', views_base.APIBanner.as_view(), name = 'api_banner'),
	url(r'^sync/categoria/$', views_inventario.CategoriaListView.as_view(), name = 'lista_categoria'),
	url(r'^sync/marca/$', views_inventario.MarcaListView.as_view(), name = 'lista_marca'),
	url(r'^sync/api-tabla/$', views_base.APITabla.as_view(), name = 'api_tabla'),
	url(r'^sync/api-sincronizacion/$', views_base.APISincronizacion.as_view(), name = 'api_sincronizacion'),
	url(r'^sync/pais/$', views_division_territorial.PaisListView.as_view(), name = 'sync_pais'),
	url(r'^sync/departamento/$', views_division_territorial.DepartamentoListView.as_view(), name = 'sync_departamento'),
	url(r'^sync/municipio/$', views_division_territorial.MunicipioListView.as_view(), name = 'sync_municipio'),
	url(r'^sync/tipo-documento/$', views_tercero.TipoDocumentoListView.as_view(), name = 'sync_tipo_documento'),

	
	url(r'^$', views_inventario.producto_categoria.as_view(), name = 'producto_categoria'),
]