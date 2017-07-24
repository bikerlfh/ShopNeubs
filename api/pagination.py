from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response

from inventario.models import SaldoInventario, Marca

NUM_ITEMS_DISPLAY_API = getattr(settings, "NUM_ITEMS_DISPLAY_API", 10)

THUMBNAIL_DEFAULT_STORAGE = getattr(settings, 'THUMBNAIL_DEFAULT_STORAGE', 'http://192.168.1.50:8000')


class CustomLimitOffsetPagination(LimitOffsetPagination):
	default_limit = NUM_ITEMS_DISPLAY_API
	max_limit = 10


class PaginationSaldoInventario(PageNumberPagination):
	page_size = NUM_ITEMS_DISPLAY_API

	# def paginate_queryset(self, queryset, request, view=None):
	# 	print(request.GET)
	# 	return Response()

	def get_paginated_response(self, data):
		print(self.request.GET)
		return Response({
			'next': self.get_next_link(),
			'previous': self.get_previous_link(),
			'count': self.page.paginator.count,
			'marcas': cargar_marcas_desde_listado_saldo_inventario(data),
			'results': data,
		})


"""
	Retorna un diccionario de las marcas que contiene el listado_saldo_inventario
"""


def cargar_marcas_desde_listado_saldo_inventario(listado_saldo_inventario):
	listado_marca = None
	if listado_saldo_inventario:
		listado_id_marca = list(sa.producto.marca_id for sa in SaldoInventario.objects.filter(
			pk__in=list(p['idSaldoInventario'] for p in listado_saldo_inventario)))
		listado_marca = Marca.objects.filter(idMarca__in=listado_id_marca).exclude(codigo='36').distinct().order_by(
			'descripcion').values('pk', 'codigo', 'descripcion')
	return listado_marca
