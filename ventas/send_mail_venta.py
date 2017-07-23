from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q

DEFAULT_FROM_EMAIL = getattr(settings,'DEFAULT_FROM_EMAIL','shop@neubs.com.co')


# envia un email de notificación de nuevo pedido venta a los miembros del staff 
def send_email_pedido_venta(pedidoVenta):
	try:
		email_admins = list(u.email for u in User.objects.filter(Q(is_superuser=True) | Q(is_staff=True)))
		subject = 'Nuevo pedido venta N° %s, cliente %s' % (str(pedidoVenta.numeroPedido),pedidoVenta.cliente)
		message = 'Se generó la solicitud de pedido N° %s del cliente %s  fecha %s' % (str(pedidoVenta.numeroPedido), pedidoVenta.cliente, pedidoVenta.fecha)
		send_mail(subject, message, DEFAULT_FROM_EMAIL, email_admins)
		return True
	except Exception:
		return False

	


