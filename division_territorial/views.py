import json

from django.shortcuts import HttpResponse

from .models import *


# Create your views here.

def departamento_json(request,idPais):
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'items': list({'value':dep.pk,'description':dep.descripcion } for dep in Departamento.objects.filter(pais=idPais))}
	return HttpResponse(json.dumps(dic),content_type='application/json')

def municipio_json(request,idDepartamento):
	# creamos el diccionaro para guardar los datos
	# al diccionario le agregamos u
	dic = {'items': list({'value':mun.pk,'description':mun.descripcion } for mun in Municipio.objects.filter(departamento=idDepartamento))}
	return HttpResponse(json.dumps(dic),content_type='application/json')
