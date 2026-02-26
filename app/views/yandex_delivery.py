from app.views import *
from rest_framework.views import APIView
from rest_framework.response import Response

from app.services.yandex_delivery_service import *
from app.services.newsletter_service import *
from app.models import *
from app.utils.data_classes import YandexTripStatus


class CallbackData(DictToClass):
    status: str
    claim_id: str


class YandexDeliveryView(APIView):
    def post(self, request):
        # Handle Yandex Delivery callback here
        data = request.data
        callback = CallbackData(data)
        yandex_trip: YandexTrip = YandexTrip.objects.filter(
                    claim_id=callback.claim_id).first()
        match callback.status:
            case YandexTripStatus.READY_FOR_APPROVAL:
                # accept order
                accept_order.delay(callback.claim_id)

            case YandexTripStatus.PERFORMER_FOUND:
                # get info
                info = order_info(callback.claim_id)
                performer_info = PerformerInfo(info["performer_info"])
                # set performer values
                for attr, value in performer_info.__dict__.items():
                    if not attr.startswith("__"):
                        setattr(yandex_trip, attr, value)
                yandex_trip.save()
                # send notification to client about performer
                send_performer_info_to_client(yandex_trip)

            case YandexTripStatus.PICKUP_ARRIVED:
                # courier arrived to point
                # send notification to admin group
                notify_admin_about_performer_arrived.delay(yandex_trip.id)

            case YandexTripStatus.DELIVERY_ARRIVED:
                # notify client about driver arrived
                notify_client_delivery_arrived.delay(yandex_trip.id)

            case YandexTripStatus.DELIVERED:
                # notify admin about order delivered
                notify_admin_order_delivered.delay(yandex_trip.id)
                send_gratitude_to_client.delay(yandex_trip.id)

        yandex_trip.status = callback.status
        yandex_trip.save(update_fields=["status"])

        # Process the callback data as needed
        return Response({"status": "callback received"}, status=200)


class CheckPrice(APIView):
    def get(self, request):
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")
        price = check_price(float(lat), float(lon))
        return Response(
            {"price": "19900"},
            status=200
        )