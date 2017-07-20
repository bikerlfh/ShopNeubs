from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from division_territorial.models import Pais, Municipio
from .models import TipoDocumento


#from crispy_forms.helper import FormHelper



def validate_number(value):
	number_validator = RegexValidator('^[0-9]*$')
	try:
		number_validator(value)
	except :
		raise ValidationError("El campo no es numerico")
	return value

def get_tipo_documento():
	listado_tipo_documento = list((tipo.pk,tipo.descripcion) for tipo in TipoDocumento.objects.all())
	listado_tipo_documento.insert(0,(0,'---'))
	return listado_tipo_documento

def get_paises():
	# listado de paises
	listado_paises = list((pais.pk,pais.descripcion) for pais in Pais.objects.all())
	# se agrega en la primera posicion una tupla con value 0 y description = '---'
	listado_paises.insert(0,(0,'---'))
	return listado_paises

class ClienteForm(forms.Form):
	tipoDocumento = forms.ChoiceField(label = 'Tipo Documento' ,choices = get_tipo_documento,
									   widget = forms.Select(attrs = {'id':'idTipoDocumento','name':'idTipoDocumento'}))	
	nit = forms.CharField(max_length=12, validators=[validate_number])
	primerNombre =forms.CharField(label = 'Primer Nombre',max_length = 18)
	segundoNombre =forms.CharField(label = 'Segundo Nombre',max_length = 18,required = False)
	primerApellido =forms.CharField(label = 'Primer Apellido',max_length = 18)
	segundoApellido =forms.CharField(label = 'Segundo Apellido',max_length = 18,required = False)

	correo = forms.EmailField(widget = forms.TextInput(attrs = {'id':'correo'}))
	direccion = forms.CharField(max_length = 25)
	telefono  = forms.CharField(max_length=10, validators=[validate_number])


	
	pais = forms.ChoiceField(choices = get_paises,
							 widget = forms.Select(attrs = { 'id':'idPais',
						 						     		 'onChange': "load_options_select('/dt/departamento/json/'+$(this).val()+'/','#idDepartamento')"}))
	departamento = forms.CharField(widget = forms.Select(attrs = {'id':'idDepartamento','onChange': "load_options_select('/dt/municipio/json/'+$(this).val()+'/','#idMunicipio')"}))
	municipio = forms.CharField(widget = forms.Select(attrs = {'id':'idMunicipio'}))


	def set_municipio_value(self,idMunicipio):
		municipio = Municipio.objects.get(pk = idMunicipio)
		pais = Pais.objects.get(pk = municipio.departamento.pais.pk)
		self.fields['pais'].initial = pais.pk
		self.fields['departamento'].initial = municipio.departamento.pk
		self.fields['municipio'].initial = idMunicipio

	# def __init__(self, *args, **kwargs):
	# 	super(ClienteForm, self).__init__(*args, **kwargs)
	# 	self.helper = FormHelper(self)
