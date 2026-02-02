class OrderStatus:
    CREATED = 'created'
    YANDEX_DELIVERING = 'yandex_delivering'
    DELIVERING = 'delivering'
    WAITING_DELIVERY_WORKING_HOURS = 'waiting_delivery_working_hours'
    DELIVERED = 'delivered'

class YandexTripStatus:
    READY_FOR_APPROVAL = 'performer_found'
    PERFORMER_FOUND = 'performer_found'
    PICKUP_ARRIVED = 'pickup_arrived'
    DELIVERY_ARRIVED = 'delivery_arrived'
    DELIVERED = 'delivered'