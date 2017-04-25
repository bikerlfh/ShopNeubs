from django.contrib import admin
from .models import Carousel
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
	list_display = ['imagen', 'order','estado']
	ordering = ['order','estado']
	search_fields = ['order','estado']


admin.site.register(Carousel,CarouselAdmin)

class logEntryAdmin(admin.ModelAdmin):
	list_display = ['__str__','user','action_time','content_type','object_repr','change_message']
	ordering = ['-action_time']
	search_fields = ['content_type','user']
	list_filter = ['content_type']
	
admin.site.register(LogEntry,logEntryAdmin)
