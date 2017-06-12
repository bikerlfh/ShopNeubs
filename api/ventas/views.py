from rest_framework.generics import ListAPIView,RetrieveAPIView,CreateAPIView
from rest_framework.serializers import ValidationError
from .serializers import PedidoVentaListSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,AllowAny
from ventas.models import PedidoVenta
from tercero.models import Cliente
from api.exceptions import CustomException

from rest_framework import status

class solicitud_pedido(CreateAPIView):
	serializer_class = PedidoVentaListSerializer
	permission_classes = [IsAuthenticated]


class mis_pedidos(ListAPIView):
	serializer_class = PedidoVentaListSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self,*args,**kwargs):
		try:
			cliente = Cliente.objects.get(usuario=self.request.user.pk)
			queryset_list = PedidoVenta.objects.filter(cliente_id=cliente.pk)
			return queryset_list
		except Cliente.DoesNotExist:
			raise CustomException(detail="El usuario no está creado como cliente",field="usuario_no_cliente")
		except Exception:
			raise CustomException(detail="No tiene pedidos")



		
		
