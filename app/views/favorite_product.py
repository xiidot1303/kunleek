from rest_framework import viewsets, permissions
from app.models import FavoriteProduct, ProductByShop, Product
from app.serializers import FavoriteProductSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery
from app.swagger_schemas import *


class FavoriteProductViewSet(viewsets.ModelViewSet):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer

    @swagger_auto_schema(
        method='get',
        manual_parameters=[shop_id_param],
        responses={200: openapi.Response('User favorites', FavoriteProductSerializer(many=True))}
    )
    @action(detail=False, methods=['get'], url_path='user-favorites/(?P<user_id>[^/.]+)')
    def user_favorites(self, request, user_id=None):
        """
        Get all favorite products for a specific user.
        """
        shop_id = request.query_params.get('shop_id')
        shop_products = ProductByShop.objects.filter(
            product=OuterRef('product_id'),
            shop_id=shop_id
        )
        favorites = self.queryset.filter(user__user_id=user_id).select_related('product').annotate(
            product_price=Subquery(shop_products.values('price')[:1]),
            product_price_without_discount=Subquery(shop_products.values('price_without_discount')[:1]),
            product_quantity=Subquery(shop_products.values('quantity')[:1]),
        )
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)