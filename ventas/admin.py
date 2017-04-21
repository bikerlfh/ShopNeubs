from django.contrib import admin
from .models import *
from base.admin import DefaultAdmin,RangoPedidoAdmin
from django import forms
# Register your models here.

admin.site.register(EstadoPedidoVenta,DefaultAdmin)

class ParametroImpuestoAdmin(admin.ModelAdmin):
	list_display = ['codigo','descripcion','porcentaje']
	search_fields = ['codigo','descripcion']

class PedidoVentaAdmin(admin.ModelAdmin):
	#form = PedidoVentaAdminForm
  fieldsets  = [
    (None,{'fields':['numeroPedido','cliente','estadoPedidoVenta','fechaAutorizacion','urlFactura','idUsuarioCreacion']}),
  ]
  readonly_fields = ('cliente','numeroPedido','fechaAutorizacion','idUsuarioCreacion',)
  list_display = ['numeroPedido','cliente','fecha','estadoPedidoVenta']
  search_fields = ['numeroPedido','cliente']

admin.site.register(PedidoVenta,PedidoVentaAdmin)
admin.site.register(ParametroImpuesto,ParametroImpuestoAdmin)
admin.site.register(RangoNumeroPedidoVenta,RangoPedidoAdmin)