from django.conf import settings
from inventario.models import Categoria,Marca,Producto,SaldoInventario
from rest_framework.serializers import (ModelSerializer, HyperlinkedIdentityField,
										SerializerMethodField,ValidationError,CharField)

from easy_thumbnails.templatetags.thumbnail import thumbnail_url

THUMBNAIL_DEFAULT_STORAGE = getattr(settings,'THUMBNAIL_DEFAULT_STORAGE','http://192.168.1.50:8000')

class CategoriaSerializer(ModelSerializer):
	#padre = HyperlinkedIdentityField(view_name='categoria_detail',lookup_field='cp')
	class Meta:
		model = Categoria
		fields = [
			'pk',
			'codigo',
			'descripcion',
			'categoriaPadre',
		]

class MarcaSerializer(ModelSerializer):
	class Meta:
		model = Marca
		fields = [
			'pk',
			'codigo',
			'descripcion',
		]

class ProductoDetailSerializer(ModelSerializer):
	imagenes = SerializerMethodField()
	class Meta:
		model = Producto
		fields = [
			'idProducto',
			'categoria',
			'marca',
			'numeroProducto',
			'nombre',
			'descripcion',
			'especificacion',
			'urldescripcion',
			'imagenes',
		]
	# obtiene todas las imagenes en una lista
	def get_imagenes(self,obj):
		imagenes = obj.imagenes()
		list_imagenes = []
		if imagenes:
			for i,imagen in enumerate(imagenes):
				if getattr(settings,'DEBUG',False):			
					list_imagenes.append({'order':i,'url': THUMBNAIL_DEFAULT_STORAGE + thumbnail_url(imagen, 'producto_detalle')})
				else:
					list_imagenes.append({'order':i,'url': thumbnail_url(imagen, 'producto_detalle')})
			return list_imagenes
		return None	


class ProductoSimpleSerializer(ModelSerializer):
	#detail = HyperlinkedIdentityField(view_name='producto_detail',lookup_field='pk')
	imagen = SerializerMethodField()
	class Meta:
		model = Producto
		fields = [
			#'detail',
			#'pk',
			'numeroProducto',
			'nombre',
			'imagen'
		]
	# Se consulta la imagen principal del producto
	def get_imagen(self,obj):
		imagen = obj.imagen()
		if imagen:
			# se consulta la imagen thumbnail con el alias 'producto'
			if getattr(settings,'DEBUG',False):	
				return THUMBNAIL_DEFAULT_STORAGE + thumbnail_url(imagen, 'producto')
			else:
				return thumbnail_url(imagen, 'producto')
		return None


class SaldoInventarioDetailSerializer(ModelSerializer):
	producto = ProductoDetailSerializer()
	
	class Meta:
		model = SaldoInventario
		fields = [
			'idSaldoInventario',
			'producto',
			'precioVentaUnitario',
			'precioOferta',
			'estado',
		]


class SaldoInventarioListSerializer(ModelSerializer):
	producto = ProductoSimpleSerializer()
	
	#categoria = SerializerMethodField()
	class Meta:
		model = SaldoInventario
		fields = [
			'pk',
			'producto',
			'precioVentaUnitario',
			'precioOferta',
			'estado',
		]