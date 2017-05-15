"""ShopNeubs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.decorators import login_required,permission_required
from base import views as view_base
from tercero import views as views_tercero
from ventas import views as views_ventas
#from django_pdfkit import PDFView


urlpatterns = [
    url(r'^$', view_base.index, name = 'home'),
    url(r'^filer/', include('filer.urls')),
    
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.default.urls')),
    
    url(r'^informacion-envio/$', view_base.informacion_envio, name = 'informacion_envio'),
    url(r'^terminos-y-condiciones/$', view_base.terminos_condiciones, name = 'terminos_y_condiciones'),
    url(r'^como-comprar/$', view_base.como_comprar, name = 'como_comprar'),
    url(r'^garantia/$', view_base.garantia, name = 'garantia'),
    url(r'^actualizar-cache/$', login_required(view_base.actualizar_cache.as_view()), name = 'actualizar_cache'),
    
    # Cart
    url(r'^cart/$', views_ventas.cart, name = 'cart'),
    url(r'^cart/get/$', views_ventas.get_cantidad_cart, name = 'get_cantidad_cart'),
    
    url(r'^cart/add/(?P<idSaldoInventario>[\d]{1,10})/(?P<cantidad>-?\d{1,3})/$', views_ventas.add_cart, name='add_cart'),
    url(r'^cart/change/(?P<idSaldoInventario>[\d]{1,10})/(?P<cantidad>-?\d{1,3})/$', views_ventas.ajustar_cantidad_cart, name='change_cart'),
    url(r'^cart/remove/(?P<idSaldoInventario>[\d]{1,10})/$', views_ventas.remove_item, name='remove_item_cart'),
    #clientes
    url(r'^profile/$', views_tercero.profile.as_view(), name = 'profile'),
    url(r'^mis-pedidos/$', login_required(views_tercero.mis_pedidos),name = 'mis_pedidos'),
    # Compras
    url(r'^compras/', include('compras.urls')),
    # Division territorial
    url(r'^dt/', include('division_territorial.urls')),
    # Reportes
    url(r'^reportes/', include('reportes.urls')),
    # Tercero
    url(r'^tercero/', include('tercero.urls')),
    # Ventas
    url(r'^ventas/', include('ventas.urls')),
    
    url(r'^pedido-enviado/(?P<numeroPedido>[\d]{1,10})/$', views_ventas.pedido_enviado, name = 'pedido_enviado'),
    url(r'^pedido-no-generado/$', views_ventas.pedido_no_generado, name = 'pedido_no_generado'),
    
    # Inventario
    url(r'^', include('inventario.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)