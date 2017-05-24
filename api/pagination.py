from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
from django.conf import settings

class CustomLimitOffsetPagination(LimitOffsetPagination):
	default_limit = settings.NUM_ITEMS_DISPLAY
	max_limit = 10

class CustomPageNumberPagination(PageNumberPagination):
	page_size = settings.NUM_ITEMS_DISPLAY