from django.conf.urls import url
from django.contrib.auth.decorators import login_required,permission_required
from . import views

urlpatterns = [
	url(r'^proveedor/json/$', login_required(permission_required('compras.solicitar_compra',login_url='/')(views.proveedor_json))),
	url(r'^busqueda/proveedor/modal/$', login_required(permission_required('compras.solicitar_compra',login_url='/')(views.busqueda_proveedor_modal)), name='busqueda_proveedor_modal'),
	url(r'^cliente/json/$', login_required(permission_required('compras.solicitar_compra',login_url='/')(views.cliente_json))),
	url(r'^busqueda/cliente/modal/$', login_required(permission_required('compras.solicitar_compra',login_url='/')(views.busqueda_cliente_modal)), name='busqueda_cliente_modal'),
	url(r'^pedido/detalle/(?P<idPedidoVenta>[\d]+)/$', login_required(views.pedido_detalle), name='mis_pedido_detalle'),

]