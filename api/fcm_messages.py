from fcm_django.models import FCMDevice
from tercero.models import Cliente


ACTION_VER_PRODUCTO = "VISUALIZAR_PRODUCTO_DETALLE"
ACTION_VER_PEDIDO = "VISUALIZAR_PEDIDO_VENTA"
ACTION_VER_LISTADO_PRODUCTO = "VISUALIZAR_LISTADO_PEDIDO"


def send_message(title, body, data=None, user=None,click_action=None, low_priority=False,time_to_live=None):
	devices = None
	if user is None:
		devices = FCMDevice.objects.all().distinct("registration_id")
	elif FCMDevice.objects.filter(user_id=user.pk).exists():
		devices = FCMDevice.objects.get(user_id=user.pk)

	if devices is not None:
		devices.send_message(title=title, body=body, data=data,icon="ic_notification_small", sound="TYPE_NOTIFICATION", click_action=click_action)#,low_priority=low_priority,time_to_live=time_to_live)
		return True
	return False


def send_promocion(saldoInventario, user=None):
	title = "Hey! %s en oferta 😍" % saldoInventario.producto.nombre
	if user:
		title = "Hey %s! %s en oferta 😍" % (user.username, saldoInventario.producto.nombre)
	body = "No te pierdas la oportunidad de adquirilo por tan solo $%s" % '{:,.0f}'.format(saldoInventario.precioOferta).replace(",",".")
	data = {"idSaldoInventario": saldoInventario.pk}
	send_message(title, body, data=data, user=user,click_action=ACTION_VER_PRODUCTO)


def send_nuevo_producto(saldoInventario,user=None):
	title = "🛍 ShopNeubs 🛍"
	if user:
		title = "Hey %s! %s esta en promoción" % (user.username, saldoInventario.producto.nombre)
	body = "%s - $%s adquierelo en nuestra tienda" % (saldoInventario.producto.nombre, '{:,.0f}'.format(saldoInventario.precioOferta).replace(",","."))
	data = {"idSaldoInventario": saldoInventario.pk}
	send_message(title, body, data=data, user=user,click_action=ACTION_VER_PRODUCTO)


# Se envia al cliente la notificación del cambio de estado del pedido
def send_cambio_estado_pedido_venta(pedidoVenta, user):
	cliente = Cliente.objects.get(usuario_id=user.pk)
	title = "ShopNeubs"
	body = "%s, tu pedido N° %s  ha sido %s" % (cliente.datoBasicoTercero.primerNombre, str(pedidoVenta.numeroPedido), pedidoVenta.estadoPedidoVenta.descripcion)

	data = {"idPedidoVenta":pedidoVenta.pk}
	send_message(title, body,data=data, user=user,click_action=ACTION_VER_PEDIDO)





