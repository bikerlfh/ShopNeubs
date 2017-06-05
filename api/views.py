from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,AllowAny
from .serializers import ApiSincronizacionSerializer,ApiTablaSerializer
from base.models import ApiSincronizacion,ApiTabla
from django.db.models import Q


class APITabla(ListAPIView):
	serializer_class = ApiTablaSerializer

	def get_queryset(self,*args,**kwargs):
		queryset_list = ApiTabla.objects.all()
		return queryset_list

class APISincronizacion(ListAPIView):
	serializer_class = ApiSincronizacionSerializer

	def get_queryset(self,*args,**kwargs):
		filter_Q = Q(ultima = True)
		# Se valida la tabla
		if self.request.GET.get('tabla',None):
			filter_Q = filter_Q & Q(tabla_id = self.request.GET.get('tabla',None))
		return ApiSincronizacion.objects.filter(filter_Q).order_by('-fecha')