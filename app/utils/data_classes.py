class OrderStatus:
    CREATED = 'created'
    NEED_CONFIRMATION = 'need_confirmation'
    READY_TO_APPROVAL = 'ready_to_approval'
    YANDEX_DELIVERING = 'yandex_delivering'
    DELIVERING = 'delivering'
    WAITING_DELIVERY_WORKING_HOURS = 'waiting_delivery_working_hours'
    DELIVERED = 'delivered'
    ERROR_IN_BILLZ_API = 'error_in_billz_api'
    PAYMENT_RETURNED = 'payment_returned'
    PAYMENT_RETURN_ERROR = 'payment_return_error'
    RATED = 'rated'

    @staticmethod
    def is_error(status):
        return True if 'error' in status else False

class YandexTripStatus:
    READY_FOR_APPROVAL = 'ready_for_approval'
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
    ForTest = 'for_test'