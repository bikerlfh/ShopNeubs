from django.shortcuts import render,Http404
from base.generate_pdf import generate_pdf
from ventas.models import PedidoVenta,PedidoVentaPosicion
from inventario.models import SaldoInventario,Categoria
# Create your views here.


def reporte_orden_pedido(request,idPedidoVenta):
	listado_pedido_venta = PedidoVenta.objects.filter(pk=idPedidoVenta)
	for pedido in listado_pedido_venta:
		pedido.listadoPedidoVentaPosicion = PedidoVentaPosicion.objects.filter(pedidoVenta = pedido.pk)

	return generate_pdf('reports/ventas/pedido_venta.html',{'listado_pedido_venta':listado_pedido_venta})

# solo para los adminsitradores
def lista_precios(request):
	if not request.user.is_superuser:
		raise Http404()

	fields =['producto__numeroProducto','producto__nombre','referenciaProveedor','proveedor__datoBasicoTercero__descripcion',
			'precioOferta','precioVentaUnitario','producto__categoria__codigo']
	listado_saldo_inventario = SaldoInventario.objects.filter_products().order_by('producto__categoria__codigo','producto__numeroProducto').values(*fields)
	listado_categoria = []
	codigo_categoria = "0"
	for saldo in listado_saldo_inventario:
		if len(listado_categoria) ==0 or saldo['producto__categoria__codigo'] != codigo_categoria:
			categoria = Categoria.objects.get(codigo=saldo['producto__categoria__codigo'])
			codigo_categoria = categoria.codigo
			if categoria.categoriaPadre:
				listado_categoria.append({'categoria': "%s - %s " % (categoria.categoriaPadre.descripcion ,categoria.descripcion),'listado_saldo_inventario':[]})
			else:
				listado_categoria.append({'categoria': categoria.descripcion,'listado_saldo_inventario':[]})
		if saldo['producto__categoria__codigo'] == codigo_categoria:
			listado_categoria[-1]['listado_saldo_inventario'].append(saldo)
	return generate_pdf("reports/ventas/lista-precios.html",{'listado':listado_categoria})
