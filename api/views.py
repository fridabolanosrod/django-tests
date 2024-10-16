import requests
from rest_framework import generics
from django.conf import settings
from .models import Product
from .serializers import ProductSerializer
from rest_framework.response import Response

class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        # Consumir la API de WooCommerce
        response = requests.get(
            settings.WOOCOMMERCE_API_URL, 
            auth=(settings.WOOCOMMERCE_API_KEY, settings.WOOCOMMERCE_API_SECRET)
        )
        
        # Mostrar el contenido de la respuesta en caso de error
        if response.status_code == 200:
            try:
                products_data = response.json()
            except ValueError:
                return Response({
                    "error": "No se pudo decodificar la respuesta JSON",
                    "response_content": response.text  # Mostrar el contenido de la respuesta
                }, status=500)

            # Crear o actualizar productos en la base de datos
            for product_data in products_data:
                product, created = Product.objects.update_or_create(
                    sku=product_data['sku'],
                    defaults={
                        'name': product_data['name'],
                        'price': product_data['regular_price']
                    }
                )
            return super().get(request, *args, **kwargs)
        else:
            return Response({
                "error": "Error al consumir la API de WooCommerce",
                "status_code": response.status_code,
                "content": response.text
            }, status=response.status_code)
