from django.contrib import admin

from base.admin import DefaultAdmin, RangoPedidoAdmin
from .models import *

# Register your models here.

admin.site.register(EstadoPedidoVenta,DefaultAdmin)
admin.site.register(MotivoCancelacionPedidoVenta,DefaultAdmin)

class ParametroImpuestoAdmin(admin.ModelAdmin):
	list_display = ['codigo','descripcion','porcentaje']
	search_fields = ['codigo','descripcion']

class PedidoVentaAdmin(admin.ModelAdmin):
	#form = PedidoVentaAdminForm
  fieldsets  = [
    (None,{'fields':['numeroPedido','cliente','estadoPedidoVenta','fechaAutorizacion','urlFactura','idUsuarioCreacion']}),
  ]
  readonly_fields = ('numeroPedido','fechaAutorizacion','idUsuarioCreacion',)
  list_display = ['numeroPedido','cliente','fecha','estadoPedidoVenta']
  search_fields = ['numeroPedido','cliente']

admin.site.register(PedidoVenta,PedidoVentaAdmin)
admin.site.register(PedidoVentaPosicion)
admin.site.register(ParametroImpuesto,ParametroImpuestoAdmin)
admin.site.register(RangoNumeroPedidoVenta,RangoPedidoAdmin)