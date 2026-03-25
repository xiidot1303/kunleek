from rest_framework import viewsets
from app.models import Category, DiscountCategory
from app.serializers import CategorySerializer, DiscountCategorySerializer
from rest_framework.response import Response
from app.swagger_schemas import *
from app.services.product_service import search_products_by_name, Product


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(active=True).select_related('parent_category')
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        """
        Override the list method to return categories with their subcategories.
        """
        # Load all categories in a single query and build an in-memory tree to avoid N+1 queries.
        all_cats = list(self.get_queryset().order_by('index'))

        # map parent_id -> [children]
        children_map = {}
        for c in all_cats:
            children_map.setdefault(c.parent_category_id, []).append(c)

        # attach prefetched children list to each instance for serializer to use
        for c in all_cats:
            # ensure safe default empty list when no children
            c.prefetched_subcategories = children_map.get(c.id, [])

        # top-level categories have parent_category_id == None
        top_level = children_map.get(None, [])

        serializer = self.get_serializer(top_level, many=True)
        return Response(serializer.data)


class DiscountCategoryViewSet(viewsets.ModelViewSet):
    queryset = DiscountCategory.objects.all().order_by('index')
    serializer_class = DiscountCategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        product_name = self.request.query_params.get('name', None)
        lang = self.request.query_params.get('lang')
        if product_name:
            products = Product.objects.filter(active=True)
            filtered_products = search_products_by_name(
                queryset=products,
                name=product_name,
                name_field=f"name_normalized_{lang}"
            )
            matching_products_ids = filtered_products.values_list('discount_category', flat=True)
            queryset = queryset.filter(id__in=matching_products_ids)
        return queryset

    @swagger_auto_schema(
        manual_parameters=[product_by_name_param, lang_param],
        responses={200: DiscountCategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs) 
