from django.shortcuts import render
from base.generate_pdf import generate_pdf
from ventas.models import PedidoVenta,PedidoVentaPosicion
# Create your views here.


def reporte_orden_pedido(request,idPedidoVenta):
	listado_pedido_venta = PedidoVenta.objects.filter(pk=idPedidoVenta)
	for pedido in listado_pedido_venta:
		pedido.listadoPedidoVentaPosicion = PedidoVentaPosicion.objects.filter(pedidoVenta = pedido.pk)

	return generate_pdf('reports/ventas/pedido_venta.html',{'listado_pedido_venta':listado_pedido_venta})
