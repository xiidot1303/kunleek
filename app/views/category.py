from rest_framework import viewsets
from app.models import Category
from app.serializers import CategorySerializer
from rest_framework.response import Response


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
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