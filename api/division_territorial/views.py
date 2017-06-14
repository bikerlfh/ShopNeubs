from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter,OrderingFilter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .serializers import *
from django.conf import settings

SESSION_CACHE_TIEMOUT = getattr(settings,'SESSION_CACHE_TIEMOUT',7200)

class PaisListView(ListAPIView):
	queryset = Pais.objects.all().order_by('codigo')
	serializer_class = PaisSerializer
	filter_backends = [OrderingFilter]

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(PaisListView, self).dispatch(request,*args, **kwargs)

class DepartamentoListView(ListAPIView):
	#queryset = Departamento.objects.all().order_by('codigo')
	serializer_class = DepartamentoSerializer
	filter_backends = [OrderingFilter]

	def get_queryset(self,*args,**kwargs):
		idPais = self.request.GET.get('idPais',None)
		if idPais:
			return Departamento.objects.filter(pais_id = idPais).order_by('codigo')
		else:
			return Departamento.objects.all().order_by('codigo')

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(DepartamentoListView, self).dispatch(request,*args, **kwargs)

class MunicipioListView(ListAPIView):
	#queryset = Municipio.objects.all().order_by('codigo')
	serializer_class = MunicipioSerializer
	filter_backends = [OrderingFilter]

	def get_queryset(self,*args,**kwargs):
		idDepartamento = self.request.GET.get('idDepartamento',None)
		if idDepartamento:
			return Municipio.objects.filter(departamento_id = idDepartamento).order_by('codigo')
		else:
			return Municipio.objects.all().order_by('codigo')

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(MunicipioListView, self).dispatch(request,*args, **kwargs)