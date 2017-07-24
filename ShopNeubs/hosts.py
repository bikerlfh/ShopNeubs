from django.conf import settings
from django_hosts import patterns, host

from api import urls as urls_api

host_patterns = patterns('',
	host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'api', urls_api, name='api'),
)