from django.db.models import Q
from fcm_django.models import FCMDevice
from rest_framework.decorators import permission_classes, api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from api.exceptions import CustomException
from base.models import ApiSincronizacion, ApiTabla, ApiBanner, ApiSection
from .serializers import ApiSincronizacionSerializer, ApiTablaSerializer, ApiBannerSerializer, ApiSectionSerializer


class APITablaListView(ListAPIView):
	serializer_class = ApiTablaSerializer

	def get_queryset(self, *args, **kwargs):
		queryset_list = ApiTabla.objects.all()
		return queryset_list


class APISincronizacionListView(ListAPIView):
	serializer_class = ApiSincronizacionSerializer

	def get_queryset(self, *args, **kwargs):
		filter_Q = Q(ultima=True)
		# Se valida la tabla
		if self.request.GET.get('tabla', None):
			filter_Q = filter_Q & Q(tabla_id=self.request.GET.get('tabla', None))
		return ApiSincronizacion.objects.filter(filter_Q).order_by('-fecha')


class APIBannerListView(ListAPIView):
	serializer_class = ApiBannerSerializer

	def get_queryset(self, *args, **kwargs):
		return ApiBanner.objects.all().order_by('-fecha')


class APISectionListView(ListAPIView):
	serializer_class = ApiSectionSerializer

	def get_queryset(self, *args, **kwargs):
		return ApiSection.objects.all().order_by('-estado')


@api_view(['POST'])
@permission_classes([AllowAny])
def FMCDeviceRegister(request):
	if request.POST:
		registration_id = request.POST.get("registration_id", None)
		type = request.POST.get("type", None)
		active = request.POST.get("active", None)
		user = None
		if request.user.is_authenticated():
			user = request.user

		# se consulta si existe un registro con el mismo token
		fcm_device_token = FCMDevice.objects.filter(registration_id=registration_id)
		if fcm_device_token.exists():
			fcm_device_token = fcm_device_token.first()
			# si el usuario es el mismo
			if fcm_device_token.user == user:
				return Response(data={'detail': 'Token was already created'}, status=HTTP_200_OK)
			elif fcm_device_token.user is None:
				fcm_device_token.user = request.user
				fcm_device_token.save()
				return Response(data={'detail': 'Token updated'}, status=HTTP_200_OK)
		else:
			fcm_device_token = None

		if request.user.is_authenticated():
			# si ya existe el token y tiene un usuario asignado, se crea un nuevo registro con el nuevo usuario.
			if fcm_device_token is not None and fcm_device_token.user is not None:
				FCMDevice(registration_id=registration_id, user=request.user, type=type, active=active).save()
				return Response(data={'detail': 'Token created'}, status=HTTP_201_CREATED)
			# si existe un dispositivo registrado al usuario, se cambia el token
			elif FCMDevice.objects.filter(user_id=request.user.pk).exists():
				fcm_device_user = FCMDevice.objects.get(user_id=request.user.pk)
				fcm_device_user.registration_id = registration_id
				fcm_device_user.save()
				return Response(data={'detail': 'Token updated'}, status=HTTP_200_OK)
			# de lo contrario se crea el registro con el usuario

		# se crea el registro cuando no esta autenticado y cuando está autenticado pero no tiene registro el token
		FCMDevice(registration_id=registration_id, user=user, type=type, active=active).save()
		return Response(data={'detail': 'Token created'}, status=HTTP_201_CREATED)
	else:
		raise CustomException(detail="los campos son necesarios")
