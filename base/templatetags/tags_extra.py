from datetime import datetime,timedelta
from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
from inventario.models import Categoria
from ventas.cart import Cart
import urllib
import re
from django.conf import settings


register = template.Library()

@register.filter(name='name_url_absolute')
def name_url_absolute(value):
    return value.split('/',1)[1]

"""
	Limpia la url de parametros GET
"""
@register.filter(name='filter_url_absolute')
def filter_url_absolute(value):
	return  '%s' % re.sub(r'/\?[\w=&+]+','/',value)
"""
Crea el breadcrumb apartir del full_path
parametros
- value*: full_path
- display_name_page: display del link de la pagina actual
"""
@register.simple_tag()
def get_breadcrumb(value,display_name_page = None):
	# se limpia la ruta de los parámetros
	value = filter_url_absolute(value)
	url_home = reverse('home')
	value = value.replace(url_home,'/')
	breadcrumb = "<ol class='breadcrumb'><li><a  href='%s'>Home</a></li>" % url_home
	val = value.split('/',1)[1].split('/')
	# Se limina la ultima posición
	val_deleted = val.pop()
	# Si la posición eliminada no estaba vacía, se vuelve a agregar
	if val_deleted != '':
		val.append(val_deleted)

	is_categoria = False
	# Si es una categoria, se deben mostrar sus padres
	if len(val) == 1:
		try:
			categoria = Categoria.objects.get(descripcion = urllib.parse.unquote(val[0]))
			if categoria.categoriaPadre is not None:
				val.insert(0,categoria.categoriaPadre.descripcion)
			is_categoria = True
		except Categoria.DoesNotExist:
			pass

	href = url_home
	for x in range(0,len(val)):
		if is_categoria:
			href = "%s%s" % (url_home,val[x])
		else:
			href += "%s/" % (val[x])
		clase = ""
		display_name = val[x]
		if (x) == (len(val)-1):
			clase = "class='active'"
			if display_name_page != None:
				display_name = display_name_page
		breadcrumb += ("<li><a %s href='%s'>%s</a></li>" % (clase,href,(urllib.parse.unquote(display_name))))
	breadcrumb +="</ol>"
	return mark_safe(breadcrumb)

@register.simple_tag()
def get_span_new_product(date,clase):
	span = ""
	fechaInicio = datetime.now() - timedelta(days=settings.DAYS_PRODUCT_NEW)
	fechaCreacion  =datetime.strptime(date, "%Y-%m-%d")
	
	if fechaCreacion >= fechaInicio and fechaCreacion <= datetime.now():
		span = "<span class='%s'></span>" % clase
	return mark_safe(span)

@register.simple_tag()
def get_porcentaje_oferta(saldoInventario):
	porcentaje = (100*(1-(saldoInventario.precioOferta/saldoInventario.precioVentaUnitario)))
	return ("%.1f" % porcentaje )
