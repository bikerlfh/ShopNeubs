from django.contrib import admin
from .models import Carousel, ApiTabla,ApiSincronizacion
from django.contrib.admin.models import LogEntry
# Register your models here.

# clase de visualización del modelos de rango pedido (compras y ventas)
class RangoPedidoAdmin(admin.ModelAdmin):
	list_display = ['codigo','descripcion','numeroDesde','numeroHasta','numeroActual','estado']
	search_fields = ['codigo','descripcion']
	ordering = ['numeroActual']

# clase de visualización del modelos con codigo y descripcion
class DefaultAdmin(admin.ModelAdmin):
	list_display = ['codigo', 'descripcion']
	ordering = ['codigo']
	search_fields = ['codigo','descripcion']

class CarouselAdmin(admin.ModelAdmin):
	list_display = ['imagen','url','order','estado']
	ordering = ['order','estado']
	search_fields = ['order','estado']


admin.site.register(Carousel,CarouselAdmin)

admin.site.register(ApiTabla,DefaultAdmin)


class ApiSincronizacionAdmin(admin.ModelAdmin):
	fieldsets  = [
		('',{'fields':['tabla','fecha']}),
	]
	list_display = ['tabla','fecha']
	ordering = ['-fecha']
	search_fields = ['tabla','fecha']
	list_filter = ['tabla']

admin.site.register(ApiSincronizacion,ApiSincronizacionAdmin)


class logEntryAdmin(admin.ModelAdmin):
	list_display = ['__str__','user','action_time','content_type','object_repr','change_message']
	ordering = ['-action_time']
	search_fields = ['content_type','user']
	list_filter = ['content_type']
	
admin.site.register(LogEntry,logEntryAdmin)
