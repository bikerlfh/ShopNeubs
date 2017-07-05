from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter,OrderingFilter
from .serializers import CategoriaSerializer,MarcaSerializer,ProductoDetailSerializer,SaldoInventarioListSerializer,SaldoInventarioDetailSerializer,SaldoInventarioListSimpleSerializer
from inventario.models import Categoria,Marca,Producto,SaldoInventario,Marca,Promocion,ProductoReview
from django.db.models import Q
from api.pagination import PaginationSaldoInventario
from api.exceptions import CustomException
import operator
from functools import reduce
from django.conf import settings

from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from django.views.decorators.cache import cache_page
import json


SESSION_CACHE_TIEMOUT = getattr(settings,'SESSION_CACHE_TIEMOUT',7200)

class CategoriaListView(ListAPIView):
	#queryset = Categoria.objects.filter(estado = True)
	serializer_class = CategoriaSerializer
	#filter_backends = [SearchFilter]
	filter_backends = [OrderingFilter]
	# sarch_fields = ['']

	def get_queryset(self,*args,**kwargs):
		queryset_list = Categoria.objects.filter(estado = True).order_by('codigo')
		categoriaPadre = self.request.GET.get('idCategoriaPadre',None)
		if categoriaPadre:
			queryset_list = queryset_list.filter(categoriaPadre = categoriaPadre)
		return queryset_list

class MarcaListView(ListAPIView):
	queryset = Marca.objects.all()
	serializer_class = MarcaSerializer
	#filter_backends = [SearchFilter]
	filter_backends = [OrderingFilter]
	# sarch_fields = ['']


class CategoriaDetailView(RetrieveAPIView):
	queryset = Categoria.objects.all()
	serializer_class = CategoriaSerializer
	# fila a buscar
	lookup_field = 'pk'
	# nombre del parametro
	#lookup_url_kwarg = 'idCategoria'

class producto_detalle(RetrieveAPIView):
	queryset = SaldoInventario.objects.filter_products()
	serializer_class = SaldoInventarioDetailSerializer
	lookup_field = 'pk'
	lookup_url_kwarg = 'pk'

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(producto_detalle, self).dispatch(request,*args, **kwargs)


class producto_marca(ListAPIView):
	#queryset = SaldoInventario.objects.filter_products()
	serializer_class = SaldoInventarioListSerializer
	pagination_class = PaginationSaldoInventario
	def get_queryset(self, *args,**kwargs):
		marca = self.request.GET.get('idMarca',None)
		if not marca:
			raise CustomException(detail='Hace falta especificar la variable',field='idMarca')
		return SaldoInventario.objects.filter_products(producto__marca = marca)

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(producto_marca, self).dispatch(request,*args, **kwargs)

class producto_categoria(ListAPIView):
	#queryset = SaldoInventario.objects.filter_products()
	serializer_class = SaldoInventarioListSerializer
	pagination_class = PaginationSaldoInventario
	def get_queryset(self, *args,**kwargs):
		categoria = self.request.GET.get('categoria',None)
		marca = self.request.GET.get('marca',None)
		filter_Q = None
		if categoria:
			filter_Q = Q(producto__categoria__codigo = categoria) | Q(producto__categoria__categoriaPadre__codigo = categoria)
		else:
			raise CustomException('Hace falta especificar la variable','categoria')
		if marca:
			filter_Q &= Q(producto__marca__codigo = marca)

		order = self.request.GET.get('order','rel')
		if order == "desc":
			order = '-precioVentaUnitario'
		elif(order == 'asc'):
			order = 'precioVentaUnitario'
		elif order == 'rel':
			order = '-fechaCreacion'
		elif order == 'promo':
			order = 'precioOferta'

		return SaldoInventario.objects.filter_products(filter_Q).order_by('-estado',order)

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(producto_categoria, self).dispatch(request,*args, **kwargs)

class oferta(ListAPIView):
	serializer_class = SaldoInventarioListSerializer
	pagination_class = PaginationSaldoInventario

	def get_queryset(self, *args,**kwargs):
		categoria = self.request.GET.get('categoria',None)
		marca = self.request.GET.get('marca',None)

		listado_promociones = Promocion.objects.only('saldoInventario_id').filter(fechaFin__isnull=True,estado=True,saldoInventario__precioOferta__gt=0,saldoInventario__estado=True).order_by('-fechaInicio')
		filter_Q = Q(pk__in=list(p.saldoInventario_id for p in listado_promociones))
		if categoria:
			filter_Q = Q(producto__categoria__codigo = categoria) | Q(producto__categoria__categoriaPadre__codigo = categoria)
		if marca:
			filter_Q &= Q(producto__marca__codigo = marca)
		return SaldoInventario.objects.filter_products(filter_Q)

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(oferta, self).dispatch(request,*args, **kwargs)

class search_producto(ListAPIView):
	serializer_class = SaldoInventarioListSerializer
	pagination_class = PaginationSaldoInventario

	def get_queryset(self,*args,**kwargs):
		if not self.request.GET.get('filtro'):
			raise CustomException('Hace falta especificar la variable','filtro')
			
		filtro = self.request.GET.get('filtro').strip()
		list_filtro = filtro.replace('+',' ').split(' ')

		filter_Q = Q()
		listado_categorias = Categoria.objects.filter(reduce(operator.or_, (Q(descripcion__icontains=x) for x in list_filtro)))
		if listado_categorias:
			for categoria in listado_categorias:
				filter_Q |= Q(producto__categoria = categoria.pk) | Q(producto__categoria__categoriaPadre = categoria.pk)

		marca = Marca.objects.filter(Q(descripcion__in = list_filtro))
		if len(marca) > 0:
			filter_Q = filter_Q and Q(producto__marca = marca.first().pk)
		
		for filtro in list_filtro:
			filter_Q |= Q(producto__nombre__icontains = filtro) | Q(producto__referencia__icontains = filtro)
		#listado_saldo_inventario = get_list_or_404(SaldoInventario,filter_Q)
		marca_filtro = self.request.GET.get('marca',None)
		if marca_filtro:
			filter_Q &= Q(producto__marca__codigo = marca_filtro)
		order = self.request.GET.get('order','rel')
		if order == "desc":
			order = '-precioVentaUnitario'
		elif(order == 'asc'):
			order = 'precioVentaUnitario'
		elif order == 'rel':
			order = '-fechaCreacion'
		elif order == 'promo':
			order = 'precioOferta'
		return SaldoInventario.objects.filter_products(filter_Q).order_by('-estado',order)

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(search_producto, self).dispatch(request,*args, **kwargs)

# recibe por post un parametro data = [{"idSaldoInventario":130},{"idSaldoInventario":129}]
@api_view(['POST'])
def saldo_inventario_simple(request):
	if not request.POST.get("data",None):
		raise CustomException(detail='Hace falta especificar los datos')
	data = json.loads(request.POST.get("data",None))
	listado = (SaldoInventarioListSimpleSerializer(instance= p).data for p in  SaldoInventario.objects.filter(pk__in = list(d.get("idSaldoInventario") for d in data)))
	return Response(data=listado,status = 200)



class oferta_index(ListAPIView):
	#queryset = SaldoInventario.objects.filter_products()
	serializer_class = SaldoInventarioListSerializer
	pagination_class = PaginationSaldoInventario
	def get_queryset(self, *args,**kwargs):
		listado_promociones = Promocion.objects.filter_promocion(fechaFin__isnull=True,
																 estado=True,
																 saldoInventario__precioOferta__gt=0,
																 saldoInventario__estado=True).only('saldoInventario_id').order_by('-fechaInicio')[:10]
		return SaldoInventario.objects.filter_products(pk__in=list(p.saldoInventario_id for p in listado_promociones))

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(oferta_index, self).dispatch(request,*args, **kwargs)

class mas_vistos_index(ListAPIView):
	#queryset = SaldoInventario.objects.filter_products()
	serializer_class = SaldoInventarioListSerializer
	pagination_class = PaginationSaldoInventario
	def get_queryset(self, *args,**kwargs):
		top = 10
		review = ProductoReview.objects.all().order_by('-numeroVista')[:25].values_list('producto',flat=True)
		listado_idSaldoInventario = []
		for idProducto in review:
			if SaldoInventario.objects.filter_products(estado=True,producto=idProducto).exists():
				listado_idSaldoInventario.append(SaldoInventario.objects.filter_products(estado=True,producto=idProducto).only('pk').first().pk)
			if len(listado_idSaldoInventario) >= top:
				break
		print(listado_idSaldoInventario)
		return SaldoInventario.objects.filter_products(estado=True,pk__in = listado_idSaldoInventario)

	# Se cachea
	@method_decorator(cache_page(SESSION_CACHE_TIEMOUT))
	def dispatch(self,request, *args, **kwargs):
		return super(mas_vistos_index, self).dispatch(request,*args, **kwargs)
