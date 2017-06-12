from rest_framework.generics import CreateAPIView,RetrieveAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer,UsuarioSerializer


User = get_user_model()

class register(CreateAPIView):
	serializer_class = UserCreateSerializer

class UsuarioDetailView(RetrieveAPIView):
	queryset = User.objects.all()
	serializer_class = UsuarioSerializer
	# fila a buscar
	lookup_field = 'pk'

class UsuarioDetailUsernameView(RetrieveAPIView):
	queryset = User.objects.all()
	serializer_class = UsuarioSerializer
	# fila a buscar
	lookup_field = 'username'







