from division_territorial.models import Pais,Departamento,Municipio
from rest_framework.serializers import (ModelSerializer, HyperlinkedIdentityField,
										SerializerMethodField,ValidationError,CharField)


class PaisSerializer(ModelSerializer):
	class Meta:
		model = Pais
		fields = [
			'pk',
			'codigo',
			'descripcion',
		]
class DepartamentoSerializer(ModelSerializer):
	class Meta:
		model = Departamento
		fields = [
			'pk',
			'pais',
			'codigo',
			'descripcion',
		]
class MunicipioSerializer(ModelSerializer):
	class Meta:
		model = Municipio
		fields = [
			'pk',
			'departamento',
			'codigo',
			'descripcion',
		]