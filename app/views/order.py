from rest_framework import viewsets
from app.models import Order, OrderItem
from app.serializers import OrderSerializer, OrderItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    def get_queryset(self):
        """
        Optionally filter orders by bot user ID.
        """
        queryset = super().get_queryset()
        bot_user_id = self.request.query_params.get('user_id', None)
        if bot_user_id is not None:
            queryset = queryset.filter(bot_user__user_id=bot_user_id)
        return queryset


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
