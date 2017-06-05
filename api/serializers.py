from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField,SerializerMethodField,ValidationError
from inventario.models import Categoria,Producto,SaldoInventario
from base.models import ApiTabla,ApiSincronizacion
from django.contrib.auth import get_user_model
from datetime import date,datetime

User = get_user_model()

class UserCreateSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = [
			'username',
			'password',
			'email'
		]
		extra_kwargs = {'password':
							{ 'write_only':True }
						}
	def validate_email(self,value):
		data = self.get_initial()
		email = data.get("email")

		if User.objects.filter(email = email).exists():
			raise ValidationError("Ya existe un usuario registrado con el email %s" % email)
		return value

	def create(self,validated_data):
		username = validated_data['username']
		email = validated_data['email']
		password = validated_data['password']
		user_obj = User(username = username,email = email)
		user_obj.set_password(password)
		user_obj.save()
		return validated_data

class ApiTablaSerializer(ModelSerializer):
	class Meta:
		model = ApiTabla
		fields = [
			'idApiTabla',
			'codigo',
			'descripcion'
		]

class ApiSincronizacionSerializer(ModelSerializer):
	tabla = ApiTablaSerializer()
	fecha = SerializerMethodField()
	class Meta:
		model = ApiSincronizacion
		fields = [
			'idApiSincronizacion',
			'tabla',
			'fecha'
		]

	def get_fecha(self,obj):
		#date1 = datetime(obj.fecha)
		return obj.fecha.strftime('%d-%m-%Y %H:%M:%S')


