from fcm_django.models import FCMDevice

ACTION_VER_PRODUCTO = "VISUALIZAR_PRODUCTO_DETALLE"
ACTION_VER_PEDIDO = "VISUALIZAR_PEDIDO_VENTA"
ACTION_VER_LISTADO_PRODUCTOS = "VISUALIZAR_LISTADO_PRODUCTOS"


def send_message(title, body, data=None, user=None, click_action=None, low_priority=False, time_to_live=None):
	devices = None
	if user is None:
		devices = FCMDevice.objects.all().distinct("registration_id")
	elif FCMDevice.objects.filter(user_id=user.pk).exists():
		devices = FCMDevice.objects.get(user_id=user.pk)

	if devices is not None:
		devices.send_message(title=title, body=body, data=data, icon="ic_notification_small", sound="TYPE_NOTIFICATION",
							 click_action=click_action)  # ,low_priority=low_priority,time_to_live=time_to_live)
		return True
	return False


def send_message_promocion(saldoInventario, user=None):
	title = "Ofertas increíbles en ShopNeubs"
	body = "%s por tan solo %s. Esta oferta durará pocos días, no pierdas esta magnifica oportunidad." % (
	saldoInventario.producto.nombre, format_currency(saldoInventario.precioOferta))
	if user:
		body = "%s! %s" % (user.username, body)
	data = {"idSaldoInventario": saldoInventario.pk}
	send_message(title=title, body=body, data=data, user=user, click_action=ACTION_VER_PRODUCTO)


def send_message_nuevo_producto(saldoInventario, user=None):
	title = "Producto nuevo en ShopNeubs"
	precio = saldoInventario.precioVentaUnitario

	if saldoInventario.precioOferta is not None and saldoInventario.precioOferta > 0:
		precio = saldoInventario.precioOferta

	body = "%s, adquiérelo en ShopNeubs por solo %s" % (saldoInventario.producto.nombre, format_currency(precio))
	if user:
		body = "%s! $%s" % (user.username, body)

	data = {"idSaldoInventario": saldoInventario.pk}
	send_message(title=title, body=body, data=data, user=user, click_action=ACTION_VER_PRODUCTO)


# Se envia al cliente la notificación del cambio de estado del pedido
def send_message_cambio_estado_pedido(pedidoVenta, cliente):
	title = "ShopNeubs"
	body = "%s, tu pedido N° %s  ha sido %s" % (cliente.datoBasicoTercero.primerNombre, str(pedidoVenta.numeroPedido), pedidoVenta.estadoPedidoVenta.descripcion)

	data = {"idPedidoVenta": pedidoVenta.pk}
	send_message(title=title, body=body, data=data, user=user, click_action=ACTION_VER_PEDIDO)


# Envía un mensaje con una petición de listado productos
def send_message_show_url_request(title, body, url_request, user=None):
	data = {"URL_REQUEST": url_request}
	send_message(title=title, body=body, data=data, user=user, click_action=ACTION_VER_LISTADO_PRODUCTOS)


def format_currency(value):
	return '${:,.0f}'.format(value).replace(",", ".")
