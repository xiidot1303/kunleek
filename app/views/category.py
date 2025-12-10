from rest_framework import viewsets
from app.models import Category
from app.serializers import CategorySerializer
from rest_framework.response import Response
from app.services.category_service import *


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        """
        Override the list method to return categories with their subcategories.
        """
        queryset = self.get_queryset().filter(id__in = list_categories_id_in_sell()).order_by('index')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)