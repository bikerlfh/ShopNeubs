from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

urlpatterns = [
    url(r'^solicitud/$',login_required(permission_required('compras.solicitar_compra',login_url='/')(views.solicitud_pedido.as_view())), name = 'solicitud_compra'),
    url(r'^consulta/pedido/$',login_required(permission_required('compra.consultar_pedido',login_url='/')(views.consulta_pedido.as_view())),name = 'consulta_pedido_compra'),
    url(r'^pedido/posicion/json/(?P<idPedidoCompra>[\d]{1,9})/$',login_required(permission_required('compra.consultar_pedido',login_url='/')(views.pedido_compra_posicion_json))),
]