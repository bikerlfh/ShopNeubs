from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render,HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.decorators.cache import cache_page
from inventario.models  import Categoria,Marca,SaldoInventario,ProductoReview
from .models import Carousel

SESSION_CACHE_TIEMOUT = getattr(settings,'SESSION_CACHE_TIEMOUT',7200)

def index(request):
	request.session.clear_expired()
	if request.GET.get('activate-complete',None) != None and request.user.is_authenticated:
		messages.success(request, 'Tu cuenta ha sido activada')

	# Se consultan las categorias o se obtienen del cache
	if not cache.get('categorias'):
		categorias = Categoria.objects.filter(categoriaPadre = None).order_by('descripcion')
		cache.set('categorias',categorias,SESSION_CACHE_TIEMOUT)
	else:
		categorias = cache.get('categorias')
	listado_saldo_inventario = None
	carousel = None

	if not cache.get('carousel'):
		if Carousel.objects.filter(estado = True).exists():
			carousel = Carousel.objects.filter(estado = True).order_by('order')
			cache.set('carousel',carousel,SESSION_CACHE_TIEMOUT)
	else:
		carousel = cache.get('carousel')
	
	# Se consultan todas las marcas o se obtienen del cache
	if not cache.get('marcas'):
		marcas = Marca.objects.all().order_by('descripcion')
		cache.set('marcas',marcas,SESSION_CACHE_TIEMOUT)
	else:
		marcas = cache.get('marcas')
	
	return render(request,"base/index.html",{ 'listado_categoria' : categorias,'listado_marcas':marcas ,'carousel':carousel})

@cache_page(SESSION_CACHE_TIEMOUT)
def informacion_envio(request):
	print("INFORMACION")
	return render(request,"base/informacion-envio.html",{ })
@cache_page(SESSION_CACHE_TIEMOUT)
def terminos_condiciones(request):
	return render(request,"base/terminos-y-condiciones.html",{ })
@cache_page(SESSION_CACHE_TIEMOUT)
def como_comprar(request):
	return render(request,"base/como-comprar.html",{})
@cache_page(SESSION_CACHE_TIEMOUT)
def garantia(request):
	return render(request,"base/garantia.html",{})

class actualizar_cache(View):
	def get(self,request,*args,**kwargs):
		if not request.user.is_superuser:
			return HttpResponseRedirect(reverse("home"))
		return render(request,"base/actualizar_cache.html")
	def post(self,request,*args,**kwargs):
		if not request.user.is_superuser:
			return HttpResponseRedirect(reverse("home"))
		name_cache = request.POST.get('name-cache',None)
		if name_cache is None:
			return render(request,"base/actualizar_cache.html")
		else:
			if name_cache == "index_carousel":
				cache.delete("carousel")
				messages.success(request, 'Se ha eliminado el cache del Carousel')
			elif name_cache == "index_categorias":
				cache.delete("categorias")
				messages.success(request, 'Se ha eliminado el cache de categorias')
			elif name_cache == "index_marcas":
				cache.delete("marcas")
				messages.success(request, 'Se ha eliminado el cache de marcas')
			elif name_cache == "index_promocion":
				cache.delete("index_promocion")
				messages.success(request, 'Se ha eliminado el cache de index promociones')
			elif name_cache == "index_mas_vistos":
				cache.delete("index_mas_vistos")
				messages.success(request, 'Se ha eliminado el cache de index mas vistos')
			elif name_cache == "menu_categoria":
				cache.delete("menu_categorias")
				messages.success(request, 'Se ha eliminado el cache del menu categorias')
			elif name_cache == "TODO":
				cache.clear()
				messages.success(request, 'Se ha eliminado todo el cache')
		return HttpResponseRedirect(reverse("actualizar_cache"))


