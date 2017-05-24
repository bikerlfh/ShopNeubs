from django.conf import settings
from inventario.models import Categoria,Producto,SaldoInventario
from rest_framework.serializers import (ModelSerializer, HyperlinkedIdentityField,
										SerializerMethodField,ValidationError,CharField)

THUMBNAIL_DEFAULT_STORAGE = getattr(settings,'THUMBNAIL_DEFAULT_STORAGE','')

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
				list_imagenes.append({'order':i,'url': THUMBNAIL_DEFAULT_STORAGE + imagen.url})
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
			return THUMBNAIL_DEFAULT_STORAGE + imagen.url
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