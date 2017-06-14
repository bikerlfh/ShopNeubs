from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField,SerializerMethodField,ValidationError,CharField,EmailField
from django.contrib.auth import get_user_model
from registration.models import SHA1_RE, RegistrationProfile
from django.contrib.sites.shortcuts import get_current_site
from tercero.models import Cliente,TipoDocumento,DatoBasicoTercero
from division_territorial.models import Municipio
from django.test import RequestFactory

User = get_user_model()

def get_site():
        """
        Return a Site or RequestSite instance for use in registration.
        """
        factory = RequestFactory()
        return get_current_site(factory.get('/'))


class TipoDocumentoSerializer(ModelSerializer):
	class Meta:
		model = TipoDocumento
		fields = [
			'pk',
			'codigo',
			'descripcion',
		]

class PerfilSerializer(ModelSerializer):
	idTipoDocumento = SerializerMethodField()
	nit = SerializerMethodField()
	primerNombre = SerializerMethodField()
	segundoNombre = SerializerMethodField()
	primerApellido = SerializerMethodField()
	segundoApellido = SerializerMethodField()
	direccion = SerializerMethodField()
	telefono = SerializerMethodField()
	idPais = SerializerMethodField()
	idDepartamento = SerializerMethodField()
	idMunicipio = SerializerMethodField()

	class Meta:
		model = Cliente
		fields = [
			'idCliente',
			'idTipoDocumento',
			'nit',
			'primerNombre',
			'segundoNombre',
			'primerApellido',
			'segundoApellido',
			'correo',
			'direccion',
			'telefono',
			'idPais',
			'idDepartamento',
			'idMunicipio',
		]

	def get_idTipoDocumento(self,obj):
		return obj.datoBasicoTercero.tipoDocumento_id
	def get_nit(self,obj):
		return obj.datoBasicoTercero.nit
	def get_primerNombre(self,obj):
		return obj.datoBasicoTercero.primerNombre
	def get_segundoNombre(self,obj):
		return obj.datoBasicoTercero.segundoNombre
	def get_primerApellido(self,obj):
		return obj.datoBasicoTercero.primerApellido
	def get_segundoApellido(self,obj):
		return obj.datoBasicoTercero.segundoApellido
	def get_direccion(self,obj):
		return obj.datoBasicoTercero.direccion
	def get_telefono(self,obj):
		return obj.datoBasicoTercero.telefono
	def get_idPais(self,obj):
		return obj.municipio.departamento.pais_id
	def get_idDepartamento(self,obj):
		return obj.municipio.departamento_id
	def get_idMunicipio(self,obj):
		return obj.municipio_id

class UsuarioSerializer(ModelSerializer):
	idCliente = SerializerMethodField()
	class Meta:
		model = User
		fields = [
			'pk',
			'username',
			'email',
			'idCliente',
		]
	def get_idCliente(self,obj):
		try:
			cliente = Cliente.objects.get(usuario_id=obj.pk);
			return cliente.pk
		except Exception as e:
			pass
		return None;


class UserCreateSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = [
			'username',
			'password',
			'email'
		]
		extra_kwargs = {'password':
							{'write_only':True}
						}

	def validate_username(self,value):
		data = self.get_initial()
		username = data.get("username")

		if User.objects.filter(username = username).exists():
			raise ValidationError("Ya existe un usuario con este nombre")
		return value

	def validate_email(self,value):
		data = self.get_initial()
		email = data.get("email")

		if User.objects.filter(email = email).exists():
			raise ValidationError("Ya existe un usuario con este email")
		return value


	def create(self,validated_data):
		username = validated_data['username']
		email = validated_data['email']
		password = validated_data['password']

		user_info = {
			'username':username,
			'email':email,
			'password':password
		}
		new_user = RegistrationProfile.objects.create_inactive_user(
			site=get_site(),
			**user_info
		)
		return validated_data