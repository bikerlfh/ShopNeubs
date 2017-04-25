from django.conf.urls import url
from django.contrib.auth.decorators import login_required,permission_required
from ventas import views

urlpatterns = [
    url(r'^solicitud/$', login_required(views.solicitud_pedido), name = 'solicitud_venta'),
    url(r'^autorizar/$', login_required(permission_required('ventas.autorizar_pedido',login_url='/')(views.autorizar_pedido.as_view())), name = 'autorizar_venta'),
    url(r'^pedido/modificar/$', login_required(permission_required('ventas.change_pedidoventa',login_url='/')(views.modificar_pedido)), name = 'modificar_pedido_venta'),
    url(r'^pedido/posicion/modificar/(?P<idPedidoVentaPosicion>[\d]{1,9})/$', login_required(permission_required('ventas.modificar_pedido',login_url='/')(views.modificar_pedido_posicion)), name = 'modificar_pedido_venta_posicion'),
    url(r'^pedido-enviado/(?P<numeroPedido>[\d])/$', login_required(views.pedido_enviado), name = 'pedido_venta_enviado'),
    url(r'^pedido/json/$', login_required(permission_required('ventas.consultar_pedido',login_url='/')(views.pedido_venta_json)),name='pedido_venta_json'),
    url(r'^pedido/json/all/$', login_required(permission_required('ventas.consultar_pedido',login_url='/')(views.pedido_venta_json_all)),name='pedido_venta_json_all'),
    url(r'^pedido/posicion/json/(?P<idPedidoVenta>[\d]{1,9})/$',login_required(permission_required('ventas.consultar_pedido',login_url='/')(views.pedido_venta_posicion_json))),
    url(r'^busqueda/pedido/modal/$', login_required(permission_required('ventas.consultar_pedido',login_url='/')(views.busqueda_pedido_venta_modal)), name='busqueda_venta_pedido_modal'),
    url(r'^consulta/pedido/$',login_required(permission_required('ventas.consultar_pedido',login_url='/')(views.consulta_pedido.as_view())),name = 'consulta_pedido_venta'),
    url(r'^consulta/pedido/avanzada/$',login_required(permission_required('ventas.consultar_pedido',login_url='/')(views.consulta_avanzada_pedido)),name = 'consulta_avanzada_pedido_venta'),
    url(r'^pedido/venta-compra/json/(?P<idPedidoVentaPosicion>[\d]{1,9})/$',login_required(permission_required('ventas.consultar_pedido',login_url='/')(views.pedido_venta_compra_json)),name = 'pedido_venta_compra_json'),

]