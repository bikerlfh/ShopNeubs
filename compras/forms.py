from django import forms

from .models import EstadoPedidoCompra


def get_estados():
	# listado de estados
	listado_estados = list((estado.pk,estado.descripcion) for estado in EstadoPedidoCompra.objects.all())
	# se agrega en la primera posicion una tupla con value 0 y description = '---'
	listado_estados.insert(0,('','------'))
	return listado_estados

class ConsultaPedidoCompraForm(forms.Form):
	numeroPedido = forms.CharField(label = 'Número Pedido',required=False, 
								   widget = forms.NumberInput(attrs={'id':'numeroPedido','class':'form-control','min':'0'}))
	idProveedor = forms.CharField(required=False,widget = forms.HiddenInput(attrs = {'id':'idProveedor','name':'idProveedor'}))
	proveedor = forms.CharField(label = 'proveedor',required=False,
							    widget = forms.TextInput(attrs={'id':'proveedor','class':'form-control','onkeypress':'return false'}))

	
	estadoPedidoCompra = forms.ChoiceField(label = 'Estado',choices = get_estados,required = False,
									   	   widget = forms.Select(attrs = {'id':'idEstadoPedidoCompra','class':'form-control','name':'idEstadoPedidoCompra'}))