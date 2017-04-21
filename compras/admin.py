from django.contrib import admin
from .models import *
from base.admin import DefaultAdmin,RangoPedidoAdmin
from django import forms
# Register your models here.

class PedidoCompraAdmin(admin.ModelAdmin):
	fieldsets  = [
		(None,{'fields':['numeroPedido','proveedor','estadoPedidoCompra','urlFactura']}),
	]
	readonly_fields = ('numeroPedido','proveedor',)
	list_display = ['numeroPedido','proveedor','fecha','estadoPedidoCompra']
	search_fields = ['numeroPedido','proveedor']
	ordering = ['estadoPedidoCompra']

admin.site.register(PedidoCompra,PedidoCompraAdmin)

admin.site.register(EstadoPedidoCompra,DefaultAdmin)

admin.site.register(RangoNumeroPedidoCompra,RangoPedidoAdmin)







