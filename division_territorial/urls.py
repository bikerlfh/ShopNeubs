from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^departamento/json/(?P<idPais>[\d]{1,5})/$', views.departamento_json, name = 'json_departamento'),
    url(r'^municipio/json/(?P<idDepartamento>[\d]{1,5})/$', views.municipio_json, name = 'json_municipio'),
]