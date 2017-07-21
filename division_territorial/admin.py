from django.contrib import admin

from base.admin import DefaultAdmin
from .models import *

# deshabilitamos la acción de borrar los seleccionados
admin.site.disable_action('delete_selected')

admin.site.register(Pais,DefaultAdmin)

class DepartamentoAdmin(admin.ModelAdmin):
	list_display = ['codigo','descripcion','pais']
	ordering = ['pais','codigo']
	search_fields = ['codigo','descripcion']
	list_filter = ['pais']
	raw_id_fields = ['pais']

admin.site.register(Departamento,DepartamentoAdmin)

class MunicipioAdmin(admin.ModelAdmin):
	list_display = ['codigo','descripcion','departamento']
	ordering = ['departamento','codigo']
	search_fields = ['codigo','descripcion']
	list_filter = ['departamento']
	raw_id_fields = ['departamento']

admin.site.register(Municipio,MunicipioAdmin)

