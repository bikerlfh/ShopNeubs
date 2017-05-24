from rest_framework.generics import ListAPIView,RetrieveAPIView,CreateAPIView
from .serializers import PedidoVentaSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,AllowAny
from ventas.models import PedidoVenta
from tercero.models import Cliente

class solicitud_pedido(CreateAPIView):
	serializer_class = PedidoVentaSerializer
	permission_classes = [IsAuthenticated]


class mis_pedidos(ListAPIView):
	serializer_class = PedidoVentaSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self,*args,**kwargs):
		cliente = Cliente.objects.get(usuario=self.request.user.pk)
		queryset_list = PedidoVenta.objects.filter(cliente=cliente.pk)
		return queryset_list
