from rest_framework import viewsets
from app.models import Product, Category, FavoriteProduct
from app.serializers import ProductSerializer, CategorySerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Exists, OuterRef, BooleanField
from app.swagger_schemas import *
from bot.models import Bot_user
from django.db.models import Min, Max, F


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer


    @swagger_auto_schema(
        method='get',
        manual_parameters=product_by_name,
        responses={200: openapi.Response('Products found by name', ProductSerializer(many=True))}
    )
    @action(detail=False, methods=['get'], url_path='by-name')
    def by_name(self, request):
        """
        Get products by name.
        """
        name = request.query_params.get('name')
        if not name:
            return Response({"error": "Name parameter is required"}, status=400)
        
        products = self.queryset.filter(name__icontains=name)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='discounted')
    def discounted(self, request):
        """
        Get discounted products
        """
        products = self.queryset.filter(price__lt=F('price_without_discount'))
        print(products.count())
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_id>[^/.]+)')
    def by_category(self, request, category_id=None):
        """
        Get products by category ID.
        """
        user_id = request.query_params.get('user_id')
        favorites = FavoriteProduct.objects.filter(user__user_id=user_id, product=OuterRef('pk'))
        products = self.queryset.filter(category_id=category_id).annotate(
            is_favorite=Exists(favorites)
        ).order_by('price')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(
        method='post',
        request_body=toogle_favorite_product,
        responses={200: openapi.Response('Product favorite status toggled')}
    )
    @action(detail=False, methods=['post'], url_path='toggle-favorite')
    def toggle_favorite(self, request):
        """
        Toggle favorite status of a product.
        """
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')

        if not user_id or not product_id:
            return Response({"error": "user_id and product_id are required"}, status=400)
        bot_user = Bot_user.objects.filter(user_id=user_id).first()
        product = Product.objects.filter(id=product_id).first()
        favorite, created = FavoriteProduct.objects.get_or_create(
            user=bot_user,
            product=product
        )

        if not created:
            favorite.delete()
            return Response({"message": "Product removed from favorites"})
        
        return Response({"message": "Product added to favorites"})

    @swagger_auto_schema(
        method='get',
        responses={200: openapi.Response('Minimum and maximum prices of products', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'min_price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Minimum price'),
                    'max_price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Maximum price'),
                }
            )
        )}
    )
    @action(detail=False, methods=['get'], url_path='min-max-prices')
    def min_max_prices(self, request):
        """
        Get minimum and maximum prices of products.
        """
        min_price = self.queryset.aggregate(min_price=Min('price'))['min_price']
        max_price = self.queryset.aggregate(max_price=Max('price'))['max_price']
        
        return Response({
            "min_price": min_price,
            "max_price": max_price
        })