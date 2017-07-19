from django.contrib import admin
from django.db.models import Q
from .models import *
from .forms import SaldoInventarioForm
from base.admin import DefaultAdmin
from django.utils.translation import ugettext_lazy as _

# Clase para el filtro de productos por categoria
class ProductoCategoriaListFilter(admin.SimpleListFilter):
    title = _('Categoría')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'categoria'
    # el filtro son las categorias
    def lookups(self, request, model_admin):
    	# Debe ser una lista o una tupla.
    	# El primer elemento de la tupla es el pk de la categoria
    	# El segundo es la categoria a visualizar 
        return tuple((c.pk,'%s - %s (%s)' % (c.codigo, c.descripcion,(Producto.objects.filter(Q(categoria = c.pk)|Q(categoria__categoriaPadre=c.pk)).count()))) for c in Categoria.objects.all().order_by('codigo'))
    def queryset(self, request, queryset):
    	if self.value() is None:
        	return queryset.all()
		# se filtra por categoria y categoria padre
    	return queryset.filter(Q(categoria=self.value())|Q(categoria__categoriaPadre=self.value()))

# Clase para el filtro de categorias por CategoriaPadre
class CategoriaPadreListFilter(admin.SimpleListFilter):
    title = _('Categoría Padre')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'categoria_padre'
    # el filtro son las categorias
    def lookups(self, request, model_admin):
        return tuple((c.pk,'%s - %s (%s)' % (c.codigo, c.descripcion,(Categoria.objects.filter(categoriaPadre=c.pk).count()))) for c in Categoria.objects.filter(categoriaPadre = None).order_by('codigo'))
    def queryset(self, request, queryset):
        # se filtra por categoria padre
        if self.value() is None:
            return queryset.all()
        return queryset.filter(categoriaPadre = self.value())

class CategoriaAdmin(admin.ModelAdmin):
	fieldsets  = [
		('Categoría Padre',{'fields':['categoriaPadre']}),
		('Default', {'fields':['codigo','descripcion','estado']})
	]
	list_display = ['codigo','descripcion','categoriaPadre','estado']
	list_filter = [CategoriaPadreListFilter,'estado']
	search_fields = ['codigo','descripcion']
	ordering = ['codigo']
admin.site.register(Categoria,CategoriaAdmin)

admin.site.register(Marca,DefaultAdmin)

admin.site.register(Garantia,DefaultAdmin)


# Filtro de productos con o sin saldo inventario
class ProductoConSinSaldoInventarioListFilter(admin.SimpleListFilter):
    title = _('Registro en saldo inventario')
    parameter_name = 'producto_con_saldo'
    # el filtro son las categorias
    def lookups(self, request, model_admin):
        return ((0,'Sin registro'),(1,'Con registro'))
    def queryset(self, request, queryset):
        # se filtra por categoria padre
        if self.value() is None:
            return queryset.all()
        list_productos=SaldoInventario.objects.distinct('producto_id').values_list('producto_id',flat=True)
        if int(self.value()) == 1:
            return queryset.filter(pk__in = list_productos)
        else:
            return queryset.exclude(pk__in = list_productos)

class ProductoAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Parametros', {'fields':['categoria','marca']}),
	   ('Campos del Producto', {'fields':['nombre','referencia','descripcion','especificacion','urldescripcion']}),
    ]    
    list_display = ['numeroProducto','nombre','referencia','categoria']
    list_display_links = ['nombre']
    list_filter = [ProductoConSinSaldoInventarioListFilter,ProductoCategoriaListFilter,'marca']
    search_fields = ['numeroProducto','referencia','nombre','marca__descripcion']
admin.site.register(Producto,ProductoAdmin)

admin.site.register(Plataforma,DefaultAdmin)

class CategoriaSaldoInventarioListFilter(admin.SimpleListFilter):
    title = _('Categoría')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'categoria'
    # el filtro son las categorias
    def lookups(self, request, model_admin):
        return tuple((c.pk,'%s - %s (%s)' % (c.codigo, c.descripcion,(SaldoInventario.objects.filter(Q(producto__categoria = c.pk)|Q(producto__categoria__categoriaPadre = c.pk)).count()))) for c in Categoria.objects.all().order_by('codigo'))
    def queryset(self, request, queryset):
        # se filtra por categoria padre
        if self.value() is None:
            return queryset.all()
        return queryset.filter(Q(producto__categoria = self.value())|Q(producto__categoria__categoriaPadre = self.value()))

class SaldoInventarioAdmin(admin.ModelAdmin):
    form = SaldoInventarioForm
    fieldsets  = [
        ('Default',{'fields':['producto','proveedor','garantia','referenciaProveedor','cantidad','costoTotal',
                              'precioCompraUnitario','precioVentaUnitario','precioOferta','plataformas','estado']}),
    ]
    list_display = ['producto','proveedor','referenciaProveedor','cantidad','costoTotal','precioCompraUnitario','precioVentaUnitario','precioOferta','estado']
    search_fields = ['referenciaProveedor','producto__numeroProducto','producto__nombre','producto__referencia']
    list_filter = ['proveedor','estado',CategoriaSaldoInventarioListFilter,'producto__marca']
    ordering = ['-producto__numeroProducto','estado']
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = ordenar_field_for_foreignkey(db_field,kwargs)
        return super(SaldoInventarioAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        obj.usuarioCreacion = request.user
        super(SaldoInventarioAdmin, self).save_model(request, obj, form, change)

admin.site.register(SaldoInventario,SaldoInventarioAdmin)

class PromocionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('', {'fields':['saldoInventario','precioOferta','fechaInicio','fechaFin']}),
    ]
    readonly_fields = ('saldoInventario','precioOferta','fechaInicio','fechaFin',)
    list_display = ['saldoInventario','precioVenta','precioOferta','fechaInicio','fechaFin','estado']
    list_display_links = ['saldoInventario']
    list_filter = ['saldoInventario__proveedor','estado']
    search_fields = ['saldoInventario__producto__numeroProducto','saldoInventario__producto__nombre','saldoInventario__proveedor']
    ordering = ['fechaInicio','estado']
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = ordenar_field_for_foreignkey(db_field,kwargs)
        return super(PromocionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
admin.site.register(Promocion,PromocionAdmin)

class ProductoImagenAdmin(admin.ModelAdmin):
    fields = ['producto','imagen','order']
    #readonly_fields = ['order']
    list_display_links = ('producto',)
    list_display = ['producto','order','imagen']
    search_fields = ['producto__numeroProducto','order']
    ordering = ['-producto__numeroProducto','order']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = ordenar_field_for_foreignkey(db_field,kwargs)
        return super(ProductoImagenAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(ProductoImagen,ProductoImagenAdmin)

class PorcentajeGananciaAdmin(admin.ModelAdmin):
    fields = ['producto','categoria','porcentaje']
    list_display_links = ['porcentaje']
    list_display = fields
    search_fields = ['producto__numeroProducto','categoria__descripcion']
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = ordenar_field_for_foreignkey(db_field,kwargs)
        return super(PorcentajeGananciaAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(PorcentajeGanancia,PorcentajeGananciaAdmin)

class ProductoReviewAdmin(admin.ModelAdmin):
    fields = ['producto','numeroVista','numeroVenta']
    list_display_links = ['producto']
    list_display = fields
    search_fields = ['producto__numeroProducto']
    ordering = ['-producto__numeroProducto']
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = ordenar_field_for_foreignkey(db_field,kwargs)
        return super(ProductoReviewAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(ProductoReview,ProductoReviewAdmin)

def ordenar_field_for_foreignkey(db_field, kwargs):
    # Se ordena los productos por numeroProducto
    if db_field.name == "producto":
        kwargs["queryset"] = Producto.objects.all().order_by('numeroProducto')
    if db_field.name == "saldoInventario":
        kwargs["queryset"] = SaldoInventario.objects.all().order_by('producto__numeroProducto')
    return kwargs