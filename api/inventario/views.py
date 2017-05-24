from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter,OrderingFilter
from .serializers import CategoriaSerializer,ProductoDetailSerializer,SaldoInventarioListSerializer,SaldoInventarioDetailSerializer
from inventario.models import Categoria,Producto,SaldoInventario,Marca
from django.db.models import Q
from api.pagination import CustomPageNumberPagination
from api.exceptions import CustomException
import operator
from functools import reduce

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


class producto_marca(ListAPIView):
	#queryset = SaldoInventario.objects.filter_products()
	serializer_class = SaldoInventarioListSerializer
	pagination_class = CustomPageNumberPagination
	def get_queryset(self, *args,**kwargs):
		marca = self.request.GET.get('idMarca',None)
		if not marca:
			raise CustomException('Hace falta especificar la variable','idMarca',status_code = status.HTTP_400_BAD_REQUEST)
		return SaldoInventario.objects.filter_products(producto__marca = marca)

class producto_categoria(ListAPIView):
	#queryset = SaldoInventario.objects.filter_products()
	serializer_class = SaldoInventarioListSerializer
	pagination_class = CustomPageNumberPagination
	def get_queryset(self, *args,**kwargs):
		categoria = self.request.GET.get('idCategoria',None)
		marca = self.request.GET.get('idMarca',None)
		filter_Q = Q()
		if categoria:
			filter_Q = Q(producto__categoria = categoria) | Q(producto__categoria__categoriaPadre = categoria)
		if marca:
			filter_Q &= Q(producto__marca = marca)
		return SaldoInventario.objects.filter_products(filter_Q)

class search_producto(ListAPIView):
	serializer_class = SaldoInventarioListSerializer
	pagination_class = CustomPageNumberPagination

	def get_queryset(self,*args,**kwargs):
		if not self.request.GET.get('filtro'):
			raise CustomException('Hace falta especificar la variable','filtro',status_code = status.HTTP_400_BAD_REQUEST)
			
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

		order = self.request.GET.get('order','rel')
		if order == "desc":
			order = '-precioVentaUnitario'
		elif(order == 'asc'):
			order = 'precioVentaUnitario'
		elif order == 'rel':
			order = '-fechaCreacion'
		elif order == 'promo':
			order = 'precioOferta'
		return SaldoInventario.objects.filter_products(filter_Q).order_by(order)
