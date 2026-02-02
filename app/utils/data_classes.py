class OrderStatus:
    CREATED = 'created'
    NEED_CONFIRMATION = 'need_confirmation'
    READY_TO_APPROVAL = 'ready_to_approval'
    YANDEX_DELIVERING = 'yandex_delivering'
    DELIVERING = 'delivering'
    WAITING_DELIVERY_WORKING_HOURS = 'waiting_delivery_working_hours'
    DELIVERED = 'delivered'
    ERROR_IN_BILLZ_API = 'error_in_billz_api'

    @staticmethod
    def is_error(status):
        return True if 'error' in status else False

class YandexTripStatus:
    READY_FOR_APPROVAL = 'performer_found'
    PERFORMER_FOUND = 'performer_found'
    PICKUP_ARRIVED = 'pickup_arrived'
    DELIVERY_ARRIVED = 'delivery_arrived'
    DELIVERED = 'delivered'


class PaymentMethod:
    CASH = 'cash'
    PAYME = 'payme'
    CLICK = 'click'


class DeliveryTypeTitle:
    ExpressYandex = 'express_yandex'
    DuringDay = 'during_day'