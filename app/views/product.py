from rest_framework import viewsets
from app.models import Product, Category, FavoriteProduct, ProductByShop
from app.serializers import ProductSerializer, CategorySerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from app.swagger_schemas import *
from bot.models import Bot_user
from django.db.models import Min, Max, F, QuerySet
from app.services.product_service import filter_products_for_serializer, search_products_by_name
from rest_framework.pagination import PageNumberPagination


class ProductsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(active=True).select_related('category', 'discount_category')
    serializer_class = ProductSerializer
    pagination_class = ProductsPagination


    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        shop_id = self.request.query_params.get('shop_id')

        return filter_products_for_serializer(queryset, user_id, shop_id)

    def paginate_queryset(self, queryset):
        """
        Enable pagination ONLY when parameter `page` is provided
        """
        if self.request.query_params.get("page"):
            return super().paginate_queryset(queryset)

        return None 

    @swagger_auto_schema(
        method='get',
        manual_parameters=[product_by_name_param, shop_id_param, user_id_param, lang_param],
        responses={200: openapi.Response('Products found by name', ProductSerializer(many=True))}
    )
    @action(detail=False, methods=['get'], url_path='by-name')
    def by_name(self, request):
        """
        Get products by name.
        """
        name = request.query_params.get('name')
        lang = request.query_params.get('lang')
        if not name:
            return Response({"error": "Name parameter is required"}, status=400)
        name_field = f"name_normalized_{lang}"
        products = search_products_by_name(self.get_queryset(), name, name_field)[:50]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[
        shop_id_param, user_id_param, discount_category_id_param, product_by_name_param, lang_param
        ])
    @action(detail=False, methods=['get'], url_path='discounted')
    def discounted(self, request):
        """
        Get discounted products
        """
        category_id = request.query_params.get('category_id', None)
        name = request.query_params.get('name', None)
        lang = request.query_params.get('lang')
        
        products: QuerySet[Product] = self.get_queryset().filter(
            price__lt=F('price_without_discount')).order_by('category')
        if category_id:
            products = products.filter(discount_category_id=category_id)
        if name:
            name_field = f"name_normalized_{lang}"
            products = search_products_by_name(products, name, name_field)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        products = products.exclude(quantity = 0)[:30]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[shop_id_param, user_id_param])
    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_id>[^/.]+)')
    def by_category(self, request, category_id=None):
        """
        Get products by category ID.
        """
        products = self.get_queryset().filter(category_id=category_id)
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
        manual_parameters=[shop_id_param],
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
        min_price = self.get_queryset().aggregate(min_price=Min('price'))['min_price']
        max_price = self.get_queryset().aggregate(max_price=Max('price'))['max_price']

        return Response({
            "min_price": min_price,
            "max_price": max_price
        })
    
    @swagger_auto_schema(manual_parameters=[shop_id_param])
    @action(detail=False, methods=['get'], url_path='pack')
    def pack(self, request):
        """
        Get all products that are packs.
        """
        products = self.get_queryset().filter(is_pack=True).first()
        serializer = self.get_serializer(products)
        return Response(serializer.data)