from app.services import *
from app.models import PromoCode


def get_valid_promo_code(code):
    try:
        promo_code = PromoCode.objects.get(code=code)
        if promo_code.is_valid():
            return promo_code
        return None
    except PromoCode.DoesNotExist:
        return None