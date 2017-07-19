from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render,HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.decorators.cache import cache_page
from inventario.models  import Categoria,Marca
from .models import Carousel,ApiSincronizacion,ArchivoModificacionPrecio
from tercero.models import Proveedor
from .forms import ArchivoModificarPrecioForm
from .update_prices import Pofo

SESSION_CACHE_TIEMOUT = getattr(settings,'SESSION_CACHE_TIEMOUT',7200)

def index(request):
	request.session.clear_expired()
	if request.GET.get('activate-complete',None) != None and request.user.is_authenticated:
		messages.success(request, 'Tu cuenta ha sido activada')

	# Se consultan las categorias o se obtienen del cache
	if not cache.get('categorias'):
		categorias = Categoria.objects.filter(categoriaPadre = None,estado=True).order_by('descripcion')
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
		marcas = Marca.objects.all().exclude(codigo = '36').order_by('descripcion')
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

def get_header(request):
	return render(request,"header.html")

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
			# Se crea un nuevo registro en ApiSincronizacion
			apiSincronizacion = ApiSincronizacion()
			apiSincronizacion.save()
			
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


class subir_archivo_actualizar_precios(View):
		def get(self,request,*args,**kwargs):
				if not request.user.is_superuser:
						return HttpResponseRedirect(reverse("home"))

				form = ArchivoModificarPrecioForm()

				listado_proveedor = Proveedor.objects.all()
				return render(request, "base/subir-archivo-actualizar-precio.html", context= {'form':form, 'listado_proveedor':listado_proveedor})

		def post(self,request,*args,**kwargs):
				if not request.user.is_superuser:
						return HttpResponseRedirect(reverse("home"))


				form = ArchivoModificarPrecioForm(data=request.POST,files=request.FILES)
				if form.is_valid():
						data = form.cleaned_data
						archivo = ArchivoModificacionPrecio(file=request.FILES['file'],proveedor=data['proveedor'])
						archivo.save()
						messages.success(request,"El archivo se ha guardado con exito")
						form = ArchivoModificarPrecioForm()
				listado_proveedor = Proveedor.objects.all()
				return render(request, "base/subir-archivo-actualizar-precio.html", context={'form':form, 'listado_proveedor': listado_proveedor})

class actualizar_precios(View):
		def get(self,request,*args,**kwargs):
				if not request.user.is_superuser:
						return HttpResponseRedirect(reverse("home"))

				listado_archivos = ArchivoModificacionPrecio.objects.all()

				if request.GET.get('file',None):
						archivo = ArchivoModificacionPrecio.objects.get(pk = request.GET.get('file',None))
						pofo = Pofo()
						pofo.analizar_actualizacion(archivo.file.path)
						return render(request, "base/actualizar-precio.html",
													context={'listado_archivos': listado_archivos,
																	 'file_selected':archivo.pk,
																	 'listado_pendiente_actualizar':pofo.listado_pendiente_actualizar,
																	 'listado_pendiente_crear': pofo.listado_pendiente_crear})


				return render(request, "base/actualizar-precio.html",
											context={'listado_archivos': listado_archivos})

		def post(self,request,*args,**kwargs):
				if not request.user.is_superuser:
						return HttpResponseRedirect(reverse("home"))

				if request.GET.get('file',None):
						archivo = ArchivoModificacionPrecio.objects.get(pk = request.GET.get('file',None))
						pofo = Pofo()
						pofo.analizar_actualizacion(archivo.file.path)
						if len(pofo.listado_pendiente_actualizar)>0:
							for sa_actualizar in pofo.listado_pendiente_actualizar:
									sa_actualizar.updateSaldoInventario()

						messages.success(request,"Se actualizaron los precios satisfactoriamente")
				else:
					messages.error(request,"Ocurrió un error al intentar actualizar precios")
				return HttpResponseRedirect(reverse("actualizar_precio"))


