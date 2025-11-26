from app.views import *
from rest_framework.views import APIView
from rest_framework.response import Response


class YandexDeliveryView(APIView):
    def post(self, request):
        # Handle Yandex Delivery callback here
        data = request.data
        # Process the callback data as needed
        return Response({"status": "callback received"}, status=200)