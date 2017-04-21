from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from inventario.models  import Categoria,Marca,SaldoInventario,ProductoReview
from .models import Carousel

# Create your views here.
def index(request):
	request.session.clear_expired()
	time_cache = getattr(settings,'SESSION_COOKIE_AGE',7200)

	if request.GET.get('activate-complete',None) != None and request.user.is_authenticated:
		messages.success(request, 'Tu cuenta ha sido activada')

	# Se consultan las categorias o se obtienen del cache
	if not cache.get('categorias'):
		categorias = Categoria.objects.filter(categoriaPadre = None).order_by('descripcion')
		cache.set('categorias',categorias,time_cache)
	else:
		categorias= cache.get('categorias')
	listado_saldo_inventario = None
	carousel = None

	if not cache.get('carousel'):
		if Carousel.objects.filter(estado = True).exists():
			carousel = Carousel.objects.filter(estado = True).order_by('order')
			cache.set('carousel',carousel,1200)
	else:
		carousel = cache.get('carousel')
	
	# Se consultan todas las marcas o se obtienen del cache
	if not cache.get('marcas'):
		marcas = Marca.objects.all().order_by('descripcion')
		cache.set('marcas',marcas,time_cache)
	else:
		marcas = cache.get('marcas')
	
	return render(request,"base/index.html",{ 'listado_categoria' : categorias,'listado_marcas':marcas ,'carousel':carousel})

def politica_privacidad(request):
	return render(request,"base/politica-privacidad.html",{ })

def terminos_condiciones(request):
	return render(request,"base/terminos-y-condiciones.html",{ })

def como_comprar(request):
	return render(request,"base/como-comprar.html",{})