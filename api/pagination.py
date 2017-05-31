from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
from django.conf import settings

NUM_ITEMS_DISPLAY_API = getattr(settings,"NUM_ITEMS_DISPLAY_API",10)

class CustomLimitOffsetPagination(LimitOffsetPagination):
	default_limit = NUM_ITEMS_DISPLAY_API
	max_limit = 10

class CustomPageNumberPagination(PageNumberPagination):
	page_size = NUM_ITEMS_DISPLAY_API