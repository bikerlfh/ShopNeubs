from django import forms
from django.forms import ValidationError

from .models import SaldoInventario


class SaldoInventarioForm(forms.ModelForm):
	class Meta:
		model = SaldoInventario
		fields = ['producto','proveedor','cantidad','costoTotal','precioOferta','precioCompraUnitario','precioVentaUnitario']
	# Se valida que si el precioVentaUnitario es modificado por el usuario, 
	# no se permita que éste sea menor al costo por unidad
	

	def clean_precioVentaUnitario(self):
		data = self.cleaned_data
		if data['cantidad'] > 0 and data['precioVentaUnitario'] > 0 and  data['precioVentaUnitario'] <= (data['costoTotal']/data['cantidad']):
			raise ValidationError("El precio de Venta no debe ser menor al costo por unidad")
		return data['precioVentaUnitario']

	def clean_precioCompraUnitario(self):
		data = self.cleaned_data
		if data['cantidad'] > 0 and data['costoTotal'] > 0 and data['precioCompraUnitario'] <= 0:
			raise ValidationError("Favor ingresar el Precio Compra Unitario")
		return data['precioCompraUnitario']

	def clean_precioOferta(self):
		data = self.cleaned_data
		if data['cantidad'] > 0 and data['precioOferta'] is not None and data['precioVentaUnitario'] <= data['precioOferta']:
			raise ValidationError("El precio Oferta debe ser menor al precio Venta Unitario")
		return data['precioOferta']

# class PromocionForm(forms.ModelForm):
#     class Meta:
#         model = Promocion
#         fields = ['saldoInventario','precioOferta','fechaInicio','fechaFin']
#         widgets = {
#           'saldoInventario':forms.Select(attrs = {'disabled': 'disabled'}),
#           'precioOferta':forms.TextInput(attrs = {'disabled': 'disabled'}),
#           'fechaInicio':forms.DateTimeInput(attrs = {'disabled': 'disabled'}),
#           'fechaFin':forms.DateTimeInput(attrs = {'disabled': 'disabled'}),
#         }
