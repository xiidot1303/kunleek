from rest_framework import viewsets
from app.models import Product, Category, FavoriteProduct
from app.serializers import ProductSerializer, CategorySerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Exists, OuterRef, BooleanField
from app.swagger_schemas import *
from bot.models import Bot_user


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_id>[^/.]+)')
    def by_category(self, request, category_id=None):
        """
        Get products by category ID.
        """
        user_id = request.query_params.get('user_id')
        favorites = FavoriteProduct.objects.filter(user__user_id=user_id, product=OuterRef('pk'))
        products = self.queryset.filter(category_id=category_id).annotate(
            is_favorite=Exists(favorites)
        )
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