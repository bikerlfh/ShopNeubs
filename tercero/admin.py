from django.contrib import admin

from base.admin import DefaultAdmin
from .models import *

# Register your models here.

admin.site.register(TipoDocumento,DefaultAdmin)
admin.site.register(MetodoPago,DefaultAdmin)
admin.site.register(TipoCuenta,DefaultAdmin)
admin.site.register(Banco,DefaultAdmin)


class DatoBasicoTerceroAdmin(admin.ModelAdmin):
	list_display = ['nit','descripcion','direccion','telefono','tipoDocumento']
	search_fields = ['nit', 'descripcion']

admin.site.register(DatoBasicoTercero,DatoBasicoTerceroAdmin)

class ProveedorAdmin(admin.ModelAdmin):
	fieldsets  = [
		('Tercero',{'fields':['datoBasicoTercero']}),
		('Datos Proveedor',{'fields':['correo','webSite']})
	]
	list_display = ['datoBasicoTercero','correo','webSite']
	search_fields = ['datoBasicoTercero']

admin.site.register(Proveedor,ProveedorAdmin)

class ClienteAdmin(admin.ModelAdmin):
	list_display = ['datoBasicoTercero','correo','municipio']
	search_fields = ['datoBasicoTercero','correo']

admin.site.register(Cliente,ClienteAdmin)
