from django import forms
from .models import EstadoPedidoVenta


def get_estados():
	# listado de estados
	listado_estados = list((estado.pk,estado.descripcion) for estado in EstadoPedidoVenta.objects.all())
	# se agrega en la primera posicion una tupla con value 0 y description = '---'
	listado_estados.insert(0,('','------'))
	return listado_estados

class ConsultaPedidoVentaForm(forms.Form):
	numeroPedido = forms.CharField(label = 'Número Pedido',required=False, 
								   widget = forms.NumberInput(attrs={'id':'numeroPedido','class':'form-control','min':'0'}))
	idCliente = forms.CharField(required=False,widget = forms.HiddenInput(attrs = {'id':'idCliente','name':'idCliente'}))
	cliente = forms.CharField(label = 'Cliente',required=False,
							  widget = forms.TextInput(attrs={'id':'cliente','class':'form-control','onkeypress':'return false'}))

	
	estadoPedidoVenta = forms.ChoiceField(label = 'Estado',choices = get_estados,required = False,
									   	  widget = forms.Select(attrs = {'id':'idEstadoPedidoVenta','class':'form-control','name':'idEstadoPedidoVenta'}))