from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from api.exceptions import CustomException
from division_territorial.models import Municipio
from tercero.models import TipoDocumento, Cliente, DatoBasicoTercero
from .serializers import UserCreateSerializer, UsuarioSerializer, TipoDocumentoSerializer, PerfilSerializer

SESSION_CACHE_TIEMOUT = getattr(settings,'SESSION_CACHE_TIEMOUT',7200)


User = get_user_model()

class register(CreateAPIView):
	serializer_class = UserCreateSerializer

class UsuarioDetailView(RetrieveAPIView):
	queryset = User.objects.all()
	serializer_class = UsuarioSerializer
	# fila a buscar
	lookup_field = 'pk'

class UsuarioDetailUsernameView(RetrieveAPIView):
	queryset = User.objects.all()
	serializer_class = UsuarioSerializer
	# fila a buscar
	lookup_field = 'username'

class TipoDocumentoListView(ListAPIView):
	queryset = TipoDocumento.objects.all().order_by('codigo')
	serializer_class = TipoDocumentoSerializer
	#filter_backends = [OrderingFilter]

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(TipoDocumentoListView, self).dispatch(request,*args, **kwargs)

class PerfilView(ListAPIView):
	#queryset = Cliente.objects.all()
	serializer_class = PerfilSerializer
	permission_classes = [IsAuthenticated]

	#lookup_field = 'pk'

	def get_queryset(self,*args,**kwargs):
		try:
			return Cliente.objects.filter(usuario=self.request.user.pk)
		except Cliente.DoesNotExist:
			raise CustomException(detail="El usuario no está creado como cliente",field="usuario_no_cliente")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def PerfilCreateView(request):
	cliente_datos = { 'idCliente':0 }
	transaction.set_autocommit(False)
	try:
		data = request.POST
		user = request.user

		if Cliente.objects.filter(usuario=user.pk).exists():
			raise Exception("El usuario ya existe como cliente")

		idTipoDocumento = data.get('idTipoDocumento',None)
		nit = data.get('nit')
		primerNombre = data.get('primerNombre',None)
		segundoNombre = data.get('segundoNombre',None)
		primerApellido = data.get('primerApellido',None)
		segundoApellido = data.get('segundoApellido',None)
		direccion = data.get('direccion',None)
		telefono = data.get('telefono',None)
		idMunicipio = data.get('idMunicipio',None)

		# Validaciones
		if idTipoDocumento is None:
			raise Exception("El campo idTipoDocumento es necesario")
		if nit is None:
			raise Exception("El campo nit es necesario")
		if primerNombre is None:
			raise Exception("El campo primerNombre es necesario")
		if segundoNombre is None:
			raise Exception("El campo segundoNombre es necesario")
		if primerApellido is None:
			raise Exception("El campo primerApellido es necesario")
		if segundoApellido is None:
			raise Exception("El campo segundoApellido es necesario")
		if direccion is None:
			raise Exception("El campo direccion es necesario")
		if telefono is None:
			raise Exception("El campo telefono es necesario")
		if idMunicipio is None:
			raise Exception("El campo idMunicipio es necesario")


		tipoDocumento = TipoDocumento.objects.get(pk=idTipoDocumento)
		
		# Se valida el tercero
		if DatoBasicoTercero.objects.filter(nit=nit,tipoDocumento=idTipoDocumento).exists():
			raise Exception("Ya existe un usuario con el nit y tipo de documento")
			
		datoBasicoTercero = DatoBasicoTercero(nit = nit,primerNombre = primerNombre,segundoNombre = segundoNombre,
											  primerApellido = primerApellido,segundoApellido = segundoApellido,
											  direccion = direccion,telefono = telefono,tipoDocumento = tipoDocumento)
		datoBasicoTercero.save()

		municipio = Municipio.objects.get(pk=idMunicipio)
		cliente = Cliente(usuario=user,datoBasicoTercero=datoBasicoTercero,correo=user.email,municipio=municipio)
		cliente.save()

		cliente_datos= {
			"idCliente": cliente.pk,
		}
	except Exception as e:
		transaction.rollback()
		raise CustomException(detail=e)
	else:
		pass
		transaction.commit()
	finally:
		pass
		transaction.set_autocommit(True)

	return Response(data=cliente_datos,status=HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def PerfilUpdateView(request):
	cliente_datos = { 'idCliente':0 }
	transaction.set_autocommit(False)
	try:
		data = request.POST
		user = request.user

		if not Cliente.objects.filter(usuario=user.pk).exists():
			raise Exception("El usuario no existe como cliente")

		idTipoDocumento = data.get('idTipoDocumento',None)
		nit = data.get('nit')
		primerNombre = data.get('primerNombre',None)
		segundoNombre = data.get('segundoNombre',None)
		primerApellido = data.get('primerApellido',None)
		segundoApellido = data.get('segundoApellido',None)
		direccion = data.get('direccion',None)
		telefono = data.get('telefono',None)
		idMunicipio = data.get('idMunicipio',None)

		# Validaciones
		if idTipoDocumento is None:
			raise Exception("El campo idTipoDocumento es necesario")
		if nit is None:
			raise Exception("El campo nit es necesario")
		if primerNombre is None:
			raise Exception("El campo primerNombre es necesario")
		if segundoNombre is None:
			raise Exception("El campo segundoNombre es necesario")
		if primerApellido is None:
			raise Exception("El campo primerApellido es necesario")
		if segundoApellido is None:
			raise Exception("El campo segundoApellido es necesario")
		if direccion is None:
			raise Exception("El campo direccion es necesario")
		if telefono is None:
			raise Exception("El campo telefono es necesario")
		if idMunicipio is None:
			raise Exception("El campo idMunicipio es necesario")


		cliente = Cliente.objects.get(usuario=user.pk)
		tipoDocumento = TipoDocumento.objects.get(pk=idTipoDocumento)
		
		datoBasicoTercero = DatoBasicoTercero.objects.get(pk=cliente.datoBasicoTercero_id)
			
		datoBasicoTercero.nit = nit
		datoBasicoTercero.primerNombre = primerNombre
		datoBasicoTercero.segundoNombre = segundoNombre
		datoBasicoTercero.primerApellido = primerApellido
		datoBasicoTercero.segundoApellido = segundoApellido
		datoBasicoTercero.direccion = direccion
		datoBasicoTercero.telefono = telefono
		datoBasicoTercero.tipoDocumento = tipoDocumento
		datoBasicoTercero.save()

		municipio = Municipio.objects.get(pk=idMunicipio)
		cliente.municipio=municipio
		cliente.save()

		cliente_datos = { "idCliente": cliente.pk }
	except Exception as e:
		transaction.rollback()
		raise CustomException(detail=e)
	else:
		pass
		transaction.commit()
	finally:
		pass
		transaction.set_autocommit(True)

	return Response(data=cliente_datos,status=HTTP_200_OK)
		
		








