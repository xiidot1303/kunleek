from rest_framework import viewsets, filters
from app.models import Shop
from app.serializers import ShopSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class ShopViewSet(viewsets.ModelViewSet):
	"""API endpoint for viewing and editing shops."""
	queryset = Shop.objects.filter(is_active=True)
	serializer_class = ShopSerializer
