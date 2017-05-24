from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from .serializers import UserCreateSerializer


class register(CreateAPIView):
	serializer_class = UserCreateSerializer





