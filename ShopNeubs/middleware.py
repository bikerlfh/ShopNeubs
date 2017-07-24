from django.conf import settings
from django.http import HttpResponsePermanentRedirect

"""
    LAS PETICIONES HTTP LAS DIRECCIONA A HTTPS
    SOLO EN PRODUCCIÓN Y SI HTTPS_SUPPORT ES TRUE
"""


class SecureRequiredMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response
		# self.paths = getattr(settings, 'SECURE_REQUIRED_PATHS',['/Board'])
		self.enabled = getattr(settings, 'HTTPS_SUPPORT', False)
		self.debug = getattr(settings, 'DEBUG')

	def __call__(self, request):
		if not self.debug and self.enabled and not request.is_secure():
			request_url = request.build_absolute_uri(request.get_full_path())
			secure_url = request_url.replace('http://', 'https://')
			return HttpResponsePermanentRedirect(secure_url)
		return self.get_response(request)

	# if not self.debug and self.enabled and not request.is_secure():
	#     request_url = request.build_absolute_uri(request.get_full_path())
	#     if request_url.startswith('http://'):
	#         for path in self.paths:
	#             if request.get_full_path().startswith(path):
	#                 secure_url = request_url.replace('http://', 'https://')
	#                 return HttpResponsePermanentRedirect(secure_url)
