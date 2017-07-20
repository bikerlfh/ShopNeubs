from django.contrib import admin
from django.contrib.admin.models import LogEntry

from .forms import ApiBannerForm
from .models import Carousel, ApiTabla, ApiSincronizacion, ApiBanner, ApiSection, ArchivoModificacionPrecio


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
		('',{'fields':['tabla','ultima']}),
	]
	list_display = ['tabla','fecha','ultima']
	ordering = ['-fecha','ultima']
	search_fields = ['tabla','fecha']
	list_filter = ['tabla']

admin.site.register(ApiSincronizacion,ApiSincronizacionAdmin)

class ApiBannerAdmin(admin.ModelAdmin):
	form = ApiBannerForm
	fieldsets  = [
		('',{'fields':['imagen','isClickable','saldoInventario','urlRequest','estado']}),
	]
	list_display = ['imagen','isClickable','saldoInventario','urlRequest','fecha','estado']
	ordering = ['estado','-fecha']
	#search_fields = ['tabla','fecha']
	list_filter = ['estado','isClickable']

	def has_delete_permission(self, request, obj=None):
		return False

admin.site.register(ApiBanner,ApiBannerAdmin)

class ApiSectionAdmin(admin.ModelAdmin):
	fieldsets  = [
		('',{'fields':['title','subTitle','orden','urlRequestProductos','urlRequestMas','estado']}),
	]
	list_display = ['title','subTitle','orden','urlRequestProductos','urlRequestMas','estado']
	ordering = ['estado']
	list_filter = ['estado']

	def has_delete_permission(self, request, obj=None):
		return False

admin.site.register(ApiSection,ApiSectionAdmin)


class logEntryAdmin(admin.ModelAdmin):
	list_display = ['__str__','user','action_time','content_type','object_repr','change_message']
	ordering = ['-action_time']
	search_fields = ['content_type','user']
	list_filter = ['content_type']
	
admin.site.register(LogEntry,logEntryAdmin)

class ArchivoModificacionPrecioadmin(admin.ModelAdmin):
		list_display = ['__str__','proveedor','fecha','ultimo']

admin.site.register(ArchivoModificacionPrecio,ArchivoModificacionPrecioadmin)
