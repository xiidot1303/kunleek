from celery import shared_task
from app.models import Order
from app.services import *
from config import YANDEX_DELIVERY_API_KEY, YANDEX_DELIVERY_URL, YANDEX_DELIVERY_CALLBACK_URL


@shared_task
def create_claim(order_id: int):
    order: Order = Order.objects.get(id=order_id)
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {YANDEX_DELIVERY_API_KEY}",
        "Content-Type": "application/json",
        "Accept-Language": "ru"
    }
    # Prepare data for Yandex Delivery API
    data = {
        "items": [
            {
                "cost_currency": "UZS",
                "cost_value": str(int(item.price)),
                "pickup_point": 1,
                "quantity": item.quantity,
                "title": item.product.name,
                "dropoff_point": 2
            } for item in order.items.all()
        ],
        "route_points": [
            {
                "address": {
                    "fullname": "3-й проезд Эшона Бобохонова, 41, Ташкент",
                    "coordinates": [69.191207, 41.342409]
                },
                "contact": {
                    "name": "Kunleek online store",
                    "phone": "+998900444777"
                },
                "point_id": 1,
                "type": "source",
                "visit_order": 1,
                "external_order_id": f"{order.id}"
            },
            {
                "address": {
                    "fullname": f"{order.address}",
                    "coordinates": [order.latitude, order.longitude]
                },
                "contact": {
                    "name": order.customer.first_name,
                    "phone": order.customer.phone
                },
                "point_id": 2,
                "type": "destination",
                "visit_order": 2,
                "external_order_id": f"{order.id}"
            }
        ],
        "callback_properties": {
            "callback_url": f"{YANDEX_DELIVERY_CALLBACK_URL}/yandex-delivery-callback"
        },
        "client_requirements": {
            "taxi_class": "express"

        }
    }

    # if order is not payed yet, set payment method on delivery
    if not order.payed:
        data["route_points"][0]["buyout"] = {
            "payment_method": "card"
        }
        data["route_points"][0]["payment_on_delivery"] = {
            "payment_method": "card"
        }
        data["route_points"][1]["payment_on_delivery"] = {
            "payment_method": "card"
        }
    response = requests.post(
        f"{YANDEX_DELIVERY_URL}/b2b/cargo/integration/v2/claims/create?request_id={order.id}",
        headers=headers,
        json=data
    )
    if claim_id := response.json().get("id"):
        # order.status = "yandex_claim_created"
        # order.save(update_fields=["status"])
        1
    else:
        # Handle error
        pass
