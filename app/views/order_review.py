# create api for order review using modelviewset
from rest_framework import viewsets, status
from rest_framework.response import Response
from app.models import OrderReview
from app.serializers import OrderReviewSerializer


class OrderReviewViewSet(viewsets.ModelViewSet):
    queryset = OrderReview.objects.all()
    serializer_class = OrderReviewSerializer
