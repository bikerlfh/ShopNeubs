from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField,SerializerMethodField,ValidationError,CharField,EmailField
from django.contrib.auth import get_user_model
from registration.models import SHA1_RE, RegistrationProfile
from django.contrib.sites.shortcuts import get_current_site
from tercero.models import Cliente
from django.test import RequestFactory

User = get_user_model()

def get_site():
        """
        Return a Site or RequestSite instance for use in registration.
        """
        factory = RequestFactory()
        return get_current_site(factory.get('/'))

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