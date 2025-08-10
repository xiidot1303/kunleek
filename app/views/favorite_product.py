from rest_framework import viewsets, permissions
from app.models import FavoriteProduct
from app.serializers import FavoriteProductSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class FavoriteProductViewSet(viewsets.ModelViewSet):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer

    @action(detail=False, methods=['get'], url_path='user-favorites/(?P<user_id>[^/.]+)')
    def user_favorites(self, request, user_id=None):
        """
        Get all favorite products for a specific user.
        """
        favorites = self.queryset.filter(user__user_id=user_id)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)