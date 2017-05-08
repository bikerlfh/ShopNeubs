from django.conf import settings
from django_hosts import patterns, host
from django.contrib import admin

host_patterns = patterns('',
    host(r'www.shopneubs.com.co:8000', settings.ROOT_URLCONF, name='shopneubs'),
    #host(r'admin', 'ShopNeubs.hostsconf.urls', name='wildcard'),
    host(r'board', 'ShopNeubs.hostsconf.urls', name='wildcard'),
)