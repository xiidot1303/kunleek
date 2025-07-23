from rest_framework import viewsets
from app.models import DeliveryType
from app.serializers import DeliveryTypeSerializer


class DeliveryTypeViewSet(viewsets.ModelViewSet):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer