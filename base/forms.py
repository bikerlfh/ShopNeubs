from django import forms
from django.forms import ValidationError
from .models import ApiBanner


class ApiBannerForm(forms.ModelForm):
	class Meta:
		model = ApiBanner
		fields = ['imagen','isClickable','saldoInventario','urlRequest','estado']
		# widgets = {
		# 	'fecha':forms.DateTimeInput(attrs = {'disabled': 'disabled'}),
		# }
	
	# Se valida si es clickeable debe seleccionar un saldoInventario o especificar la UrlRequest
	def clean_estado(self):
		data = self.cleaned_data
		if data['isClickable'] == True and data['saldoInventario'] == None and  len(data['urlRequest']) == 0:
			raise ValidationError("Debe seleccionar un Saldo Inventario o especificar la Url Request")
		return data['estado']