from rest_framework.generics import ListAPIView,RetrieveAPIView,CreateAPIView
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST
from .serializers import PedidoVentaListSerializer,PedidoVentaDetalleSerializer,PosicionPedidoSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,AllowAny
from ventas.models import PedidoVenta
from tercero.models import Cliente
from api.exceptions import CustomException
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view,permission_classes
from ventas.pedidoventamanager import PedidoVentaManager
from rest_framework import status
from rest_framework import viewsets
from inventario.models import SaldoInventario
import json


User = get_user_model()

class mis_pedidos(ListAPIView):
	serializer_class = PedidoVentaListSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self,*args,**kwargs):
		try:
			cliente = Cliente.objects.get(usuario=self.request.user.pk)
			queryset_list = PedidoVenta.objects.filter(cliente_id=cliente.pk).order_by('-fecha')
			return queryset_list
		except Cliente.DoesNotExist:
			raise CustomException(detail="El usuario no está creado como cliente",field="usuario_no_cliente")
		except Exception:
			raise CustomException(detail="No tiene pedidos")

class PedidoVentaDetalleView(RetrieveAPIView):
	queryset = PedidoVenta.objects.all()
	serializer_class = PedidoVentaDetalleSerializer
	permission_classes = [IsAuthenticated]
	lookup_field = 'idPedidoVenta'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def PedidoVentaCreateView(request):
	# Se valida que el usuario exista como cliente
	if not Cliente.objects.filter(usuario_id = request.user.pk).exists():
		raise CustomException(detail="El usuario no está creado como cliente",field="usuario_no_cliente")
	
	# se valida que la información llegue
	if not request.POST.get('data',None):
		raise CustomException(detail="No se encontró ningun producto en el carro")
	# se cargan los datos
	data = json.loads(request.POST.get('data',None))	
	# Serializamos las posiciones
	serializer = PosicionPedidoSerializer(data=data,many=isinstance(data,list))
	if serializer.is_valid():
		# se guarda el pedido
		numeroPedido = serializer.save(user=request.user.pk)
		if numeroPedido != -1:
			return Response(data={'numeroPedido':numeroPedido},status = HTTP_201_CREATED)
		else:
			raise CustomException(detail="Error al guardar el pedido venta")
	else:
		raise CustomException(detail=serializer.errors)







		
		
