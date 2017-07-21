from fcm_django.models import FCMDevice
from tercero.models import Cliente


def send_message(title, body, data=None, user=None, low_priority=False,time_to_live=None):
	devices = None
	if user is None:
		devices = FCMDevice.objects.all().distinct("registration_id")
	elif FCMDevice.objects.filter(user_id=user.pk).exists():
		devices = FCMDevice.objects.get(user_id=user.pk)

	if devices is not None:
		devices.send_message(title=title, body=body, data=data,sound="1")#,low_priority=low_priority,time_to_live=time_to_live)
		return True
	return False


def send_promocion(saldoInventario, user=None):
	title = "Hey! %s esta en promoción" % saldoInventario.producto.nombre
	if user:
		title = "Hey %s! %s esta en promoción" % (user.username,saldoInventario.producto.nombre)
	body = "No te pierdas la oportunidad de adquirilo por tan solo $%s" % str(saldoInventario.precioOferta)
	send_message(title, body, user=user)


# Se envia al cliente la notificación del cambio de estado del pedido
def send_cambio_estado_pedido_venta(pedidoVenta, user):
	cliente = Cliente.objects.get(usuario_id=user.pk)
	title = "Se ha cambiado el estado de tu pedido!"
	body = "%s, tu pedido N° %s  ha sido %s" % (cliente.datoBasicoTercero.primerNombre, str(pedidoVenta.numeroPedido), pedidoVenta.estadoPedidoVenta.descripcion)
	send_message(title, body, user=user)


