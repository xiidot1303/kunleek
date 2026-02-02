from app.services.yandex_delivery_service import create_claim
from app.models import Order, OrderStatus

def create_claims_if_delivery_open():
    orders = Order.objects.filter(status=OrderStatus.WAITING_DELIVERY_WORKING_HOURS)
    for order in orders:
        if order.delivery_type.is_open():
            create_claim.delay(order.id)