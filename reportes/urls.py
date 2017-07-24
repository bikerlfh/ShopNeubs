from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

urlpatterns = [
    url(r'^orden-pedido/(?P<idPedidoVenta>[\d]+)/$', login_required(permission_required('ventas.reportes',login_url='/')(views.reporte_orden_pedido)), name = 'reporte_orden_pedido'),
    url(r'^lista-precios/$', login_required((views.lista_precios)), name = 'lista_precios'),
]